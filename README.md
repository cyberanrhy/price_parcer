# price_parcer (Проценка)

Бесплатный парсер цен автозапчастей. Поиск одновременно по 7 поставщикам — сравнение цен, сроков и кратности в одном окне.

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)]()
[![PyQt6](https://img.shields.io/badge/pyqt6-6.5%2B-blueviolet)]()
[![License](https://img.shields.io/badge/license-MIT-green)]()
[![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)]()
[![Release](https://img.shields.io/github/v/release/cyberanrhy/price_parcer)]()

**Скачать:** https://github.com/cyberanrhy/price_parcer/releases

---

![Скриншот программы](screenshots/main_window.jpg)

---

## О программе

Десктоп-приложение для специалистов по автозапчастям. Отправляет параллельные запросы к API поставщиков, отображает цены с наценкой и позволяет добавлять позиции в корзину поставщика.

Создано для пользователей Skitchen PRO и всех, кто профессионально занимается подбором запчастей.

## Возможности

- Параллельный поиск по всем подключённым поставщикам
- Сравнение цен в общей таблице с сортировкой
- Автоматический расчёт наценки
- Добавление в корзину поставщика
- История поиска с автодополнением
- Чёрный список брендов
- Фильтр поставки Emex (только с поставкой >= 50%)
- Время ответа каждого поставщика
- Проверка белого IP
- Тёмная тема

## Поддерживаемые поставщики

Все поставщики требуют, чтобы ваш IP был внесён в белый список в личном кабинете.

- **Emex** (ws.emex.ru) — SOAP API
- **Profit-League** (pr-lg.ru) — REST API
- **Автосоюз** (avtoso-yz.ru) — REST API
- **Armtek** (armtek.su) — REST API
- **Forum-Auto** (forum-auto.ru) — REST API
- **Mikado** (mikado.su) — HTTP+XML API
- **ABSTD** (abstd.ru) — REST API

## Быстрый старт

**Вариант 1:** Скачайте price_parcer.exe со страницы Releases и запустите.

**Вариант 2:** Запуск из исходного кода:

```
git clone https://github.com/cyberanrhy/price_parcer.git
cd price_parcer
pip install -r requirements.txt
python main.py
```

## Настройка

При первом запуске откроется страница настроек. Для каждого поставщика:
1. Включите чекбоксом
2. Введите данные (логин/пароль или API-ключ)
3. Нажмите Сохранить

Файлы настроек:
- В режиме .py: config/settings.json
- В режиме .exe: %APPDATA%\Проценка\settings.json

## Технологии

Python 3.10+, PyQt6, requests, zeep (SOAP), concurrent.futures

## Структура проекта

```
price_parcer/
  main.py              # GUI (PyQt6)
  settings_page.py     # Страница настроек
  config_path.py       # Пути к конфигам
  emex.py              # Провайдер Emex (SOAP)
  pr_lg.py             # Провайдер Profit-League (REST)
  avtosoyuz.py         # Провайдер Автосоюз (REST)
  armtek.py            # Провайдер Armtek (REST)
  forum_auto.py        # Провайдер Forum-Auto (REST)
  mikado.py            # Провайдер Mikado (HTTP+XML)
  abstd.py             # Провайдер ABSTD (REST)
  screenshots/         # Скриншоты
  config/              # Локальные настройки (в .gitignore)
  requirements.txt     # Зависимости
  *-api.md             # Документация API
```

## Безопасность

- Все данные хранятся только локально
- В исходном коде нет хардкод-паролей или ключей
- Данные не передаются третьим лицам
- Программа подключается только к API поставщиков

## Лицензия

MIT — можно использовать, изменять и распространять без ограничений.
