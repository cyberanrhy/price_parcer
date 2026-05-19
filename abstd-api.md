# ABSTD API

**Сайт:** https://abstd.ru  
**Base URL:** `https://abstd.ru/`  
**Формат:** JSON (по умолчанию) / XML  
**Кодировка:** UTF-8

---

## 1. Аутентификация

Параметр `auth` передаётся во все запросы как GET-параметр.

**Формула:**
```
auth = lowercase(md5(login + lowercase(md5(password))))
```

**Псевдокод:**
```python
import hashlib
def calc_auth(login, password):
    return hashlib.md5((login + hashlib.md5(password.encode()).hexdigest().lower()).encode()).hexdigest().lower()
```

При неверном `auth` — HTTP 403 Forbidden.

---

## 2. Поиск

### 2.1. Получение списка брендов по артикулу

**GET** `/api-brands`

Параметры:
| Параметр | Обязательный | Описание |
|---|---|---|
| `auth` | да | хэш аутентификации |
| `article` | да | артикул |
| `format` | нет | `json` (по умолч.) или `xml` |

Ответ: массив наименований брендов.

```json
[
    "CALORSTAT BY VERNET",
    "KAYABA",
    "KNECHT",
    "MAHLE"
]
```

### 2.2. Поиск предложений товаров

**GET** `/api-search`

Параметры:
| Параметр | Обязательный | Описание |
|---|---|---|
| `auth` | да | хэш аутентификации |
| `article` | да | артикул |
| `agreement_id` | да | ID договора (из контекста) |
| `brand` | нет | фильтр по бренду |
| `show_unavailable` | нет | 0/1, показывать недоступные |
| `format` | нет | `json` (по умолч.) или `xml` |

Поля ответа (`data` — массив объектов):
| Поле | Тип | Описание |
|---|---|---|
| `brand` | string | Бренд |
| `article` | string | Артикул |
| `product_id` | string | ID товара (для корзины) |
| `product_name` | string | Наименование |
| `delivery_duration` | string | Срок поставки (рабочие дни), число или `"1-3"` |
| `delivery_time` | array | Даты поставки [min, max] |
| `delivery_expires` | string | Срок актуальности дат поставки |
| `nomenclature_id` | string | ID номенклатуры |
| `warehouse_id` | string | ID склада |
| `warehouse_name` | string | Наименование склада |
| `return_type` | object | `{id, name}` — тип возврата |
| `quantity` | string | Доступное количество |
| `quantity_on_the_way` | string | В пути |
| `mult_sale` | string | Кратность продажи |
| `by_request` | string | 0/1 — под заказ (можно заказать при qty=0) |
| `special_order` | string | 0/1 — спецзаказ (без возврата) |
| `updated` | string | Дата обновления |
| `price` | string | Цена |
| `currency` | string | Валюта (RUB) |
| `is_cross` | int | 0 — искомый, 1 — кросс |
| `fail_percent` | int/null | Процент отказов склада (0-100), аналог DDPercent |
| `barcodes` | array/null | Штрихкоды |
| `measure` | object | `{id, name}` — единица измерения |

```json
{
  "status": "OK",
  "data": [
    {
      "brand": "KNECHT",
      "article": "OC47",
      "product_id": "52569142",
      "product_name": "Фильтр масляный",
      "delivery_duration": "1",
      "delivery_time": ["22.03.2024 09:00:00", "22.03.2024 09:00:00"],
      "delivery_expires": "15.03.2024 13:00:00",
      "nomenclature_id": "198795",
      "warehouse_id": "194",
      "warehouse_name": "ABS Ростов 184",
      "return_type": {"id": "1", "name": "Возврат возможен, кроме..."},
      "quantity": "3",
      "quantity_on_the_way": "0",
      "mult_sale": "1",
      "by_request": "0",
      "special_order": "1",
      "updated": "09.12.2019 18:19:54",
      "price": "224.00",
      "currency": "RUB",
      "is_cross": 0,
      "fail_percent": 2,
      "barcodes": ["004690", "4009026026953"],
      "measure": {"id": "796", "name": "шт"}
    }
  ]
}
```

### 2.3. Поиск кроссов

**GET** `/api-search_crosses`

Требует включённой опции "Разрешить поиск кроссов" в ЛК.

Параметры:
| Параметр | Обязательный | Описание |
|---|---|---|
| `auth` | да | хэш |
| `article` | да | артикул |
| `brand` | да | бренд |
| `agreement_id` | да | ID договора |
| `format` | нет | json/xml |

