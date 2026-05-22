import json
import os
import sys
import requests
import zeep
from zeep.transports import Transport
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QSpinBox, QLineEdit, QFrame,
                             QSizePolicy, QDoubleSpinBox, QScrollArea, QCheckBox)
from PyQt6.QtCore import pyqtSignal, Qt, QTimer
from PyQt6.QtGui import QColor, QFont
from config_path import get_settings_path

CONFIG_PATH = get_settings_path()

_is_frozen = getattr(sys, 'frozen', False)


class SettingsPage(QWidget):
    saved = pyqtSignal()
    back_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings_data = self._read_settings()
        self._provider_fields = {}
        self._provider_enabled = {}
        self._check_buttons = {}
        self._build_ui()
        self._fill_fields()

    def _read_settings(self):
        default = {
            "emex": {"enabled": True, "login": "", "password": ""},
            "profit_league": {"enabled": True, "api_key": ""},
            "avtosoyuz": {"enabled": True, "login": "", "password": ""},
            "armtek": {"enabled": True, "login": "", "password": "", "vkorg": "", "kunnr": ""},
            "forum_auto": {"enabled": True, "login": "", "password": ""},
            "mikado": {"enabled": True, "login": "", "password": ""},
            "abstd": {"enabled": True, "login": "", "password": "", "agreement_id": ""},            "1c": {"enabled": False, "conn_string": "", "login": "", "password": ""},
            "default_markup": 0,
            "default_comment": "",
            "expected_ip": "",
            "first_run": True
        }
        if _is_frozen:
            default["emex"]["enabled"] = False
            default["profit_league"]["enabled"] = False
            default["avtosoyuz"]["enabled"] = False
            default["armtek"]["enabled"] = False
            default["forum_auto"]["enabled"] = False
            default["mikado"]["enabled"] = False
            default["abstd"]["enabled"] = False
        try:
            with open(CONFIG_PATH, encoding="utf-8") as f:
                return json.load(f)
        except:
            return default

    def _write_settings(self, data):
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _build_ui(self):
        self.setStyleSheet("""
            QLineEdit, QSpinBox, QDoubleSpinBox {
                padding: 6px; font-size: 13px; min-height: 28px;
                border: 1.5px solid #d2d2d7; border-radius: 6px; background: white;
            }
            QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {
                border-color: #2563eb;
            }
        """)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: #f5f5f7; }")

        inner = QWidget()
        layout = QVBoxLayout(inner)
        layout.setContentsMargins(20, 14, 20, 14)
        layout.setSpacing(8)

        # --- Header ---
        header = QHBoxLayout()
        self.btn_back = QPushButton("в†ђ РќР°Р·Р°Рґ")
        self.btn_back.setStyleSheet("""
            QPushButton { background: transparent; color: #2563eb; font-size: 13px; font-weight: 600;
                          border: none; padding: 4px 10px; }
            QPushButton:hover { color: #1d4ed8; }
        """)
        self.btn_back.clicked.connect(self.back_requested.emit)
        header.addWidget(self.btn_back)

        title = QLabel("РќР°СЃС‚СЂРѕР№РєРё API")
        title.setStyleSheet("font-size: 18px; font-weight: 700; color: #1d1d1f;")
        header.addWidget(title)
        header.addStretch()

        self.btn_save_top = QPushButton("РЎРѕС…СЂР°РЅРёС‚СЊ")
        self.btn_save_top.setMinimumHeight(34)
        self.btn_save_top.setStyleSheet("""
            QPushButton { background: #2563eb; color: white; font-size: 12px; font-weight: 700;
                          padding: 0 16px; border-radius: 8px; border: none; }
            QPushButton:hover { background: #1d4ed8; }
            QPushButton:disabled { background: #9ca3af; }
        """)
        self.btn_save_top.clicked.connect(self._save)
        header.addWidget(self.btn_save_top)

        layout.addLayout(header)

        # --- РљРѕРјРјРµРЅС‚Р°СЂРёР№ РїРѕ СѓРјРѕР»С‡Р°РЅРёСЋ (РІ СЃР°РјС‹Р№ РІРµСЂС…) ---
        self._add_section_header(layout, "РљРћРњРњР•РќРўРђР РР™ РџРћ РЈРњРћР›Р§РђРќРР®")
        self.default_comment = QLineEdit()
        self.default_comment.setPlaceholderText("РљРѕРјРјРµРЅС‚Р°СЂРёР№ Рє РїРѕР·РёС†РёРё РІ РєРѕСЂР·РёРЅРµ...")
        layout.addWidget(self.default_comment)

        # --- Р–РёСЂРЅС‹Р№ СЂР°Р·РґРµР»РёС‚РµР»СЊ ---
        big_sep = QFrame()
        big_sep.setFrameShape(QFrame.Shape.HLine)
        big_sep.setStyleSheet("background: #d2d2d7; max-height: 2px; margin: 6px 0;")
        layout.addWidget(big_sep)

        # --- РќР°С†РµРЅРєР° РїРѕ СѓРјРѕР»С‡Р°РЅРёСЋ ---
        self._add_section_header(layout, "РќРђР¦Р•РќРљРђ РџРћ РЈРњРћР›Р§РђРќРР®")
        row_markup = QHBoxLayout()
        row_markup.setSpacing(6)
        row_markup.addWidget(QLabel("РќР°С†РµРЅРєР°:"))
        self.default_markup = QDoubleSpinBox()
        self.default_markup.setRange(0, 999)
        self.default_markup.setSingleStep(0.5)
        self.default_markup.setDecimals(1)
        self.default_markup.setSuffix(" %")
        self.default_markup.setValue(0)
        row_markup.addWidget(self.default_markup, 1)
        layout.addLayout(row_markup)

        # --- РћР¶РёРґР°РµРјС‹Р№ IP ---
        self._add_section_header(layout, "РћР–РР”РђР•РњР«Р™ IP")
        row_ip = QHBoxLayout()
        row_ip.setSpacing(6)
        row_ip.addWidget(QLabel("IP Р°РґСЂРµСЃ:"))
        self.expected_ip = QLineEdit()
        self.expected_ip.setPlaceholderText("РќР°РїСЂРёРјРµСЂ: 95.24.137.82")
        row_ip.addWidget(self.expected_ip, 1)

        self.btn_detect_ip = QPushButton("РћРїСЂРµРґРµР»РёС‚СЊ")
        self.btn_detect_ip.setFixedHeight(30)
        self.btn_detect_ip.setStyleSheet("""
            QPushButton { background: #e5e7eb; color: #374151; padding: 4px 12px; font-size: 11px;
                          font-weight: 600; border-radius: 6px; border: none; }
            QPushButton:hover { background: #d1d5db; }
            QPushButton:disabled { background: #e5e7eb; color: #9ca3af; }
        """)
        self.btn_detect_ip.clicked.connect(self._detect_ip)
        row_ip.addWidget(self.btn_detect_ip)

        layout.addLayout(row_ip)
        ip_hint = QLabel("Р•СЃР»Рё С‚РµРєСѓС‰РёР№ IP СЃРѕРІРїР°РґР°РµС‚ СЃ РѕР¶РёРґР°РµРјС‹Рј вЂ” РІ СЃР°Р№РґР±Р°СЂРµ РѕС‚РѕР±СЂР°Р¶Р°РµС‚СЃСЏ Р·РµР»С‘РЅС‹Р№ РёРЅРґРёРєР°С‚РѕСЂ")
        ip_hint.setStyleSheet("font-size: 11px; color: #9ca3af; margin-left: 2px;")
        layout.addWidget(ip_hint)

        # --- РџСЂРѕРІР°Р№РґРµСЂС‹ (РєРѕРјРїР°РєС‚РЅС‹Рµ РєР°СЂС‚РѕС‡РєРё) ---
        providers_sep = QFrame()
        providers_sep.setFrameShape(QFrame.Shape.HLine)
        providers_sep.setStyleSheet("background: #e5e7eb; max-height: 1px; margin: 4px 0;")
        layout.addWidget(providers_sep)
        prov_label = QLabel("РџРћРЎРўРђР’Р©РРљР")
        prov_label.setStyleSheet("font-size: 13px; font-weight: 700; color: #1d1d1f; margin-top: 2px;")
        layout.addWidget(prov_label)

        # Emex
        self._add_provider_card(layout, "Emex", [
            ("login", "Р›РѕРіРёРЅ:", "text"),
            ("password", "РџР°СЂРѕР»СЊ:", "password"),
        ], check_method=self._check_emex, status_attr="emex_status")

        # Profit-League
        self._add_provider_card(layout, "Profit-League", [
            ("api_key", "API-РєР»СЋС‡:", "text"),
        ], check_method=self._check_pl, status_attr="pl_status")

        # РђРІС‚РѕСЃРѕСЋР·
        self._add_provider_card(layout, "РђРІС‚РѕСЃРѕСЋР·", [
            ("login", "Р›РѕРіРёРЅ:", "text"),
            ("password", "РџР°СЂРѕР»СЊ:", "password"),
        ], check_method=self._check_as, status_attr="as_status")

        # Armtek
        self._add_provider_card(layout, "Armtek", [
            ("login", "Р›РѕРіРёРЅ:", "text"),
            ("password", "РџР°СЂРѕР»СЊ:", "password"),
            ("vkorg", "VKORG:", "text"),
            ("kunnr", "KUNNR_RG:", "text"),
        ], check_method=self._check_armtek, status_attr="armtek_status")

        # Forum-Auto
        self._add_provider_card(layout, "Forum-Auto", [
            ("login", "Р›РѕРіРёРЅ:", "text"),
            ("password", "РџР°СЂРѕР»СЊ:", "password"),
        ], check_method=self._check_forum_auto, status_attr="forum_auto_status")

        # Mikado
        self._add_provider_card(layout, "Mikado", [
            ("login", "Р›РѕРіРёРЅ (РєРѕРґ РєР»РёРµРЅС‚Р°):", "text"),
            ("password", "РџР°СЂРѕР»СЊ:", "password"),
        ], check_method=self._check_mikado, status_attr="mikado_status")

        # ABSTD
        self._add_provider_card(layout, "ABSTD", [
            ("login", "Р›РѕРіРёРЅ:", "text"),
            ("password", "РџР°СЂРѕР»СЊ:", "password"),
            ("agreement_id", "ID РґРѕРіРѕРІРѕСЂР°:", "text"),
        ], check_method=self._check_abstd, status_attr="abstd_status")

        # --- РҐСЂР°РЅРёР»РёС‰Рµ ---
        self._add_section_header(layout, "РҐР РђРќРР›РР©Р•")
        storage_label = QLabel("в—Џ JSON С„Р°Р№Р»")
        storage_label.setStyleSheet("font-size: 12px; color: #374151;")
        layout.addWidget(storage_label)

        layout.addStretch()

        # --- Save button ---
        self.btn_save = QPushButton("РЎРѕС…СЂР°РЅРёС‚СЊ")
        self.btn_save.setMinimumHeight(38)
        self.btn_save.setStyleSheet("""
            QPushButton { background: #2563eb; color: white; font-size: 14px; font-weight: 700;
                          border-radius: 8px; border: none; }
            QPushButton:hover { background: #1d4ed8; }
            QPushButton:disabled { background: #9ca3af; }
        """)
        self.btn_save.clicked.connect(self._save)
        layout.addWidget(self.btn_save)

        scroll.setWidget(inner)
        outer.addWidget(scroll)

    # ============ РљРћРњРџРћРќР•РќРўР« ============

    def _add_section_header(self, layout, title):
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background: #e5e7eb; max-height: 1px; margin: 4px 0;")
        layout.addWidget(sep)
        label = QLabel(title)
        label.setStyleSheet("font-size: 13px; font-weight: 700; color: #1d1d1f; margin-top: 2px;")
        layout.addWidget(label)

    def _add_provider_card(self, layout, title, fields, check_method=None, status_attr=None):
        card = QWidget()
        card.setObjectName("providerCard")
        card.setStyleSheet("""
            QWidget#providerCard {
                background: #ffffff; border: 1px solid #e5e7eb; border-radius: 10px;
            }
        """)
        cv = QVBoxLayout(card)
        cv.setContentsMargins(0, 0, 0, 0)
        cv.setSpacing(0)

        # Р·Р°РіРѕР»РѕРІРѕРє + С‡РµРєР±РѕРєСЃ РІРєР»СЋС‡РµРЅРёСЏ
        hdr_row = QHBoxLayout()
        hdr_row.setContentsMargins(12, 6, 12, 2)
        hdr_row.setSpacing(6)

        enable_cb = QCheckBox(title)
        enable_cb.setStyleSheet("""
            QCheckBox { font-size: 12px; font-weight: 700; color: #1d1d1f; spacing: 6px; }
            QCheckBox::indicator { width: 36px; height: 20px; border-radius: 10px; border: none; background: #d1d5db; }
            QCheckBox::indicator:checked { background: #2563eb; }
        """)
        enable_cb.setChecked(True)
        hdr_row.addWidget(enable_cb)
        hdr_row.addStretch()
        cv.addLayout(hdr_row)

        # РїРѕР»СЏ
        field_widgets = {}
        for tag, label_text, field_type, *extra in fields:
            extra_args = extra[0] if extra else {}
            row = QHBoxLayout()
            row.setContentsMargins(12, 2, 12, 2)
            row.setSpacing(6)
            row.addWidget(QLabel(label_text))
            if field_type == "spin":
                w = QSpinBox()
                w.setRange(extra_args.get("min", 0), extra_args.get("max", 9999999))
            elif field_type == "password":
                w = QLineEdit()
                w.setEchoMode(QLineEdit.EchoMode.Password)
            else:
                w = QLineEdit()
            row.addWidget(w, 1)
            cv.addLayout(row)
            field_widgets[tag] = w

        # РєРЅРѕРїРєР° РїСЂРѕРІРµСЂРєРё + СЃС‚Р°С‚СѓСЃ
        if check_method:
            check_row = QHBoxLayout()
            check_row.setContentsMargins(12, 2, 12, 6)
            check_row.setSpacing(6)
            btn = QPushButton(f"РџСЂРѕРІРµСЂРёС‚СЊ {title}")
            btn.setFixedHeight(28)
            btn.setStyleSheet("""
                QPushButton { background: #e5e7eb; color: #374151; padding: 4px 14px; font-size: 11px;
                              font-weight: 600; border-radius: 6px; border: none; }
                QPushButton:hover { background: #d1d5db; }
            """)
            status_label = QLabel("")
            check_row.addWidget(btn)
            check_row.addWidget(status_label)
            check_row.addStretch()
            cv.addLayout(check_row)

            btn.clicked.connect(check_method)
            setattr(self, status_attr, status_label)
            self._check_buttons[title] = btn

        layout.addWidget(card)
        self._provider_fields[title] = field_widgets
        self._provider_enabled[title] = enable_cb

    def _fill_fields(self):
        # РѕР±С‰РёРµ
        self.default_comment.setText(self.settings_data.get("default_comment", ""))
        self.default_markup.setValue(self.settings_data.get("default_markup", 0))
        self.expected_ip.setText(self.settings_data.get("expected_ip", ""))
        # РїСЂРѕРІР°Р№РґРµСЂС‹
        mapping = {
            "Emex": "emex",
            "Profit-League": "profit_league",
            "РђРІС‚РѕСЃРѕСЋР·": "avtosoyuz",
            "Armtek": "armtek",
            "Forum-Auto": "forum_auto",
            "Mikado": "mikado",
            "ABSTD": "abstd",
        }
        for display_name, cfg_key in mapping.items():
            cfg = self.settings_data.get(cfg_key, {})
            cb = self._provider_enabled.get(display_name)
            if cb:
                cb.setChecked(cfg.get("enabled", True))
            widgets = self._provider_fields.get(display_name, {})
            for tag, w in widgets.items():
                val = cfg.get(tag, "")
                if isinstance(w, QSpinBox):
                    w.setValue(int(val) if val else 0)
                else:
                    w.setText(str(val) if val else "")

    # ============ РЎРўРђРўРЈРЎ ============

    def _set_status(self, label, ok, text=""):
        color = "#2e7d32" if ok else "#c62828"
        icon = "в—Џ" if ok else "в—Џ"
        label.setText(f"{icon} {text if text else ('OK' if ok else 'РћС€РёР±РєР°')}")
        label.setStyleSheet(f"font-size: 12px; color: {color}; font-weight: 600;")

    # ============ РџР РћР’Р•Р РљРђ EMEX ============

    def _check_emex(self):
        self.emex_status.setText("вЏі РџСЂРѕРІРµСЂРєР°...")
        self.emex_status.setStyleSheet("font-size: 12px; color: #f57c00; font-weight: 600;")
        self._run_check("emex", self._do_check_emex)

    def _do_check_emex(self):
        login = self._provider_fields["Emex"]["login"].value()
        password = self._provider_fields["Emex"]["password"].text()
        session = requests.Session()
        session.trust_env = False
        transport = Transport(session=session, timeout=10)
        client = zeep.Client(wsdl="http://ws.emex.ru/EmExService.asmx?WSDL", transport=transport)
        client.service.TestConnect("test")
        self._set_status(self.emex_status, True)
        self._enable_check("emex")

    # ============ РџР РћР’Р•Р РљРђ PROFIT-LEAGUE ============

    def _check_pl(self):
        self.pl_status.setText("вЏі РџСЂРѕРІРµСЂРєР°...")
        self.pl_status.setStyleSheet("font-size: 12px; color: #f57c00; font-weight: 600;")
        self._run_check("profit_league", self._do_check_pl)

    def _do_check_pl(self):
        key = self._provider_fields["Profit-League"]["api_key"].text()
        if not key:
            self._set_status(self.pl_status, False, "РљР»СЋС‡ РїСѓСЃС‚")
            self._enable_check("profit_league")
            return
        session = requests.Session()
        session.trust_env = False
        resp = session.get(
            "https://api.pr-lg.ru/search/warehouses",
            params={"secret": key, "action": "list"},
            timeout=10,
            proxies={"http": None, "https": None}
        )
        if resp.status_code == 200:
            self._set_status(self.pl_status, True)
        else:
            self._set_status(self.pl_status, False, f"HTTP {resp.status_code}")
        self._enable_check("profit_league")

    # ============ РџР РћР’Р•Р РљРђ РђР’РўРћРЎРћР®Р— ============

    def _check_as(self):
        self.as_status.setText("вЏі РџСЂРѕРІРµСЂРєР°...")
        self.as_status.setStyleSheet("font-size: 12px; color: #f57c00; font-weight: 600;")
        self._run_check("avtosoyuz", self._do_check_as)

    def _do_check_as(self):
        login = self._provider_fields["РђРІС‚РѕСЃРѕСЋР·"]["login"].text()
        password = self._provider_fields["РђРІС‚РѕСЃРѕСЋР·"]["password"].text()
        if not login or not password:
            self._set_status(self.as_status, False, "Р›РѕРіРёРЅ/РїР°СЂРѕР»СЊ РїСѓСЃС‚С‹")
            self._enable_check("avtosoyuz")
            return
        import base64
        creds = base64.b64encode(f"{login}:{password}".encode()).decode()
        headers = {
            "Authorization": f"Basic {creds}",
            "Accept": "application/json",
            "Content-type": "application/json"
        }
        session = requests.Session()
        session.trust_env = False
        resp = session.get(
            "https://api.xn--80aep1aarf3h.xn--p1ai/SearchService/GetBrands",
            params={"article": "test", "withoutTransit": "true"},
            headers=headers,
            timeout=10,
            proxies={"http": None, "https": None}
        )
        if resp.status_code == 200:
            self._set_status(self.as_status, True)
        elif resp.status_code == 401:
            self._set_status(self.as_status, False, "РќРµРІРµСЂРЅС‹Р№ Р»РѕРіРёРЅ/РїР°СЂРѕР»СЊ")
        else:
            self._set_status(self.as_status, False, f"HTTP {resp.status_code}")
        self._enable_check("avtosoyuz")

    # ============ РџР РћР’Р•Р РљРђ ARMTEK ============

    def _check_armtek(self):
        self.armtek_status.setText("вЏі РџСЂРѕРІРµСЂРєР°...")
        self.armtek_status.setStyleSheet("font-size: 12px; color: #f57c00; font-weight: 600;")
        self._run_check("armtek", self._do_check_armtek)

    def _do_check_armtek(self):
        login = self._provider_fields["Armtek"]["login"].text()
        password = self._provider_fields["Armtek"]["password"].text()
        if not login or not password:
            self._set_status(self.armtek_status, False, "Р›РѕРіРёРЅ/РїР°СЂРѕР»СЊ РїСѓСЃС‚С‹")
            self._enable_check("armtek")
            return
        import base64
        creds = base64.b64encode(f"{login}:{password}".encode()).decode()
        headers = {
            "Authorization": f"Basic {creds}",
            "Accept": "application/json",
        }
        try:
            session = requests.Session()
            session.trust_env = False
            resp = session.get(
                "https://ws.armtek.ru/api/ws_ping/ping?format=json",
                headers=headers,
                timeout=10,
                proxies={"http": None, "https": None}
            )
            if resp.status_code == 200:
                self._set_status(self.armtek_status, True)
            elif resp.status_code == 401:
                self._set_status(self.armtek_status, False, "РќРµРІРµСЂРЅС‹Р№ Р»РѕРіРёРЅ/РїР°СЂРѕР»СЊ")
            else:
                self._set_status(self.armtek_status, False, f"HTTP {resp.status_code}")
        except Exception as e:
            self._set_status(self.armtek_status, False, str(e)[:80])
        self._enable_check("armtek")

    # ============ РџР РћР’Р•Р РљРђ FORUM-AUTO ============

    def _check_forum_auto(self):
        self.forum_auto_status.setText("вЏі РџСЂРѕРІРµСЂРєР°...")
        self.forum_auto_status.setStyleSheet("font-size: 12px; color: #f57c00; font-weight: 600;")
        self._run_check("forum_auto", self._do_check_forum_auto)

    def _do_check_forum_auto(self):
        login = self._provider_fields["Forum-Auto"]["login"].text()
        password = self._provider_fields["Forum-Auto"]["password"].text()
        if not login or not password:
            self._set_status(self.forum_auto_status, False, "Р›РѕРіРёРЅ/РїР°СЂРѕР»СЊ РїСѓСЃС‚С‹")
            self._enable_check("forum_auto")
            return
        try:
            session = requests.Session()
            session.trust_env = False
            resp = session.get(
                "https://api.forum-auto.ru/v2/clientInfo",
                params={"login": login, "pass": password},
                timeout=10,
                proxies={"http": None, "https": None}
            )
            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, dict) and "error" in data:
                    self._set_status(self.forum_auto_status, False, "РћС€РёР±РєР° Р°РІС‚РѕСЂРёР·Р°С†РёРё")
                else:
                    self._set_status(self.forum_auto_status, True)
            else:
                self._set_status(self.forum_auto_status, False, f"HTTP {resp.status_code}")
        except Exception as e:
            self._set_status(self.forum_auto_status, False, str(e)[:80])
        self._enable_check("forum_auto")

    # ============ РџР РћР’Р•Р РљРђ MIKADO ============

    def _check_mikado(self):
        self.mikado_status.setText("вЏі РџСЂРѕРІРµСЂРєР°...")
        self.mikado_status.setStyleSheet("font-size: 12px; color: #f57c00; font-weight: 600;")
        self._run_check("mikado", self._do_check_mikado)

    def _do_check_mikado(self):
        login = self._provider_fields["Mikado"]["login"].text()
        password = self._provider_fields["Mikado"]["password"].text()
        if not login or not password:
            self._set_status(self.mikado_status, False, "Р›РѕРіРёРЅ/РїР°СЂРѕР»СЊ РїСѓСЃС‚С‹")
            self._enable_check("mikado")
            return
        try:
            import xml.etree.ElementTree as ET
            session = requests.Session()
            session.trust_env = False
            resp = session.post(
                "http://www.mikado-parts.ru/ws1/service.asmx/Get_MyIP",
                data={"ClientID": login, "Password": password},
                timeout=10,
                proxies={"http": None, "https": None}
            )
            if resp.status_code == 200:
                root = ET.fromstring(resp.content)
                ip = root.text.strip() if root.text else ""
                if ip:
                    self._set_status(self.mikado_status, True, f"IP: {ip}")
                else:
                    self._set_status(self.mikado_status, False, "РџСѓСЃС‚РѕР№ РѕС‚РІРµС‚")
            else:
                self._set_status(self.mikado_status, False, f"HTTP {resp.status_code}")
        except Exception as e:
            self._set_status(self.mikado_status, False, str(e)[:80])
        self._enable_check("mikado")

    # ============ РџР РћР’Р•Р РљРђ ABSTD ============

    def _check_abstd(self):
        self.abstd_status.setText("вЏі РџСЂРѕРІРµСЂРєР°...")
        self.abstd_status.setStyleSheet("font-size: 12px; color: #f57c00; font-weight: 600;")
        self._run_check("abstd", self._do_check_abstd)

    def _do_check_abstd(self):
        login = self._provider_fields["ABSTD"]["login"].text()
        password = self._provider_fields["ABSTD"]["password"].text()
        if not login or not password:
            self._set_status(self.abstd_status, False, "Р›РѕРіРёРЅ/РїР°СЂРѕР»СЊ РїСѓСЃС‚С‹")
            self._enable_check("abstd")
            return
        try:
            import hashlib
            pwd_hash = hashlib.md5(password.encode()).hexdigest().lower()
            auth = hashlib.md5((login + pwd_hash).encode()).hexdigest().lower()
            session = requests.Session()
            session.trust_env = False
            resp = session.get(
                "https://abstd.ru/api-get_user_context",
                params={"auth": auth, "format": "json"},
                timeout=10,
                proxies={"http": None, "https": None}
            )
            if resp.status_code == 200:
                data = resp.json()
                if data.get("status") == "OK":
                    agreements = data.get("user_agreements", [])
                    if agreements:
                        self._set_status(self.abstd_status, True, f"Р”РѕРіРѕРІРѕСЂРѕРІ: {len(agreements)}")
                    else:
                        self._set_status(self.abstd_status, True, "OK (Р±РµР· РґРѕРіРѕРІРѕСЂРѕРІ)")
                else:
                    self._set_status(self.abstd_status, False, data.get("status", "РћС€РёР±РєР°"))
            elif resp.status_code == 403:
                self._set_status(self.abstd_status, False, "РќРµРІРµСЂРЅС‹Р№ Р»РѕРіРёРЅ/РїР°СЂРѕР»СЊ")
            else:
                self._set_status(self.abstd_status, False, f"HTTP {resp.status_code}")
        except Exception as e:
            self._set_status(self.abstd_status, False, str(e)[:80])
        self._enable_check("abstd")

    # ============ Р’РЎРџРћРњРћР“РђРўР•Р›Р¬РќР«Р• Р”Р›РЇ РџР РћР’Р•Р РћРљ ============

    def _run_check(self, provider_name, do_check):
        title_map = {"emex": "Emex", "profit_league": "Profit-League", "avtosoyuz": "РђРІС‚РѕСЃРѕСЋР·", "armtek": "Armtek", "forum_auto": "Forum-Auto", "mikado": "Mikado", "abstd": "ABSTD"}
        btn = self._check_buttons.get(title_map.get(provider_name))
        if btn:
            btn.setEnabled(False)
        QTimer.singleShot(50, do_check)

    def _enable_check(self, provider_name):
        title_map = {"emex": "Emex", "profit_league": "Profit-League", "avtosoyuz": "РђРІС‚РѕСЃРѕСЋР·", "armtek": "Armtek", "forum_auto": "Forum-Auto", "mikado": "Mikado", "abstd": "ABSTD"}
        btn = self._check_buttons.get(title_map.get(provider_name))
        if btn:
            btn.setEnabled(True)

    # ============ РћРџР Р•Р”Р•Р›Р•РќРР• IP ============

    def _detect_ip(self):
        self.btn_detect_ip.setText("вЏі")
        self.btn_detect_ip.setEnabled(False)
        QTimer.singleShot(50, self._do_detect_ip)

    def _do_detect_ip(self):
        try:
            s = requests.Session()
            s.trust_env = False
            resp = s.get("https://api.ipify.org", timeout=5, proxies={"http": None, "https": None})
            if resp.status_code == 200:
                self.expected_ip.setText(resp.text.strip())
                self.btn_detect_ip.setText("РћРїСЂРµРґРµР»РёС‚СЊ")
            else:
                self._detect_ip_error()
        except:
            self._detect_ip_error()
        self.btn_detect_ip.setEnabled(True)

    def _detect_ip_error(self):
        self.btn_detect_ip.setText("вњ— РћС€РёР±РєР°")
        self.btn_detect_ip.setStyleSheet("""
            QPushButton { background: #fecaca; color: #dc2626; padding: 4px 12px; font-size: 11px;
                          font-weight: 600; border-radius: 6px; border: none; }
        """)
        QTimer.singleShot(1500, self._reset_detect_ip)

    def _reset_detect_ip(self):
        self.btn_detect_ip.setText("РћРїСЂРµРґРµР»РёС‚СЊ")
        self.btn_detect_ip.setStyleSheet("""
            QPushButton { background: #e5e7eb; color: #374151; padding: 4px 12px; font-size: 11px;
                          font-weight: 600; border-radius: 6px; border: none; }
            QPushButton:hover { background: #d1d5db; }
            QPushButton:disabled { background: #e5e7eb; color: #9ca3af; }
        """)

    # ============ РЎРћРҐР РђРќР•РќРР• ============

    def _save(self):
        data = {}
        mapping = {
            "Emex": "emex",
            "Profit-League": "profit_league",
            "РђРІС‚РѕСЃРѕСЋР·": "avtosoyuz",
            "Armtek": "armtek",
            "Forum-Auto": "forum_auto",
            "Mikado": "mikado",
            "ABSTD": "abstd",
        }
        for display_name, cfg_key in mapping.items():
            cfg = {}
            cb = self._provider_enabled.get(display_name)
            if cb:
                cfg["enabled"] = cb.isChecked()
            widgets = self._provider_fields.get(display_name, {})
            for tag, w in widgets.items():
                if isinstance(w, QSpinBox):
                    cfg[tag] = w.value()
                else:
                    cfg[tag] = w.text()
            data[cfg_key] = cfg

        data["default_markup"] = self.default_markup.value()
        data["default_comment"] = self.default_comment.text()
        data["expected_ip"] = self.expected_ip.text()
        self._write_settings(data)
        self.settings_data = data

        for btn in [self.btn_save_top, self.btn_save]:
            btn.setText("вњ“ РЎРѕС…СЂР°РЅРµРЅРѕ")
            btn.setStyleSheet("""
                QPushButton { background: #2e7d32; color: white; font-size: 14px; font-weight: 700;
                              border-radius: 8px; border: none; }
            """)
        QTimer.singleShot(2000, self._reset_save_buttons)
        self.saved.emit()

    def _reset_save_buttons(self):
        for btn in [self.btn_save_top, self.btn_save]:
            btn.setText("РЎРѕС…СЂР°РЅРёС‚СЊ")
            btn.setStyleSheet("""
                QPushButton { background: #2563eb; color: white; font-size: 14px; font-weight: 700;
                              border-radius: 8px; border: none; }
                QPushButton:hover { background: #1d4ed8; }
                QPushButton:disabled { background: #9ca3af; }
            """)

    def get_settings_data(self):
        return self.settings_data

