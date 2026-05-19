import requests
import re
import json
from concurrent.futures import ThreadPoolExecutor, TimeoutError


def _decode_response(resp):
    raw = resp.content
    for enc in ('utf-8', 'windows-1251', 'cp1251', 'koi8-r'):
        try:
            return raw.decode(enc)
        except:
            continue
    return raw.decode('utf-8', errors='replace')


class PrLgProvider:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.pr-lg.ru/search/items"
        self.cart_url = "https://api.pr-lg.ru/cart/add"
        self._session = None

    @property
    def session(self):
        if self._session is None:
            self._session = requests.Session()
            self._session.trust_env = False
        return self._session

    def get_prices(self, article):
        params = {
            "secret": self.api_key,
            "article": article
        }
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            resp = self.session.get(self.base_url, params=params, headers=headers,
                                    timeout=25, proxies={"http": None, "https": None})
            if resp.status_code != 200:
                return []
            data = json.loads(_decode_response(resp))
            results = []
            if isinstance(data, list):
                for brand_group in data:
                    brand_name = brand_group.get("brand", "Unknown")
                    products_raw = brand_group.get("products", {})
                    if isinstance(products_raw, dict):
                        items_iter = products_raw.values()
                    elif isinstance(products_raw, list):
                        items_iter = products_raw
                    else:
                        continue
                    for item in items_iter:
                        raw_days = str(item.get("show_date", "0"))
                        days_val = re.sub(r'\D', '', raw_days)
                        results.append({
                            "provider": "Profit-League",
                            "brand": brand_name,
                            "article": item.get("article", ""),
                            "price": float(item.get("price", 0)),
                            "days": int(days_val) if days_val else 0,
                            "quantity": str(item.get("quantity", "0")),
                            "logo": item.get("custom_warehouse_name", "-"),
                            "name": item.get("description", "No name"),
                            "article_id": str(item.get("article_id", "")),
                            "warehouse_id": str(item.get("warehouse_id", "")),
                            "code": item.get("product_code", ""),
                            "multiplicity": int(item.get("multi", 1))
                        })
            return results
        except Exception as e:
            print(f"Ошибка внутри PrLgProvider: {e}")
            return []

    def add_to_basket(self, item, quantity=1, comment=""):
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            params = {
                "secret": self.api_key,
                "id": item.get("article_id", ""),
                "warehouse": item.get("warehouse_id", ""),
                "quantity": quantity,
                "code": item.get("code", ""),
                "comment": comment
            }
            resp = self.session.post(self.cart_url, data=params, headers=headers,
                                     timeout=25, proxies={"http": None, "https": None})
            if resp.status_code == 200:
                data = json.loads(_decode_response(resp))
                if isinstance(data, dict) and data.get("status") == "error":
                    return {"success": False, "error": f"API error: {data}"}
                return {"success": True, "data": data}
            else:
                return {"success": False, "error": f"HTTP {resp.status_code}: {resp.text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_prices_parallel(self, raw_article, clean_article):
        executor = ThreadPoolExecutor(max_workers=2)
        try:
            raw_future = executor.submit(self.get_prices, raw_article)
            clean_future = executor.submit(self.get_prices, clean_article)

            try:
                raw_result = raw_future.result(timeout=20)
                if raw_result:
                    executor.shutdown(wait=False, cancel_futures=True)
                    return raw_result
            except TimeoutError:
                pass
            except:
                pass

            try:
                clean_result = clean_future.result(timeout=20)
                return clean_result or []
            except:
                return []
        finally:
            executor.shutdown(wait=False)
