# price_parcer

**Free cross-supplier auto parts price parser.** Search across 7 Russian auto parts suppliers simultaneously — compare prices, delivery times, and minimum order quantities in one window.

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)]()
[![PyQt6](https://img.shields.io/badge/pyqt6-6.5%2B-blueviolet)]()
[![License](https://img.shields.io/badge/license-MIT-green)]()
[![Platform](https://img.shields.io/badge/platform-Windows%2010%2F11-lightgrey)]()
[![Release](https://img.shields.io/github/v/release/cyberanrhy/price_parcer)]()
[![Status](https://img.shields.io/badge/status-stable-brightgreen)]()

[Download .exe](https://github.com/cyberanrhy/price_parcer/releases)

---

![Screenshot](screenshots/main_window.jpg)

---

## About

**price_parcer** (Проценка) is a desktop application for auto parts professionals. It queries multiple supplier APIs in parallel, displays prices with markup, and allows adding items directly to the supplier's cart.

Built primarily for **Skitchen PRO** users, but works as a standalone multi-supplier API client.

## Features

- Parallel search across all enabled suppliers
- Price comparison table with sorting
- Automatic markup calculation
- Direct cart/order integration
- Search history with autocomplete
- Brand blacklist
- Emex delivery filter (hide items with <50% delivery)
- Per-supplier request timing
- White IP verification
- Dark theme (follows system settings)

## Supported Suppliers

| Supplier | API Type | Search | Cart |
|----------|----------|--------|------|
| Emex (ws.emex.ru) | SOAP (zeep) | Yes | Yes |
| Profit-League (pr-lg.ru) | REST | Yes | Yes |
| Avtosoyuz (avtoso-yz.ru) | REST | Yes | Yes |
| Armtek (armtek.su) | REST | Yes | Yes |
| Forum-Auto (forum-auto.ru) | REST | Yes | Yes |
| Mikado (mikado.su) | HTTP + XML | Yes | Yes |
| ABSTD (abstd.ru) | REST (md5) | Yes | Yes |

> All suppliers require your IP to be whitelisted in their admin panel.

## Quick Start

### Option 1: Download pre-built exe

Download [price_parcer.exe](https://github.com/cyberanrhy/price_parcer/releases/latest) and run it. The settings page will open on first launch.

### Option 2: Run from source

```
git clone https://github.com/cyberanrhy/price_parcer.git
cd price_parcer
pip install -r requirements.txt
python main.py
```

## Configuration

On first launch, the settings page appears. For each supplier:

1. Enable with the checkbox
2. Enter credentials (login/password or API key)
3. Click Save

Config files are stored locally:
- `.py` mode: `config/settings.json`
- `.exe` mode: `%APPDATA%\Проценка\settings.json`

## Tech Stack

Python 3.10+ · PyQt6 · requests · zeep (SOAP) · concurrent.futures

## Project Structure

```
price_parcer/
  main.py                  # GUI (PyQt6)
  settings_page.py         # Settings widget
  config_path.py           # Config path resolver
  emex.py                  # Emex SOAP provider
  pr_lg.py                 # Profit-League REST provider
  avtosoyuz.py             # Avtosoyuz REST provider
  armtek.py                # Armtek REST provider
  forum_auto.py            # Forum-Auto REST provider
  mikado.py                # Mikado HTTP+XML provider
  abstd.py                 # ABSTD REST provider
  screenshots/             # Screenshots
  config/                  # Local config (gitignored)
  requirements.txt         # Dependencies
  *-api.md                 # Supplier API docs
```

## Security

- All credentials are stored **locally only**
- Source code contains **no** hardcoded keys or passwords
- No third-party data sharing
- The app connects only to supplier APIs

## License

MIT — free to use, modify, and distribute.

---

*Built for the auto parts community. Star the repo if you find it useful.*
