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
                            "brand": getattr(item, 'MakeName', 'Н/Д'),
                            "price": float(getattr(item, 'ResultPrice', 0)),
                            "days": int(getattr(item, 'ADDays', 999)),
                            "quantity": str(getattr(item, 'Quantity', '0')),
                            "logo": getattr(item, 'PriceLogo', '???'),
                            "name": getattr(item, 'DetailNameRus', 'Н/Д'),
                            "dlogo": getattr(item, 'DetailLogo', ''),
                            "ref": getattr(item, 'DetailRef', ''),
                            "plogo": getattr(item, 'PriceLogo', ''),
                            "delivery_percent": float(getattr(item, 'DDPercent', 0)),
                            "multiplicity": int(getattr(item, 'LotQuantity', 1))
                        })
        except Exception as e:
            print(f"Ошибка в модуле Emex: {e}")
        
        return results

    def add_to_basket(self, item, quantity=1, comment=""):
        """Добавление товара в корзину Emex через EmEx_Basket.asmx"""
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
                Ref=item.get("ref", ""),
                Name=item.get("name", ""),
                Comment=comment[:255],</iri_param>

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

            return {"success": True, "data": "товар добавлен в корзину"}</iri_param>

        except Exception as e:
            return {"success": False, "error": str(e)}