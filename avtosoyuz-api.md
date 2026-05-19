# Автосоюз API — полная документация

**API Base URL (punycode):** `https://api.xn--80aep1aarf3h.xn--p1ai`  
**API Base URL (рус):** `https://api.автосоюз.рф`  
**Сайт:** https://автосоюз.рф  
**Email для подключения:** request@s4ab.ru  
**Swagger:** https://автосоюз.рф/API_Documentation (после авторизации)

## Подключение
1. Зарегистрироваться на сайте https://автосоюз.рф
2. Написать на `request@s4ab.ru` с темой "Подключение к Web-сервисам API автосоюз.рф"
3. Указать: логин, URL сайта + CMS, IP-адрес
4. После открытия доступа — документация по `/API_Documentation`

## Авторизация
**Basic Auth:** заголовок `Authorization: Basic {credentials}`
где `credentials` = `Base64(Login:Password)` (логин и пароль от сайта)

## Форматы
- Все запросы: **GET** (кроме ChangeBasketPositionComment/Count/Remove/Clear/Checkout — **POST**)
- Заголовки: `Accept: application/json`, `Content-type: application/json`
- Параметры URL кодировать через `HttpUtility.UrlEncode`
- Тип bool: только `true`/`false` (не 0/1)

---

## Эндпоинты

### Получение брендов по артикулу
**GET** `/SearchService/GetBrands?article={article}&withoutTransit={true/false}`

| Параметр | Тип | Описание |
|----------|-----|----------|
| article | string | Артикул |
| withoutTransit | bool | Не возвращать транзитных |

Ответ — массив:
- `Article` — артикул (string)
- `Brand` — производитель/бренд (string)
- `Description` — описание детали (string)

### Поиск цен и наличия
**GET** `/SearchService/GetParts?article={article}&brand={brand}&withoutTransit={true/false}`

| Параметр | Тип | Описание |
|----------|-----|----------|
| article | string | Артикул |
| brand | string | Бренд |
| withoutTransit | bool | Не возвращать транзитных |

Ответ — массив:
| Поле | Тип | Описание |
|------|-----|----------|
| Article | string | Артикул |
| Brand | string | Бренд |
| CostSale | double | Цена продажи |
| Count | short | Количество |
| CountText | string | Кол-во текстом (напр. ">10") |
| Description | string | Наименование детали |
| IsAllowDiscountRefund | bool | Возможен возврат |
| IsAnalog | bool | Аналог |
| IsDefective | bool | Уценка |
| IsOriginal | bool | Оригинал |
| IsWarehouse | bool | Собственный склад |
| MinCount | int? | Кратность (партийность) |
| SupplierColor | string | Цвет строки на сайте (#6adafc) |
| SupplierLastUpdate | string | Дата обновления прайса |
| SupplierName | string | Название поставщика |
| SupplierPercent | int? | Вероятность поставки (0-100) |
| SupplierTimeMax | short? | Макс. срок поставки (часы) |
| SupplierTimeMin | short? | Мин. срок поставки (часы) |

### Добавление в корзину
**GET** `/SearchService/AddToBasket?article={article}&brand={brand}&supplierName={supplierName}&costSale={costSale}&quantity={count}&supplierTimeMin={supplierTimeMin}&supplierTimeMax={supplierTimeMax}&comment={comment}`

Ответ: "Ok" / "Position was not found" / "Error: ..."

### Получение корзины
**GET** `/SearchService/GetBasket`

Ответ — массив:
- `Article`, `Brand`, `Description`
- `Cost` — цена (double)
- `Count` — количество (short)
- `MinCount` — кратность
- `SupCode` — поставщик (string)
- `SupTimeMin`, `SupTimeMax` — срок в часах
- `Id` — номер позиции (int)

### Изменение комментария в корзине
**POST** `/SearchService/ChangeBasketPositionComment?positionId={positionId}&comment={comment}`

### Изменение количества в корзине
**POST** `/SearchService/ChangeBasketPositionCount?positionId={positionId}&count={count}`

### Удаление позиции из корзины
**POST** `/SearchService/RemoveBasketPosition?positionId={positionId}`

### Очистка корзины
**POST** `/SearchService/ClearBasket` → `{"IsSuccess": true/false}`

### Отправка товаров в заказ (без корзины)
**GET** `/SearchService/AddOrder?items=[{article,brand,SupplierName,CostSale,Quantity,SupplierTimeMin,SupplierTimeMax,Comment,GioID}]`

Параметр `items` — JSON-массив, закодированный в URL.
Ответ: `AddToOrderResult`, `AddToOrderStatus`, `OrderID`, `GioId`

### Получение статусов заказа
**GET** `/SearchService/GetPositionsByOrder/{orderId}`

Ответ — массив: Article, Brand, CostSale, Count, DateAdded, DeliveryTimeMin/Max, Description, Status (Id, CategoryId, Name, Color, Date, IsCompletedLabel, Count), SubOrderId, Sum, SupplierName, RefusedCount

### Параметры оформления заказа
**GET** `/SearchService/GetCheckoutParams` → Deliveries, Payments, Points, Addresses

### Оформление заказа из корзины
**POST** `/SearchService/CheckoutBasket?positionIds={ids}&deliveryTypeId={deliveryTypeId}&paymentTypeId={paymentTypeId}&addressId={addressId}&deliveryPointId={deliveryPointId}&comment={comment}`

---

## Ограничения
- Суточный лимит запросов
- IP-адрес должен совпадать с указанным при регистрации
- Транзитные поставщики могут быть недоступны при исчерпании лимита
- Параметры URL нужно кодировать
- Параметр withoutTransit принимает только `true`/`false` (не 0/1)

## Интеграция с "Проценкой"
Можно добавить как нового провайдера `AvtosoyuzProvider`:
- Auth: Basic (логин:пароль от сайта)
- Search: `/SearchService/GetBrands` → `/SearchService/GetParts`
- Cart: `/SearchService/AddToBasket`
- Поля: `SupplierPercent` → delivery_percent, `MinCount` → multiplicity, `SupplierTimeMin/Max` → срок в днях (часы / 24)
- Цвет поставщика: `SupplierColor` (можно для подсветки строки)
