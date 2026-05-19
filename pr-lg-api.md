# Profit-League API — полная документация (версия 1.4)

**API-ключ:** qIa-vGwS751DMM_w1LtL2PfdNIvi3t-6  
**Базовый URL:** https://api.pr-lg.ru

## Авторизация
Все запросы передают параметр `secret` с API-ключом.

---

## Эндпоинты

### Поиск товаров по артикулу
**GET** `/search/products`

| Параметр | Тип | Описание |
|----------|-----|----------|
| secret | string | API-ключ |
| article | string | Артикул |

Ответ: массив — article, brand, description, brand_warranty, original, countProducts

### Поиск товаров с наличием
**GET** `/search/items`

| Параметр | Тип | Описание |
|----------|-----|----------|
| secret | string | API-ключ |
| article | string | Артикул |

Ответ — массив групп по брендам:
- `brand` — бренд
- `products` — массив товаров по складам:
  - `article_id` (int) — ID товара в системе (для корзины)
  - `warehouse_id` (int) — ID поставщика (для корзины)
  - `product_code` (string) — код для 1С (для корзины)
  - `description` — описание
  - `price` — цена
  - `quantity` — количество
  - `custom_warehouse_name` — название склада
  - `show_date` — срок поставки
  - `delivery_time` — часы поставки
  - `multi` — кратность (мин. кол-во в заказе)
  - `sale` — уценка (0/1)
  - `incart` — уже в корзине
  - `waitings` — ожидаемое кол-во

### Корзина: добавить товар
**POST** `/cart/add`

| Параметр | Тип | Обязательный | Описание |
|----------|-----|-------------|----------|
| secret | string | да | API-ключ |
| id | int | да | article_id из поиска |
| warehouse | int | да | warehouse_id из поиска |
| quantity | int | да | Количество |
| code | string | да | product_code из поиска |
| comment | string | нет | Комментарий (255 символов) |

Ответ: `{"status": "success"/"error"/"no-quantity"/"less", "total": float, "count": int}`

### Корзина: список
**GET** `/cart/list`

| Параметр | Тип |
|----------|-----|
| secret | string |

### Корзина: удалить товар
**POST** `/cart/remove`

| Параметр | Тип |
|----------|-----|
| secret | string |
| id | int |
| warehouse | int |

### Корзина: установить торговую точку
**POST** `/cart/point`

| Параметр | Тип |
|----------|-----|
| secret | string |
| code | string |

### Корзина: параметры заказа
**GET** `/cart/params`

| Параметр | Тип |
|----------|-----|
| secret | string |

Ответ: methods, points, pickup_points, payment, statuses

### Корзина: оформить заказ
**POST** `/cart/order`

| Параметр | Тип | Описание |
|----------|-----|----------|
| secret | string | API-ключ |
| method | int | ID доставки |
| payment | int | ID оплаты |
| point | string | Код торговой точки |
| address | string | Адрес |
| pickup_point | string | Код самовывоза |

### Склады
**GET** `/search/warehouses`

| Параметр | Тип |
|----------|-----|
| secret | string |
| action | "list" |

### Заказы
**GET** `/orders/list`

| Параметр | Тип |
|----------|-----|
| secret | string |
| page | int |
| order_id | string |
| status_id | int |
| date_start / date_end | string |
