import requests
import base64
import re
import datetime


class ArmtekProvider:
    def __init__(self, login, password, vkorg, kunnr):
        self.login = login
        self.password = password
        self.vkorg = vkorg
        self.kunnr = kunnr
        self.base_url = "https://ws.armtek.ru/api"
        creds = base64.b64encode(f"{login}:{password}".encode()).decode()
        self.headers = {
            "Authorization": f"Basic {creds}",
            "Accept": "application/json",
        }

    def _parse_date_days(self, date_str):
        if not date_str or len(date_str) < 8:
            return 0
        try:
            dt = datetime.datetime.strptime(date_str[:14], "%Y%m%d%H%M%S")
            delta = dt - datetime.datetime.now()
            return max(1, round(delta.total_seconds() / 86400))
        except:
            try:
                dt = datetime.datetime.strptime(date_str[:8], "%Y%m%d")
                delta = dt - datetime.datetime.now()
                return max(1, round(delta.total_seconds() / 86400))
            except:
                return 0

    def get_prices(self, article, brand=""):
        results = []
        try:
            params = {
                "VKORG": self.vkorg,
                "KUNNR_RG": self.kunnr,
                "PIN": article,
                "QUERY_TYPE": "2",
                "format": "json",
            }
            if brand:
                params["BRAND"] = brand

            session = requests.Session()
            session.trust_env = False
            resp = session.post(
                f"{self.base_url}/ws_search/search",
                data=params,
                headers=self.headers,
                timeout=15,
                proxies={"http": None, "https": None},
            )
            if resp.status_code != 200:
                return results

            data = resp.json()
            if not isinstance(data, dict):
                return results

            resp_data = data.get("RESP", {})
            items = resp_data.get("ARRAY", [])
            if not isinstance(items, list):
                return results

            for item in items:
                price_raw = item.get("PRICE", "0")
                try:
                    price = float(price_raw)
                except:
                    price = 0.0

                if price <= 0:
                    continue

                raw_qty = item.get("RVALUE", "0")
                try:
                    qty = int(float(raw_qty))
                except:
                    qty = 0

                mult_raw = item.get("RDPRF", "1")
                try:
                    mult = int(float(mult_raw))
                except:
                    mult = 1

                dp_raw = item.get("VENSL", "")
                try:
                    dp = float(dp_raw) if dp_raw else 0
                except:
                    dp = 0

                days = self._parse_date_days(item.get("DLVDT", ""))

                results.append({
                    "provider": "Armtek",
                    "article": item.get("PIN", article),
                    "brand": item.get("BRAND", brand),
                    "price": price,
                    "days": days,
                    "quantity": str(qty),
                    "logo": item.get("KEYZAK", "-"),
                    "name": item.get("NAME", "No name"),
                    "delivery_percent": dp,
                    "multiplicity": mult,
                    "is_original": item.get("ANALOG", "") == "",
                    "is_analog": item.get("ANALOG", "") != "",
                    "keyzak": item.get("KEYZAK", ""),
                    "artid": item.get("ARTID", ""),
                })

        except Exception as e:
            print(f"Ошибка Armtek: {e}")

        return results

    def add_to_basket(self, item, quantity=1, comment=""):
        try:
            payload = {
                "VKORG": self.vkorg,
                "KUNRG": self.kunnr,
                "format": "json",
                "ITEMS[0][PIN]": item.get("article", ""),
                "ITEMS[0][BRAND]": item.get("brand", ""),
                "ITEMS[0][KWMENG]": str(quantity),
                "ITEMS[0][KEYZAK]": item.get("keyzak", ""),
            }
            if comment:
                payload["TEXT_ORD"] = comment

            session = requests.Session()
            session.trust_env = False
            resp = session.post(
                f"{self.base_url}/ws_order/createOrder",
                data=payload,
                headers=self.headers,
                timeout=15,
                proxies={"http": None, "https": None},
            )
            text = resp.text.strip()
            if resp.status_code == 200:
                try:
                    json_data = resp.json()
                    status_code = json_data.get("STATUS", 0)
                    if status_code == 200:
                        return {"success": True, "data": text[:200]}
                    else:
                        msgs = json_data.get("MESSAGES", [])
                        err_text = msgs[0].get("TEXT", text[:200]) if msgs else text[:200]
                        return {"success": False, "error": err_text}
                except:
                    return {"success": True, "data": text[:200]}
            else:
                return {"success": False, "error": f"HTTP {resp.status_code}: {text[:200]}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
