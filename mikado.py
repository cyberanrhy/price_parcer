import requests
import xml.etree.ElementTree as ET

NS = {"ns": "http://mikado-parts.ru/service"}
NS_BASKET = {"ns": "http://mikado-parts.ru/ws1/"}

class MikadoProvider:
    def __init__(self, client_id, password):
        self.client_id = client_id
        self.password = password
        self.service_url = "http://www.mikado-parts.ru/ws1/service.asmx"
        self.basket_url = "http://www.mikado-parts.ru/ws1/basket.asmx"

    def _post(self, url, action, params):
        session = requests.Session()
        session.trust_env = False
        resp = session.post(f"{url}/{action}", data=params,
                            timeout=15, proxies={"http": None, "https": None})
        if resp.status_code != 200:
            return None
        return ET.fromstring(resp.content)

    def get_prices(self, article):
        root = self._post(self.service_url, "Code_Search", {
            "Search_Code": article,
            "ClientID": self.client_id,
            "Password": self.password,
            "FromStockOnly": "FromStockAndByOrder",
        })
        if root is None:
            return []
        return self._parse_search(root)

    def _parse_search(self, root):
        results = []
        list_el = root.find(".//ns:List", NS)
        if list_el is None:
            return results
        for row in list_el.findall("ns:Code_List_Row", NS):
            zakaz = _txt(row.find("ns:ZakazCode", NS))
            brand = _txt(row.find("ns:Brand", NS)) or _txt(row.find("ns:ProducerBrand", NS))
            producer_code = _txt(row.find("ns:ProducerCode", NS))
            article_val = producer_code or ""
            name = _txt(row.find("ns:Name", NS))
            price = _float(row.find("ns:PriceRUR", NS))
            code_type = _txt(row.find("ns:CodeType", NS))
            min_qty_str = _txt(row.find("ns:MinZakazQTY", NS)) or "1"
            srock = _txt(row.find("ns:Srock", NS))
            days = _int(srock) if srock and srock != "?" else 0
            stocks_el = row.find("ns:OnStocks", NS)
            total_qty = 0
            warehouses = []
            if stocks_el is not None:
                for sl in stocks_el.findall("ns:StockLine", NS):
                    qty_str = _txt(sl.find("ns:StockQTY", NS)) or "0"
                    total_qty += _parse_qty(qty_str)
                    wh = _txt(sl.find("ns:StokName", NS)) or "-"
                    warehouses.append(wh)
            results.append({
                "provider": "Mikado",
                "brand": brand,
                "article": article_val,
                "price": price,
                "days": days,
                "quantity": str(total_qty) if total_qty else "0",
                "logo": ", ".join(warehouses) if warehouses else "-",
                "name": name,
                "zakaz_code": zakaz,
                "multiplicity": _int(min_qty_str) if min_qty_str.isdigit() else 1,
                "code_type": code_type,
            })
        return results

    def add_to_basket(self, item, quantity=1, comment=""):
        zakaz_code = item.get("zakaz_code", "")
        if not zakaz_code:
            return {"success": False, "error": "Нет zakaz_code"}
        root = self._post(self.basket_url, "Basket_Add", {
            "ZakazCode": zakaz_code,
            "QTY": str(quantity),
            "DeliveryType": "0",
            "Notes": comment,
            "ClientID": self.client_id,
            "Password": self.password,
            "ExpressID": "0",
            "StockID": "1",
        })
        if root is None:
            return {"success": False, "error": "HTTP error"}
        msg = _txt(root.find(".//ns:Message", NS_BASKET))
        if msg == "OK":
            id_el = root.find(".//ns:ID", NS_BASKET)
            return {"success": True, "data": {"id": _txt(id_el) if id_el is not None else ""}}
        return {"success": False, "error": msg or "Unknown error"}


def _txt(el):
    return el.text.strip() if el is not None and el.text else ""

def _float(el):
    if el is not None and el.text:
        try:
            return float(el.text)
        except:
            return 0.0
    return 0.0

def _int(s):
    try:
        return int(s)
    except:
        return 0

def _parse_qty(qty_str):
    qty_str = qty_str.strip()
    if qty_str.endswith("+"):
        try:
            return int(qty_str.rstrip("+")) * 2
        except:
            return 10
    try:
        return int(qty_str)
    except:
        return 0
