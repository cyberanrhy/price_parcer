# Emex API — Web-сервисы

## Общая информация

Emex предоставляет SOAP Web-сервисы для интеграции. Доступ предоставляется зарегистрированным клиентам с конкретных IP-адресов.

**Основная документация:** http://wsdoc.emex.ru/
**WSDL (главный сервис):** http://ws.emex.ru/EmExService.asmx?WSDL

## Подключение

1. Зарегистрироваться на emex.ru
2. Отправить заявку на подключение к веб-сервисам через раздел https://emex.ru/ws
3. Указать IP-адрес, с которого будут идти запросы
4. Получить логин и пароль

## Используемые методы

### FindDetailAdv4 — поиск деталей и цен

```
FindDetailAdv4(
  login: string,
  password: string,
  makeLogo: string,
  detailNum: string,
  substLevel: string,
  substFilter: string,
  deliveryRegionType: string,
  maxOneDetailOffersCount: int,
  minQuantity: int
)
```

Параметры входа:
- `login` — числовой логин (для EmexProvider: `717828`)
- `password` — пароль
- `detailNum` — искомый артикул

Пример вызова (zeep, Python):
```python
session = requests.Session()
transport = Transport(session=session, timeout=15)
client = zeep.Client(wsdl="http://ws.emex.ru/EmExService.asmx?WSDL", transport=transport)

response = client.service.FindDetailAdv4(
    login=login,
    password=password,
    makeLogo="",
    detailNum=article,
    substLevel="OriginalOnly",
    substFilter="None",
    deliveryRegionType="PRI",
    maxOneDetailOffersCount=50,
    minQuantity=1
)
```

Структура ответа SoapDetailItem:
```
response.Details.SoapDetailItem[] — массив предложений
  .MakeName       — бренд (производитель)
  .DetailNum      — артикул
  .ResultPrice    — цена
  .DDPercent      — процент поставки (0-100)  <-- важно
  .ADDays         — срок поставки (дни)
  .DeliverTimeGuaranteed — гарантированное время доставки (часы)
  .Quantity       — количество
  .PriceLogo      — склад/логотип поставщика
  .DetailNameRus  — название детали
  .DetailLogo     — лого детали
  .DetailRef      — референс
```

## Корзина (EmEx_Basket.asmx)

**WSDL:** http://ws.emex.ru/EmEx_Basket.asmx?WSDL

### InsertToBasket3 — добавление товара в корзину

Параметры:
- `login` — логин (long)
- `password` — пароль
- `ePrices` — массив товаров (EPrice[])

Структура EPrice:
```python
EPrice = client.get_type('{http://tempuri.org/}EPrice')
EPrice(
    Num="1",
    DLogo="...",        # DetailLogo
    MName="...",        # MakeName (бренд)
    MLogo="",
    DNum="...",         # DetailNum (артикул)
    Ref="...",          # DetailRef
    Name="...",         # DetailNameRus
    Com="",             # комментарий
    Quan="1",           # количество
    Price="...",        # ResultPrice
    PLogo="...",        # PriceLogo
    Notc="",
    Error="",
    DeliveryRegionType="PRI"
)
```
