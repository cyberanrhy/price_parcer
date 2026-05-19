import requests
import base64
import re

class AvtosoyuzProvider:
    def __init__(self, login, password):
        self.login = login
        self.password = password
        self.base_url = "https://api.xn--80aep1aarf3h.xn--p1ai"
        credentials = base64.b64encode(f"{login}:{password}".encode()).decode()
        self.headers = {
            "Authorization": f"Basic {credentials}",
            "Accept": "application/json",
            "Content-type": "application/json"
        }

    def get_prices(self, article):
        results = []
        try:
            # Шаг 1: получить бренды по артикулу
            brands = self._get_brands(article)
            if not brands:
                return results

            # Шаг 2: для каждого бренда запросить цены
            for brand_item in brands:
                brand_name = brand_item.get("Brand", "")
                if not brand_name:
                    continue
                parts = self._get_parts(article, brand_name)
                if parts:
                    results.extend(parts)

        except Exception as e:
            print(f"Ошибка в модуле Avtosoyuz: {e}")

        return results

    def _get_brands(self, article):
        url = f"{self.base_url}/SearchService/GetBrands"
        params = {"article": article, "withoutTransit": "false"}
        session = requests.Session()
        session.trust_env = False
        resp = session.get(url, params=params, headers=self.headers, timeout=15, proxies={"http": None, "https": None})
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, list):
                return data
        return []

    def _get_parts(self, article, brand):
        url = f"{self.base_url}/SearchService/GetParts"
        params = {"article": article, "brand": brand, "withoutTransit": "false"}
        session = requests.Session()
        session.trust_env = False
        resp = session.get(url, params=params, headers=self.headers, timeout=15, proxies={"http": None, "https": None})
        if resp.status_code != 200:
            return []

        data = resp.json()
        if not isinstance(data, list):
            return []

        results = []
        for item in data:
            raw_days = item.get("SupplierTimeMin", 0)
            days_val = 0
            if raw_days:
                try:
                    days_val = max(1, round(int(raw_days) / 24))
                except:
                    days_val = 1

            mult = item.get("MinCount", None)
            if mult is None:
                mult = 1

            results.append({
                "provider": "Автосоюз",
                "article": item.get("Article", article),
                "brand": item.get("Brand", brand),
                "price": float(item.get("CostSale", 0)),
                "days": days_val,
                "quantity": str(item.get("Count", "0")),
                "logo": item.get("SupplierName", "-"),
                "name": item.get("Description", "No name"),
                "delivery_percent": float(item.get("SupplierPercent", 0)),
                "multiplicity": int(mult),
                "is_original": item.get("IsOriginal", False),
                "is_analog": item.get("IsAnalog", False),
                "supplier_time_min": item.get("SupplierTimeMin", 0),
                "supplier_time_max": item.get("SupplierTimeMax", 0)
            })
        return results

    def add_to_basket(self, item, quantity=1, comment=""):
        try:
            url = f"{self.base_url}/SearchService/AddToBasket"
            params = {
                "article": item.get("article", ""),
                "brand": item.get("brand", ""),
                "supplierName": item.get("logo", ""),
                "costSale": item.get("price", 0),
                "quantity": quantity,
                "supplierTimeMin": item.get("supplier_time_min", 0),
                "supplierTimeMax": item.get("supplier_time_max", 0),
                "comment": comment
            }
            session = requests.Session()
            session.trust_env = False
            resp = session.get(url, params=params, headers=self.headers, timeout=15, proxies={"http": None, "https": None})
            text = resp.text.strip().strip('"')
            if resp.status_code == 200 and text == "Ok":
                return {"success": True, "data": text}
            else:
                return {"success": False, "error": text}
        except Exception as e:
            return {"success": False, "error": str(e)}
