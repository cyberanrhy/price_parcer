import zeep
from zeep.transports import Transport
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class EmexProvider:
    def __init__(self, login, password):
        self.wsdl_url = "http://ws.emex.ru/EmExService.asmx?WSDL"
        self.basket_wsdl = "http://ws.emex.ru/EmEx_Basket.asmx?WSDL"
        self.login = login
        self.password = password

    def get_prices(self, article):
        results = []
        try:
            session = requests.Session()
            session.trust_env = False
            transport = Transport(session=session, timeout=15)
            client = zeep.Client(wsdl=self.wsdl_url, transport=transport)

            response = client.service.FindDetailAdv4(
                login=self.login,
                password=self.password,
                makeLogo="",
                detailNum=article,
                substLevel="OriginalOnly",
                substFilter="None",
                deliveryRegionType="PRI",
                maxOneDetailOffersCount=50,
                minQuantity=1
            )

            if response and hasattr(response, 'Details') and response.Details:
                clean_target = article.replace("-", "").upper()
                for item in response.Details.SoapDetailItem:
                    item_num = getattr(item, 'DetailNum', '').replace("-", "").upper()
                    if item_num == clean_target:
                        results.append({
                            "provider": "EMEX",
                            "article": article,
                            "brand": getattr(item, 'MakeName', 'Рќ/Р”'),
                            "price": float(getattr(item, 'ResultPrice', 0)),
                            "days": int(getattr(item, 'ADDays', 999)),
                            "quantity": str(getattr(item, 'Quantity', '0')),
                            "logo": getattr(item, 'PriceLogo', '???'),
                            "name": getattr(item, 'DetailNameRus', 'Рќ/Р”'),
                            "dlogo": getattr(item, 'DetailLogo', ''),
                            "ref": getattr(item, 'DetailRef', ''),
                            "plogo": getattr(item, 'PriceLogo', ''),
                            "delivery_percent": float(getattr(item, 'DDPercent', 0)),
                            "multiplicity": int(getattr(item, 'LotQuantity', 1))
                        })
        except Exception as e:
            print(f"РћС€РёР±РєР° РІ РјРѕРґСѓР»Рµ Emex: {e}")
        
        return results

    def add_to_basket(self, item, quantity=1, comment=""):
        """Р”РѕР±Р°РІР»РµРЅРёРµ С‚РѕРІР°СЂР° РІ РєРѕСЂР·РёРЅСѓ Emex С‡РµСЂРµР· EmEx_Basket.asmx"""
        try:
            session = requests.Session()
            session.trust_env = False
            transport = Transport(session=session, timeout=15)
            client = zeep.Client(wsdl=self.basket_wsdl, transport=transport)

            EPrice = client.get_type('{http://tempuri.org/}EPrice')
            ArrayOfEPrice = client.get_type('{http://tempuri.org/}ArrayOfEPrice')

            eprice = EPrice(
                Num="1",
                DLogo=item.get("dlogo", ""),
                MName=item.get("brand", ""),
                MLogo="",
                DNum=item.get("article", ""),
                Ref=comment[:255] if comment.strip() else item.get("ref", ""),
                Name=item.get("name", ""),
                Com="",

                Quan=str(quantity),
                Price=str(item.get("price", "0")),
                PLogo=item.get("plogo", ""),
                Notc="",
                Error="",
                DeliveryRegionType="PRI"
            )

            result = client.service.InsertToBasket3(
                login=self.login,
                password=self.password,
                ePrices=ArrayOfEPrice([eprice])
            )

            if result and len(result) > 0:
                resp = result[0]
                error_code = getattr(resp, 'ErrorMessageCode', -1)
                if error_code != 0:
                    err_msg = getattr(resp, 'Comment', 'ошибка ' + str(error_code))
                    return {"success": False, "error": err_msg}
                global_id = getattr(resp, 'GlobalId', '')
                return {"success": True, "data": "С‚РѕРІР°СЂ РґРѕР±Р°РІР»РµРЅ РІ РєРѕСЂР·РёРЅСѓ, GlobalId=" + str(global_id)}
            return {"success": True, "data": "С‚РѕРІР°СЂ РґРѕР±Р°РІР»РµРЅ РІ РєРѕСЂР·РёРЅСѓ"}

        except Exception as e:
            return {"success": False, "error": str(e)}
