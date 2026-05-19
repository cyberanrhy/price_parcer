# price_parcer

Free cross-supplier auto parts price parser. Search across 7 Russian auto parts suppliers simultaneously — compare prices, delivery times, and minimum order quantities in one window.

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)]()
[![PyQt6](https://img.shields.io/badge/pyqt6-6.5%2B-blueviolet)]()
[![License](https://img.shields.io/badge/license-MIT-green)]()
[![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)]()
[![Release](https://img.shields.io/github/v/release/cyberanrhy/price_parcer)]()

**Download:** https://github.com/cyberanrhy/price_parcer/releases

---

## About

Desktop application for auto parts professionals. Queries multiple supplier APIs in parallel, displays prices with automatic markup, and allows adding items directly to the supplier cart.

Built for Skitchen PRO users and anyone working with auto parts procurement.

## Features

- Parallel search across all enabled suppliers
- Price comparison table with sorting
- Automatic markup calculation
- Direct cart/order integration
- Search history with autocomplete
- Brand blacklist
- Emex delivery filter
- Request timing display
- White IP verification
- Dark theme

## Supported Suppliers

All suppliers require your IP to be whitelisted in their admin panel.

- **Emex** (ws.emex.ru) - SOAP API
- **Profit-League** (pr-lg.ru) - REST API
- **Avtosoyuz** (avtoso-yz.ru) - REST API
- **Armtek** (armtek.su) - REST API
- **Forum-Auto** (forum-auto.ru) - REST API
- **Mikado** (mikado.su) - HTTP+XML API
- **ABSTD** (abstd.ru) - REST API

## Quick Start

**Option 1:** Download price_parcer.exe from Releases and run it.

**Option 2:** Run from source:

```
git clone https://github.com/cyberanrhy/price_parcer.git
cd price_parcer
pip install -r requirements.txt
python main.py
```

## Configuration

On first launch the settings page opens. For each supplier:
1. Enable with checkbox
2. Enter credentials (login/password or API key)
3. Click Save

Config files:
- .py mode: config/settings.json
- .exe mode: %APPDATA%\Проценка\settings.json

## Tech Stack

Python 3.10+, PyQt6, requests, zeep (SOAP), concurrent.futures

## Project Structure

```
price_parcer/
  main.py              # GUI (PyQt6)
  settings_page.py     # Settings page
  config_path.py       # Config path resolver
  emex.py              # Emex SOAP provider
  pr_lg.py             # Profit-League REST provider
  avtosoyuz.py         # Avtosoyuz REST provider
  armtek.py            # Armtek REST provider
  forum_auto.py        # Forum-Auto REST provider
  mikado.py            # Mikado HTTP+XML provider
  abstd.py             # ABSTD REST provider
  screenshots/         # Screenshots
  config/              # Local config (gitignored)
  requirements.txt     # Dependencies
  *-api.md             # API documentation
```

## Security

- All credentials stored locally only
- No hardcoded keys or passwords in source
- No third-party data sharing
- App connects only to supplier APIs

## License

MIT - free to use, modify, and distribute.
