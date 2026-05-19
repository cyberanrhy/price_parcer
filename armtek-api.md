# Armtek API — документация

**API Base URL:** `https://ws.armtek.ru/api/`
**Сайт:** https://armtek.ru
**Документация:** https://ws.armtek.ru/

## Подключение
- Авторизация: **Basic Auth** (логин и пароль от ЭТП armtek.ru)
- Формат: JSON (`?format=json`)

## Поиск цен и наличия

**POST** `/ws_search/search`

### Параметры запроса

| Параметр | Тип | Обязательный | Описание |
|----------|-----|-------------|----------|
| VKORG | string (4) | Да | Сбытовая организация |
| KUNNR_RG | string (10) | Да | Покупатель |
| PIN | string (40) | Да | Артикул |
| BRAND | string (18) | Нет | Бренд |
| QUERY_TYPE | 1/2 | Нет | 1 — без аналогов, 2 — с аналогами |
| PROGRAM | LP/GP | Нет | Легковая/грузовая программа |
| KUNNR_ZA | string (10) | Нет | Адрес доставки |
| INCOTERMS | 0/1 | Нет | 1 — самовывоз |
| VBELN | string (10) | Нет | Договор |
| format | string | Нет | "json" |

### Ответ (RESP → ARRAY)

| Поле | Тип | Описание |
|------|-----|----------|
| PIN | string | Артикул |
| BRAND | string | Бренд |
| NAME | string | Наименование |
| ARTID | string | Уникальный ID |
| PARNR | string | Код склада партнёра |
| KEYZAK | string | Код склада |
| RVALUE | string | Доступное количество |
| RETDAYS | number | Дней на возврат |
| RDPRF | string | Кратность |
| MINBM | string | Минимальное количество |
| VENSL | string | Вероятность поставки (%) |
| PRICE | string | Цена |
| WAERS | string | Валюта |
| DLVDT | string | Дата поставки (YYYYMMDDHHIISS) |
| WRNTDT | string | Дата гарантированной поставки |
| ANALOG | string | Признак аналога |

## Создание заказа

**POST** `/ws_order/createOrder`

### Параметры запроса

| Параметр | Тип | Обязательный | Описание |
|----------|-----|-------------|----------|
| VKORG | string (4) | Да | Сбытовая организация |
| KUNRG | string (10) | Да | Покупатель |
| KUNWE | string (10) | Нет | Грузополучатель |
| KUNZA | string (10) | Нет | Адрес доставки |
| INCOTERMS | 0/1 | Нет | Самовывоз |
| VBELN | string (10) | Нет | Договор |
| TEXT_ORD | string (100) | Нет | Комментарий к заказу |
| ITEMS | массив | Да | Таблица артикулов |

### Таблица ITEMS

| Поле | Тип | Обязательный | Описание |
|------|-----|-------------|----------|
| PIN | string | Да | Артикул |
| BRAND | string | Да | Бренд |
| KWMENG | number | Да | Количество |
| KEYZAK | string | Нет | Код склада |
| PRICEMAX | string | Нет | Макс. цена |
| DATEMAX | string | Нет | Макс. дата поставки |
| COMMENT | string | Нет | Комментарий |

### Формат параметров (form-data)
```
ITEMS[0][PIN]=артикул&ITEMS[0][BRAND]=бренд&ITEMS[0][KWMENG]=1&ITEMS[0][KEYZAK]=склад
```

## Проверка соединения

**GET** `/ws_ping/ping?format=json`
- Headers: `Authorization: Basic ...`

## Общий формат ответа

```json
{
  "STATUS": 200,
  "MESSAGES": [
    {"TYPE": "S", "TEXT": "Успешно", "DATE": "..."}
  ],
  "RESP": { ... }
}
```

- STATUS: HTTP-код (200 = успех)
- MESSAGES[TYPE]: A/E/S/W/I (критическая ошибка/ошибка/успех/предупреждение/инфо)
- RESP: тело ответа (зависит от сервиса)
