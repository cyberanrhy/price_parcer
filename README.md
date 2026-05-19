<p align="center">
  <img src="https://img.shields.io/badge/python-3.10%2B-blue?style=flat-square" alt="Python">
  <img src="https://img.shields.io/badge/pyqt6-6.5%2B-blueviolet?style=flat-square" alt="PyQt6">
  <img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="License">
  <img src="https://img.shields.io/badge/platform-Windows%2010%2F11-lightgrey?style=flat-square" alt="Platform">
  <img src="https://img.shields.io/github/v/release/cyberanrhy/price_parcer?style=flat-square" alt="Release">
  <img src="https://img.shields.io/badge/status-stable-brightgreen?style=flat-square" alt="Status">
</p>

<h1 align="center">🔧 Проценка · price_parcer</h1>

<p align="center">
  <b>Бесплатный парсер цен автозапчастей</b><br>
  Одновременный поиск по 7 поставщикам · Сравнение · Заказ
</p>

<p align="center">
  <a href="https://github.com/cyberanrhy/price_parcer/releases"><b>📥 Скачать .exe</b></a>
  &nbsp;·&nbsp;
  <a href="#-быстрый-старт"><b>🚀 Быстрый старт</b></a>
  &nbsp;·&nbsp;
  <a href="#-поддерживаемые-поставщики"><b>📦 Поставщики</b></a>
</p>

<br>

<p align="center">
  <img src="screenshots/main_window.png" alt="Скриншот программы" width="800">
</p>

<br>

---

## 📌 О проекте

**Проценка** — это десктоп-приложение для поиска и сравнения цен на автозапчасти через API российских поставщиков. В одном окне вы видите цены, сроки доставки и кратность от Emex, Profit-League, Автосоюза, Armtek и других — и можете сразу отправить деталь в корзину поставщика.

Проект создан для пользователей **Skitchen PRO** и всех, кто профессионально занимается подбором автозапчастей.

---

## ✨ Возможности

| | |
|---|---|
| 🔍 **Параллельный поиск** | Одновременный запрос ко всем подключённым поставщикам |
| 📊 **Сравнение цен** | Единая таблица с сортировкой по цене, сроку, поставщику |
| 💰 **Наценка** | Автоматический расчёт продажной цены |
| 🛒 **Корзина поставщика** | Добавление позиций напрямую в заказ |
| 📜 **История поиска** | Автодополнение при вводе |
| 🚫 **Чёрный список брендов** | Исключение ненужных производителей |
| 📈 **Фильтр поставки Emex** | Только позиции с поставкой ≥50% |
| ⏱ **Тайминги запросов** | Сколько времени ответил каждый поставщик |
| 🌐 **Проверка IP** | Контроль белого IP поставщика |
| 🌙 **Тёмная тема** | Автоматически подстраивается под систему |

---

## 🏪 Поддерживаемые поставщики

| Поставщик | API | Поиск | Корзина |
|-----------|-----|:-----:|:-------:|
| [Emex](https://emex.ru) (ws.emex.ru) | SOAP (zeep) | ✅ | ✅ |
| [Profit-League](https://pr-lg.ru) (pr-lg.ru) | REST | ✅ | ✅ |
| [Автосоюз](https://avtoso-yz.ru) (avtoso-yz.ru) | REST | ✅ | ✅ |
| [Armtek](https://armtek.su) (armtek.su) | REST | ✅ | ✅ |
| [Forum-Auto](https://forum-auto.ru) (forum-auto.ru) | REST | ✅ | ✅ |
| [Mikado](https://mikado.su) (mikado.su) | HTTP + XML | ✅ | ✅ |
| [ABSTD](https://abstd.ru) (abstd.ru) | REST (md5) | ✅ | ✅ |

> ⚠️ Все поставщики требуют, чтобы ваш IP был внесён в белый список в их личном кабинете.

---

## 🚀 Быстрый старт

### Вариант 1: готовый exe

1. Скачайте [price_parcer.exe](https://github.com/cyberanrhy/price_parcer/releases/latest)
2. Запустите — откроется страница настроек
3. Заполните данные поставщиков, нажмите «Сохранить»
4. На главной странице введите артикул и нажмите Enter

### Вариант 2: из исходного кода

```bash
git clone https://github.com/cyberanrhy/price_parcer.git
cd price_parcer
pip install -r requirements.txt
python main.py
```

### Вариант 3: сборка exe самостоятельно

```bash
pip install auto-py-to-exe
auto-py-to-exe
```

Настройки: onefile, window-based (без консоли).

---

## ⚙️ Настройка поставщиков

При первом запуске откроется страница настроек. Для каждого поставщика нужно:

1. Включить его чекбоксом
2. Ввести учётные данные:
   - **Emex** — логин и пароль от ws.emex.ru
   - **Profit-League** — secret key из настроек API
   - **Автосоюз** — логин и пароль
   - **Armtek** — логин, пароль, VKORG, KUNNR_RG
   - **Forum-Auto**, **Mikado**, **ABSTD** — данные от ЛК
3. Нажать «Сохранить»

Данные хранятся локально:
- В режиме `.py`: `config/settings.json`
- В режиме `.exe`: `%APPDATA%\Проценка\settings.json`

---

## 🧱 Структура проекта

```
price_parcer/
├── main.py              # GUI приложение (PyQt6)
├── settings_page.py     # Страница настроек
├── config_path.py       # Пути к конфигам
├── emex.py              # Провайдер Emex (SOAP)
├── pr_lg.py             # Провайдер Profit-League (REST)
├── avtosoyuz.py         # Провайдер Автосоюз (REST)
├── armtek.py            # Провайдер Armtek (REST)
├── forum_auto.py        # Провайдер Forum-Auto (REST)
├── mikado.py            # Провайдер Mikado (HTTP+XML)
├── abstd.py             # Провайдер ABSTD (REST)
├── screenshots/         # Скриншоты
├── config/              # Локальные настройки (в .gitignore)
├── requirements.txt     # Зависимости
└── *-api.md             # Документация API поставщиков
```

**Стек:** Python 3.10+ · PyQt6 · requests · zeep (SOAP) · concurrent.futures

---

## 🔐 Безопасность

- Все учётные данные хранятся **только на вашем компьютере**
- Исходный код **не содержит** тестовых или реальных ключей доступа
- Данные не передаются третьим лицам
- Программа подключается только к API поставщиков

---

## 📄 Лицензия

Распространяется под лицензией **MIT**. Можно использовать, изменять и распространять без ограничений.

---

<p align="center">
  <sub>Сделано для сообщества авторазбора</sub><br>
  <sub>⭐ Если проект полезен — поставьте звезду</sub>
</p>
