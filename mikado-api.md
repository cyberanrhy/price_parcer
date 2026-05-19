# Mikado (Микадо) API

**Сайт:** https://mikado-parts.ru
**Управление доступом (личный кабинет):** https://mikado-parts.ru/office/ws_panel.asp
**Для подключения:** письмо администратору `gmv@mikado-parts.ru` (указать клиентский номер, цель, IP-адреса)

---

## Аутентификация

Код клиента (`ClientID`) + пароль (`Password`) от личного кабинета.

---

## WebService URL

| Сервис | URL |
|--------|-----|
| Проценка (поиск) | `http://www.mikado-parts.ru/ws1/service.asmx` |
| Корзина | `http://www.mikado-parts.ru/ws1/basket.asmx` |
| Экспресс-доставка | `https://mikado-parts.ru/ws1/express.asmx` |
| История поставок | `http://www.mikado-parts.ru/ws1/deliveries.asmx` |

---

## Методы поиска (service.asmx)

### Code_Search — поиск по артикулу

Ищет код по всем брендам, включая аналоги.

**Параметры:**
- `Code` — артикул (для теста всегда находит "12345")
- `ClientID` — код клиента
- `Password` — пароль

**Результат:** список кодов, сгруппированных по бренду (`SourceProducer`).
Важные поля в результате:
| Поле | Описание |
|------|----------|
| `SourceProducer` | Бренд |
| `ZakazCode` | Код для заказа (с префиксом Микадо, напр. `xbs-0265008089`) |
| `CodeType` | Aftermarket / OEM / Analog / AnalogOEM |
| `PriceRUR` | Цена в рублях (с учётом скидок) |
| `Name` | Наименование детали |
| `OnStocks/StockLine` | Массив: `StokName`, `StokID`, `StockQTY` |
| `Srock` | Срок поставки (рабочие дни). `?` — не определён |
| `MinZakazQTY` | Кратность заказа |

Лимит: ~2000 запросов/сутки (кроме `CodeBrandStockInfo`).

### Code_Info — детальная информация

Для оригинальных запчастей (OEM/AnalogOEM) показывает варианты поставки.

**Параметры:**
- `ZakazCode` — заказной код (с префиксом Микадо)
- `ClientID`, `Password`

**Доп. поля:**
- `DeliveryType` — код варианта поставки (для корзины)
- `SrockMax` — макс. срок поставки
- `Rating` — вероятность выполнения (%)

### CodeBrandStockInfo — быстрый поиск по бренду+коду (РЕКОМЕНДУЕТСЯ)

Работает **в 100 раз быстрее** `Code_Search`, **БЕЗ ЛИМИТА** запросов. Только наличие, без аналогов.

**Параметры:**
- `Code` — артикул
- `Brand` — бренд (производитель)
- `ClientID` — код клиента
- `Password` — пароль

**Результат:**
```xml
<CodeBrandResult>
  <Code_Search>0265008089</Code_Search>
  <Brand_Search>BOSCH</Brand_Search>
  <Message>Ok</Message>
  <List>
    <CodeBrandLine>
      <OrderCode>xbs-0265008089</OrderCode>
      <PriceRUR>528.99</PriceRUR>
      <Brand>BOSCH</Brand>
      <Name>Датчик abs Opel Corsa D</Name>
      <StokID>1</StokID>
      <StokName>Осн. склад СПб</StokName>
      <StockQTY>6</StockQTY>
      <MinZakazQTY>1</MinZakazQTY>
      <DeliveryDelay>0</DeliveryDelay>
    </CodeBrandLine>
  </List>
</CodeBrandResult>
```

| Поле | Описание |
|------|----------|
| `OrderCode` | Код для заказа |
| `PriceRUR` | Цена в рублях |
| `Brand` | Бренд |
| `Name` | Наименование |
| `StokID` | Код склада (1 = центральный) |
| `StokName` | Название склада |
| `StockQTY` | Кол-во на складе (4+, 10+, 20+, 100+ при большом остатке) |
| `MinZakazQTY` | Кратность заказа |
| `DeliveryDelay` | Задержка (рабочие дни) |

---

## Методы корзины (basket.asmx)

### Basket_Add — добавить в корзину

**Параметры:**
| Параметр | Описание |
|----------|----------|
| `ZakazCode` | Заказной код (с префиксом, напр. `xbs-0265008089`) |
| `QTY` | Кол-во (>0, <1000) |
| `DeliveryType` | Код варианта поставки (для OEM; для неоригинала = 0) |
| `Notes` | Примечание (сохраняется, но не обрабатывается) |
| `ClientID` | Код клиента |
| `Password` | Пароль |
| `ExpressID` | ID экспресс-доставки (0 = нет) |
| `StockID` | Код склада (1 = центральный) |

**Результат:** `<Message>OK</Message>` + `<ID>` уникальный номер записи.

### Basket_List — просмотр корзины

**Параметры:** `ClientID`, `Password`

**Результат:** список `BasketItem` с `ID`, `ZakazCode`, `Name`, `QTY`, `Price`, `Status`, `Srok`, `Notes`.

### Basket_Delete — удалить из корзины

**Параметры:** `ItemID`, `ClientID`, `Password`

### Zakaz_History — история заказа

**Параметры:** `nOrderID`

---

## Ограничения

- **Code_Search / Code_Info**: до 2000 запросов/сутки (может быть увеличено администратором)
- **CodeBrandStockInfo**: безлимитно
- Блокировать индексирование поисковыми роботами страниц с запросами к API
- Запрещено создавать избыточные запросы без реальных заказов

---

## Тестирование (без реальных данных)

- `Code_Search("12345")` — работает с любыми ClientID/Password
- `Code_Info("xbm-123/45")` — тестовый код
- `Code_Info("gfi7563985")` — тестовый код