Ответ: аналогичен `api-search`.

---

## 3. Заказы

### 3.1. Список заказов

**GET** `/api-get_orders`

Параметры (все необязательные, для фильтрации):
| Параметр | Описание |
|---|---|
| `auth` | хэш |
| `order_id` | ID заказа |
| `agreement` | ID договора |
| `article` | артикул |
| `desc` | примечание |
| `status` | ID статуса |
| `brand` | бренд |
| `is_archive` | 0/1 |
| `date_begin` | дата с (дд.мм.гггг) |
| `date_end` | дата по (дд.мм.гггг) |
| `external_id` | внешний ID заказа |
| `format` | json/xml |

Поля ответа:
- `status` — OK / ошибка
- `orders` — массив заказов
  - `order_id`, `order_description`, `create_date`
  - `agreement_id`, `agreement_name`
  - `delivery_type_id`, `delivery_name`
  - `warehouse_id`, `warehouse_name`
  - `is_archive`, `end_date`, `external_id`
  - `order_products` — массив товаров:
    - `order_product_id`, `nomenclature_id`
    - `product_name`, `article`, `brand`
    - `price`, `quantity`, `measure_name`
    - `barcodes`, `product_description`
    - `product_statuses` — массив `{status_id, status_name, quantity}`

Статусы обработки (финальные):
| ID | Статус |
|---|---|
| -3 | Отказано |
| 6 | Отгружен |
| 11 | Снят с резерва |
| 12 | Отменен |
| 19 | Возвращен на склад |
| -7 | Отменен клиентом |

### 3.2. Создание заказа

**GET** `/api-create_order`

Параметры:
| Параметр | Обязательный | Описание |
|---|---|---|
| `auth` | да | хэш |
| `ua_id` | да | ID договора пользователя |
| `uda_id` | да | ID адреса доставки |
| `dt_id` | да | ID способа доставки |
| `prods` | да | массив `[product_id]=quantity` |
| `p_desc` | нет | массив примечаний `[product_id]=текст` |
| `desc` | нет | примечание к заказу |
| `initial_price` | нет | массив `[product_id]=цена` (предотвращает изменение цены) |
| `external_id` | нет | внешний ID (до 32 симв., уникальный) |
| `format` | нет | json/xml |

### 3.3. Отмена заказа

**GET** `/api-cancel_order`

Параметры:
| Параметр | Обязательный |
|---|---|
| `auth` | да |
| `order_id` | да |
| `format` | нет |

---

## 4. Корзина

### 4.1. Получение содержимого

**GET** `/api-cart_get`

| Параметр | Описание |
|---|---|
| `auth` | хэш |
| `cart_id` | нет, 0 = основная |
| `format` | нет |

Ответ: `{products: [{product_id, quantity, price, warehouse_id, ...}]}`

### 4.2. Добавление в корзину

**GET** `/api-cart_add`

| Параметр | Обязательный |
|---|---|
| `auth` | да |
| `agreement_id` | да |
| `prod` | да, массив `[product_id]=quantity` |
| `cart_id` | нет, 0 = основная |
| `desc` | нет, `[product_id]=текст` |
| `format` | нет |

### 4.3. Удаление из корзины

**GET** `/api-cart_delete`

---

## 5. Контекст пользователя

**GET** `/api-get_user_context`

| Параметр | Описание |
|---|---|
| `auth` | хэш |
| `format` | нет |

Ответ содержит:
- `user_agreements` — договоры `[{ua_id, name, credit, balance}]`
- `user_delivery_addresses` — адреса доставки
- `delivery_types` — способы доставки
- `warehouses` — склады
- `carts` — корзины `[{cart_id, cart_name, prod_count, price_sum}]`

---

## Маппинг полей для программы

| API поле | Наше поле | Примечание |
|---|---|---|
| `product_id` | id для корзины | |
| `brand` | `brand` | |
| `article` | `article` | |
| `product_name` | `name` | |
| `price` | `price` | |
| `mult_sale` | `multiplicity` | кратность |
| `quantity` | `stock` | остаток |
| `fail_percent` | `delivery_percent` | 100 - fail_percent |
| `delivery_duration` | `delivery_days` | рабочие дни |
| `warehouse_name` | `warehouse` | склад |
| `is_cross` | — | 1 = аналог |
