import hashlib
import requests
import re


class AbstdProvider:
    def __init__(self, login, password, agreement_id, cart_id="0"):
        self.login = login
        self.password = password
        self.agreement_id = agreement_id
        self.cart_id = cart_id
        self.base_url = "https://abstd.ru"
        self._auth_hash = None

    def _calc_auth(self):
        if self._auth_hash:
            return self._auth_hash
        pwd_hash = hashlib.md5(self.password.encode()).hexdigest().lower()
        self._auth_hash = hashlib.md5((self.login + pwd_hash).encode()).hexdigest().lower()
        return self._auth_hash

    def _get(self, endpoint, params=None):
        if params is None:
            params = {}
        params["auth"] = self._calc_auth()
        session = requests.Session()
        session.trust_env = False
        try:
            resp = session.get(
                f"{self.base_url}/{endpoint}",
                params=params,
                timeout=15,
                proxies={"http": None, "https": None}
            )
            if resp.status_code != 200:
                return None
            return resp.json()
        except:
            return None

    def get_prices(self, article, brand=None):
        params = {
            "article": article,
            "agreement_id": self.agreement_id,
            "show_unavailable": "1",
            "format": "json"
        }
        if brand:
            params["brand"] = brand

        data = self._get("api-search", params)
        if not data or data.get("status") != "OK":
            return []

        items = data.get("data", [])
        results = []
        for item in items:
            delivery_str = item.get("delivery_duration", "0")
            if delivery_str and isinstance(delivery_str, str) and "-" in delivery_str:
                parts = delivery_str.split("-")
                try:
                    days = int(parts[1].strip())
                except:
                    days = int(parts[0].strip())
            else:
                try:
                    days = int(delivery_str)
                except:
                    days = 0

            fail_percent = item.get("fail_percent")
            if fail_percent is not None:
                try:
                    delivery_percent = 100 - int(fail_percent)
                except:
                    delivery_percent = ""
            else:
                delivery_percent = ""

            qty_str = item.get("quantity", "0")
            by_request = item.get("by_request", "0")
            if by_request == "1" and (qty_str == "0" or not qty_str):
                qty_str = "под заказ"

            results.append({
                "provider": "ABSTD",
                "brand": item.get("brand", ""),
                "article": item.get("article", ""),
                "price": float(item.get("price", 0)),
                "days": days,
                "quantity": qty_str,
                "name": item.get("product_name", ""),
                "multiplicity": int(item.get("mult_sale", 1)),
                "delivery_percent": delivery_percent,
                "warehouse": item.get("warehouse_name", ""),
                "product_id": item.get("product_id", ""),
                "nomenclature_id": item.get("nomenclature_id", ""),
                "warehouse_id": item.get("warehouse_id", ""),
                "is_cross": item.get("is_cross", 0)
            })
        return results

    def get_brands(self, article):
        data = self._get("api-brands", {"article": article, "format": "json"})
        if data and isinstance(data, list):
            return data
        return []

    def add_to_basket(self, item, quantity=1, comment=""):
        product_id = item.get("product_id", "")
        if not product_id:
            return {"success": False, "error": "Нет product_id"}

        params = {
            "agreement_id": self.agreement_id,
            "cart_id": self.cart_id,
            "format": "json"
        }
        params[f"prod[{product_id}]"] = str(quantity)
        if comment:
            params[f"desc[{product_id}]"] = comment

        data = self._get("api-cart_add", params)
        if data and data.get("status") == "OK":
            return {"success": True, "data": data}
        err = ""
        if data and "result" in data:
            for r in data["result"]:
                if r.get("status") == "error":
                    err = r.get("status_msg", "")
        return {"success": False, "error": err or "Ошибка добавления в корзину"}
