import requests
import json

class ForumAutoProvider:
    def __init__(self, login, password):
        self.login = login
        self.password = password
        self.base_url = "https://api.forum-auto.ru/v2"

    def _get(self, method, params):
        full_params = {"login": self.login, "pass": self.password, **params}
        session = requests.Session()
        session.trust_env = False
        resp = session.get(f"{self.base_url}/{method}", params=full_params,
                           timeout=15, proxies={"http": None, "https": None})
        if resp.status_code != 200:
            return None
        return resp.json()

    def get_prices(self, article):
        data = self._get("listGoods", {"art": article, "cross": 0})
        if not data or not isinstance(data, list):
            return []
        results = []
        for item in data:
            raw_days = item.get("d_deliv", 0)
            results.append({
                "provider": "Forum-Auto",
                "brand": item.get("brand", ""),
                "article": item.get("art", ""),
                "price": float(item.get("price", 0)),
                "days": int(raw_days) if raw_days else 0,
                "quantity": str(item.get("num", 0)),
                "logo": item.get("whse", "-"),
                "name": item.get("name", "No name"),
                "gid": str(item.get("gid", "")),
                "multiplicity": int(item.get("kr", 1))
            })
        return results

    def add_to_basket(self, item, quantity=1, comment=""):
        try:
            data = self._get("addGoodsToOrder", {
                "tid": item.get("gid", ""),
                "num": quantity
            })
            if data is None:
                return {"success": False, "error": "HTTP error"}
            if isinstance(data, dict) and "error" in data:
                return {"success": False, "error": str(data)}
            return {"success": True, "data": data}
        except Exception as e:
            return {"success": False, "error": str(e)}
