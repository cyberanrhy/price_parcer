import sys
import re
import threading
import datetime
import json
import os
import shutil
import requests
from PyQt6.QtCore import Qt, pyqtSignal, QRectF, QTimer, QUrl
from PyQt6.QtGui import QColor, QFont, QPainter, QPen, QDesktopServices

VERSION = "1.0.2"

from config_path import get_settings_path, get_history_path, get_config_dir
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QComboBox, QPushButton, QTableWidget,
                             QTableWidgetItem, QHeaderView, QLabel, QTextEdit,
                             QSpinBox, QMessageBox, QDoubleSpinBox, QCheckBox, QFrame,
                             QStackedWidget, QLineEdit, QSizePolicy, QStyledItemDelegate,
                             QStyleOptionViewItem, QStyle)
from PyQt6.QtCore import Qt, pyqtSignal, QRectF, QTimer
from PyQt6.QtGui import QColor, QFont, QPainter, QPen
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QComboBox, QPushButton, QTableWidget,
                             QTableWidgetItem, QHeaderView, QLabel, QTextEdit,
                             QSpinBox, QMessageBox, QDoubleSpinBox, QCheckBox, QFrame,
                             QStackedWidget, QLineEdit, QSizePolicy, QProgressBar,
                             QScrollArea)


class NumericTableWidgetItem(QTableWidgetItem):
    def __lt__(self, other):
        try:
            t1 = self.text().replace(' СЂ.', '').replace(' ', '').replace(',', '.')
            t2 = other.text().replace(' СЂ.', '').replace(' ', '').replace(',', '.')
            return float(t1) < float(t2)
        except:
            return super().__lt__(other)

try:
    from emex import EmexProvider
    from pr_lg import PrLgProvider
    from avtosoyuz import AvtosoyuzProvider
    from armtek import ArmtekProvider
    from forum_auto import ForumAutoProvider
    from mikado import MikadoProvider
    from abstd import AbstdProvider
    from settings_page import SettingsPage
except ImportError as e:
    print(f"РћС€РёР±РєР° РёРјРїРѕСЂС‚Р°: {e}")

class SkitchenApp(QMainWindow):
    results_ready = pyqtSignal(list)
    search_completed = pyqtSignal()
    provider_status = pyqtSignal(str, str)
    log_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int)
    ip_updated = pyqtSignal(str)

    def check_for_updates(self):
        try:
            # РџРѕР»СѓС‡Р°РµРј РґР°РЅРЅС‹Рµ Рѕ РїРѕСЃР»РµРґРЅРµРј СЂРµР»РёР·Рµ СЃ GitHub
            response = requests.get("https://api.github.com/repos/cyberanrhy/price_parcer/releases/latest", timeout=5)
            if response.status_code == 200:
                latest_tag = response.json()['tag_name'].replace('v', '') # РЈР±РёСЂР°РµРј 'v' РµСЃР»Рё РµСЃС‚СЊ
                
                if latest_tag > VERSION:
                    QMessageBox.information(
                        self, 
                        "Р”РѕСЃС‚СѓРїРЅРѕ РѕР±РЅРѕРІР»РµРЅРёРµ", 
                        f"Р’С‹С€Р»Р° РЅРѕРІР°СЏ РІРµСЂСЃРёСЏ: {latest_tag}.\nРџРѕР¶Р°Р»СѓР№СЃС‚Р°, СЃРєР°С‡Р°Р№С‚Рµ РµС‘ СЃ GitHub РґР»СЏ РїРѕР»СѓС‡РµРЅРёСЏ РёСЃРїСЂР°РІР»РµРЅРёР№."
                    )
        except Exception as e:
            # Р’ СЃР»СѓС‡Р°Рµ РѕС€РёР±РєРё СЃРµС‚Рё РїСЂРѕСЃС‚Рѕ РёРіРЅРѕСЂРёСЂСѓРµРј, С‡С‚РѕР±С‹ РЅРµ РјРµС€Р°С‚СЊ РїРѕР»СЊР·РѕРІР°С‚РµР»СЋ
            print(f"Update check failed: {e}")

    def __init__(self):
        super().__init__()
        self.setWindowTitle("РџСЂРѕС†РµРЅРєР° вЂ” Р¤РёРєСЃ Profit-League")
        self.resize(1300, 920)
        self.setMinimumSize(900, 600)
        self.setStyleSheet("""
            * { font-family: -apple-system, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif; }
            QMainWindow { background-color: #f5f5f7; }
            QLabel { color: #1d1d1f; }
        """)


        backup_dir = os.path.join(os.getcwd(), "backups")
        try:
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            for f in ["config/settings.json", "main.py", "settings_page.py"]:
                if os.path.exists(f):
                    shutil.copy2(f, os.path.join(backup_dir, os.path.basename(f) + ".backup_" + ts))
        except Exception:
            pass
        self.load_settings()
        
        # Р—Р°РїСѓСЃРє РїСЂРѕРІРµСЂРєРё РѕР±РЅРѕРІР»РµРЅРёР№ С‡РµСЂРµР· 2 СЃРµРєСѓРЅРґС‹ РїРѕСЃР»Рµ СЃС‚Р°СЂС‚Р°
        QTimer.singleShot(2000, self.check_for_updates)

        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # --- РЎРђР™Р”Р‘РђР  ---
        sidebar = QWidget()
        sidebar.setFixedWidth(180)
        sidebar.setStyleSheet("background: #ffffff; border-right: 1px solid #d2d2d7;")
        s = QVBoxLayout(sidebar)
        s.setContentsMargins(14, 18, 14, 18)
        s.setSpacing(12)

        title = QLabel("РџСЂРѕС†РµРЅРєР°")
        title.setStyleSheet("font-size: 20px; font-weight: 700; color: #1d1d1f; padding-bottom: 2px;")
        s.addWidget(title)

        # СЂР°Р·РґРµР»РёС‚РµР»СЊ РїРѕСЃР»Рµ Р·Р°РіРѕР»РѕРІРєР°
        top_sep = QFrame()
        top_sep.setFrameShape(QFrame.Shape.HLine)
        top_sep.setStyleSheet("background: #2563eb; max-height: 2px; margin: 2px 0 8px 0;")
        s.addWidget(top_sep)

        self.status_label = QLabel("")
        self.status_label.setStyleSheet("font-size: 11px; color: #9ca3af; padding-bottom: 4px;")
        s.addWidget(self.status_label)

        qty_label = QLabel("РљРѕР»-РІРѕ:")
        qty_label.setStyleSheet("font-size: 12px; color: #6b7280; font-weight: 600;")
        s.addWidget(qty_label)

        self.qty_spin = QSpinBox()
        self.qty_spin.setMinimum(1)
        self.qty_spin.setMaximum(9999)
        self.qty_spin.setValue(1)
        self.qty_spin.setStyleSheet("""
            padding: 6px; font-size: 14px; background: white; border: 2px solid #DCDFE6; border-radius: 8px;
        """)
        s.addWidget(self.qty_spin)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background: #e5e7eb; max-height: 1px;")
        s.addWidget(sep)

        self.markup_toggle = QCheckBox("РќР°С†РµРЅРєР°")
        self.markup_toggle.setStyleSheet("""
            QCheckBox { font-size: 13px; font-weight: 600; color: #374151; spacing: 8px; }
            QCheckBox::indicator { width: 40px; height: 22px; border-radius: 11px; border: none; background: #d1d5db; }
            QCheckBox::indicator:checked { background: #2563eb; }
            QCheckBox::indicator:disabled { background: #e5e7eb; }
        """)
        self.markup_toggle.toggled.connect(self.refresh_table_display)
        s.addWidget(self.markup_toggle)

        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setStyleSheet("background: #e5e7eb; max-height: 1px;")
        s.addWidget(sep2)

        # РєРѕРјРјРµРЅС‚Р°СЂРёР№ Рє Р·Р°РєР°Р·Сѓ
        comment_label = QLabel("РљРѕРјРјРµРЅС‚Р°СЂРёР№:")
        comment_label.setStyleSheet("font-size: 12px; color: #6b7280; font-weight: 600; margin-top: 2px;")
        s.addWidget(comment_label)

        self.cart_comment = QLineEdit()
        self.cart_comment.setPlaceholderText("РћРїС†РёРѕРЅР°Р»СЊРЅС‹Р№ РєРѕРјРјРµРЅС‚Р°СЂРёР№...")
        self.cart_comment.setStyleSheet("""
            padding: 6px; font-size: 13px; background: white; border: 2px solid #DCDFE6; border-radius: 8px;
        """)
        s.addWidget(self.cart_comment)

        sep3 = QFrame()
        sep3.setFrameShape(QFrame.Shape.HLine)
        sep3.setStyleSheet("background: #e5e7eb; max-height: 1px;")
        s.addWidget(sep3)

        self.btn_cart = QPushButton("Р’ РєРѕСЂР·РёРЅСѓ")
        self.btn_cart.setMinimumHeight(42)
        self.btn_cart.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cart.setStyleSheet("""
            QPushButton { background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                                        stop:0 #2563eb, stop:1 #1d4ed8);
                          color: white; font-size: 15px; font-weight: 700;
                          border-radius: 10px; border: none; padding: 12px; }
            QPushButton:hover { background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                                              stop:0 #3b82f6, stop:1 #2563eb); }
            QPushButton:pressed { padding-top: 14px; padding-bottom: 10px; }
            QPushButton:disabled { background: #9ca3af; }
        """)
        self.btn_cart.clicked.connect(self.add_to_cart)
        s.addWidget(self.btn_cart)

        # ----- РЎРўРђРўРЈРЎР« РџРћРЎРўРђР’Р©РРљРћР’ -----
        provider_card = QWidget()
        provider_card.setStyleSheet("""
            QWidget { background: #f8f9fa; border: 1px solid #e5e7eb; border-radius: 12px; }
        """)
        pc = QVBoxLayout(provider_card)
        pc.setContentsMargins(0, 0, 0, 0)
        pc.setSpacing(0)

        pheader = QLabel("  РџРћРЎРўРђР’Р©РРљР")
        pheader.setStyleSheet("font-size: 10px; color: #6b7280; font-weight: 700; background: transparent; padding: 8px 0 2px 12px; letter-spacing: 0.5px;")
        pc.addWidget(pheader)

        self.provider_rows = {}
        for pname, pcolor in [("Emex", "#0066cc"), ("Profit-League", "#2e7d32"), ("РђРІС‚РѕСЃРѕСЋР·", "#9ca3af"), ("Armtek", "#e65100"), ("Forum-Auto", "#7c3aed"), ("Mikado", "#d32f2f")]:
            row = QWidget()
            row.setStyleSheet("background: transparent;")
            rl = QHBoxLayout(row)
            rl.setContentsMargins(12, 3, 12, 3)
            rl.setSpacing(6)

            dot = QLabel("в—Џ")
            dot.setStyleSheet("font-size: 10px; color: #d1d5db; background: transparent;")

            nm = QLabel(pname)
            nm.setStyleSheet("font-size: 12px; color: #374151; background: transparent;")

            st = QLabel("вЏі")
            st.setStyleSheet("font-size: 11px; color: #9ca3af; background: transparent;")
            st.setAlignment(Qt.AlignmentFlag.AlignRight)

            rl.addWidget(dot)
            rl.addWidget(nm, 1)
            rl.addWidget(st)
            pc.addWidget(row)
            self.provider_rows[pname] = {"dot": dot, "status": st, "row": row, "name": nm}

        self._update_sidebar_providers()
        s.addWidget(provider_card)

        s.addStretch()

        # Р±Р»РѕРє РЅР°СЃС‚СЂРѕРµРє
        settings_card = QWidget()
        settings_card.setStyleSheet("""
            QWidget { background: #f8f9fa; border: 1px solid #e5e7eb; border-radius: 12px; }
        """)
        sc = QVBoxLayout(settings_card)
        sc.setContentsMargins(0, 0, 0, 0)
        sc.setSpacing(0)

        self.btn_settings = QPushButton()
        self.btn_settings.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_settings.setMinimumHeight(52)
        self.btn_settings.setStyleSheet("""
            QPushButton {
                background: transparent; color: #1d1d1f; padding: 12px 16px;
                font-size: 14px; font-weight: 700; border-radius: 12px; border: none; text-align: left;
            }
            QPushButton:hover { background: rgba(37, 99, 235, 0.08); color: #2563eb; }
            QPushButton:pressed { background: rgba(37, 99, 235, 0.14); }
        """)
        self.btn_settings.setText("вљ™  РќР°СЃС‚СЂРѕР№РєРё")
        self.btn_settings.clicked.connect(self.switch_to_settings)
        sc.addWidget(self.btn_settings)

        self.btn_help = QPushButton()
        self.btn_help.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_help.setMinimumHeight(52)
        self.btn_help.setStyleSheet("""
            QPushButton {
                background: transparent; color: #1d1d1f; padding: 12px 16px;
                font-size: 14px; font-weight: 700; border-radius: 12px; border: none; text-align: left;
            }
            QPushButton:hover { background: rgba(37, 99, 235, 0.08); color: #2563eb; }
            QPushButton:pressed { background: rgba(37, 99, 235, 0.14); }
        """)
        self.btn_help.setText("вќ“  РџРѕРјРѕС‰СЊ")
        self.btn_help.clicked.connect(self.switch_to_help)
        sc.addWidget(self.btn_help)
        
        s.addWidget(settings_card)

        # РљР»РёРєР°Р±РµР»СЊРЅР°СЏ РІРµСЂСЃРёСЏ
        self.version_btn = QPushButton(f"v{VERSION} В· GitHub")
        self.version_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.version_btn.setStyleSheet("""
            QPushButton { background: transparent; color: #6b7280; border: none; font-size: 12px; font-weight: 600; }
            QPushButton:hover { color: #2563eb; text-decoration: underline; }
        """)
        self.version_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/cyberanrhy/price_parcer")))
        s.addWidget(self.version_btn)


        # IP Р°РґСЂРµСЃ
        ip_card = QWidget()
        ip_card.setStyleSheet("""
            QWidget { background: #1e293b; border: 1px solid #334155; border-radius: 12px; }
        """)
        ip_card.setMinimumHeight(60)
        ip_inner = QHBoxLayout(ip_card)
        ip_inner.setContentsMargins(14, 10, 14, 10)
        ip_inner.setSpacing(10)

        self.ip_indicator = QLabel("в—‹")
        self.ip_indicator.setStyleSheet("font-size: 20px; color: #9ca3af; background: transparent;")

        ip_text_container = QVBoxLayout()
        ip_text_container.setContentsMargins(0, 0, 0, 0)
        ip_text_container.setSpacing(0)

        self.ip_label = QLabel("РћРїСЂРµРґРµР»РµРЅРёРµ...")
        self.ip_label.setStyleSheet("font-size: 16px; font-weight: 700; color: #f1f5f9; background: transparent; letter-spacing: 0.3px;")

        self.ip_hint = QLabel("С‚РµРєСѓС‰РёР№ IP")
        self.ip_hint.setStyleSheet("font-size: 10px; color: #64748b; background: transparent;")

        ip_text_container.addWidget(self.ip_label)
        ip_text_container.addWidget(self.ip_hint)

        ip_inner.addWidget(self.ip_indicator)
        ip_inner.addLayout(ip_text_container, 1)

        s.addWidget(ip_card)

        root.addWidget(sidebar)

        # --- QStackedWidget (РѕСЃРЅРѕРІРЅР°СЏ РѕР±Р»Р°СЃС‚СЊ + РЅР°СЃС‚СЂРѕР№РєРё) ---
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background: #f5f5f7;")
        self.stack.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # РЎС‚СЂР°РЅРёС†Р° 0: РїРѕРёСЃРє
        self.page_main = QWidget()
        self.page_main.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout = QVBoxLayout(self.page_main)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # 1. РџРћРРЎРљ
        srch = QHBoxLayout()
        self.search_combo = QComboBox()
        self.search_combo.setEditable(True)
        self.search_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.search_combo.lineEdit().setPlaceholderText("Р’РІРµРґРёС‚Рµ РёР»Рё РІС‹Р±РµСЂРёС‚Рµ РёР· РёСЃС‚РѕСЂРёРё...")
        self.search_combo.setStyleSheet("""
            QComboBox { padding: 10px; font-size: 16px; background: white; border: 2px solid #DCDFE6; border-radius: 8px; }
            QComboBox::drop-down { subcontrol-origin: padding; subcontrol-position: top right; width: 35px; border-left: 1px solid #DCDFE6; background: #F0F2F5; }
            QComboBox::down-arrow { border-left: 7px solid transparent; border-right: 7px solid transparent; border-top: 9px solid #555; }
        """)
        self.search_combo.lineEdit().returnPressed.connect(self.start_search)

        self.btn_search = QPushButton("РџР РћР¦Р•РќРРўР¬")
        self.btn_search.setMinimumHeight(44)
        self.btn_search.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_search.setStyleSheet("""
            QPushButton { background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                                                        stop:0 #d97706, stop:1 #b45309);
                          color: white; font-size: 15px; font-weight: 700; padding: 12px 30px;
                          border-radius: 10px; border: none; }
            QPushButton:hover { background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                                                              stop:0 #f59e0b, stop:1 #d97706); }
            QPushButton:pressed { padding-top: 14px; padding-bottom: 10px; }
            QPushButton:disabled { background: #9ca3af; }
        """)
        self.btn_search.clicked.connect(self.start_search)

        srch.addWidget(QLabel("РђР РўРРљРЈР›:"))
        srch.addWidget(self.search_combo, 4)
        srch.addWidget(self.btn_search, 1)
        layout.addLayout(srch)

        # 2. Р¤РР›Р¬РўР  РџРћ Р‘Р Р•РќР”РЈ
        flt = QHBoxLayout()
        flt.addWidget(QLabel("Р‘Р Р•РќР”:"))
        self.brand_filter = QComboBox()
        self.brand_filter.addItem("Р’СЃРµ Р±СЂРµРЅРґС‹")
        self.brand_filter.setStyleSheet("""
            padding: 8px; font-size: 13px; background: white; border: 2px solid #DCDFE6; border-radius: 8px;
        """)
        self.brand_filter.currentIndexChanged.connect(self.apply_brand_filter)
        flt.addWidget(self.brand_filter, 1)
        layout.addLayout(flt)

        # РёРЅРёС†РёР°Р»РёР·Р°С†РёСЏ С…СЂР°РЅРёР»РёС‰ РґР°РЅРЅС‹С… РґРѕ РїРѕРґРєР»СЋС‡РµРЅРёСЏ С„РёР»СЊС‚СЂРѕРІ
        self.all_data = []
        self.displayed_data = []

        # 2.1 Р§Р•РљР‘РћРљРЎ Р¤РР›Р¬РўР Рђ EMEX РџРћ РџРћРЎРўРђР’РљР•
        self.filter_emex_dp = QCheckBox("EMEX СЃ РїРѕСЃС‚Р°РІРєРѕР№ в‰Ґ50%")
        self.filter_emex_dp.setStyleSheet("font-size: 12px; color: #374151; spacing: 6px; margin-left: 2px;")
        self.filter_emex_dp.toggled.connect(self.apply_brand_filter)
        self.filter_emex_dp.setChecked(True)
        layout.addWidget(self.filter_emex_dp)

        # 2.2 РџР РћР“Р Р•РЎРЎ-Р‘РђР  РџРћРРЎРљРђ
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(16)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setStyleSheet("""
            QProgressBar { background: #e5e7eb; border: none; border-radius: 8px; margin: 4px 0;
                           color: white; font-size: 10px; font-weight: 700; text-align: center; }
            QProgressBar::chunk { background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                  stop:0 #2563eb, stop:1 #1d4ed8);
                                  border-radius: 8px; }
        """)
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)

        # 3. РўРђР‘Р›РР¦Рђ
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels(["РџРћРЎРўРђР’Р©РРљ", "Р‘Р Р•РќР”", "РђР РўРРљРЈР›", "Р¦Р•РќРђ", "РЎР РћРљ", "РџРћРЎРў.,%", "РљРћР›-Р’Рћ", "РЎРљР›РђР”", "РќРђР—Р’РђРќРР•"])
        self.table.setColumnWidth(0, 110)
        self.table.setColumnWidth(1, 120)
        self.table.setColumnWidth(2, 100)
        self.table.setColumnWidth(3, 90)
        self.table.setColumnWidth(4, 55)
        self.table.setColumnWidth(5, 65)
        self.table.setColumnWidth(6, 60)
        self.table.setColumnWidth(7, 80)
        self.table.horizontalHeader().setSectionResizeMode(8, QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setDefaultSectionSize(28)
        self.table.setSortingEnabled(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.table.itemSelectionChanged.connect(self.on_row_selected)
        layout.addWidget(self.table)

        # 4. Р›РћР“
        lh = QHBoxLayout()
        lh.addWidget(QLabel("Р–РЈР РќРђР› РЎРћР‘Р«РўРР™ (РћРўР›РђР”РљРђ):"))
        self.btn_copy_log = QPushButton("РљРћРџРР РћР’РђРўР¬ Р›РћР“")
        self.btn_copy_log.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_copy_log.setStyleSheet("""
            QPushButton { background: transparent; color: #2563eb; padding: 6px 16px; font-size: 12px;
                          font-weight: 600; border: 1.5px solid #d2d2d7; border-radius: 8px; }
            QPushButton:hover { background: #f3f4f6; border-color: #2563eb; }
        """)
        self.btn_copy_log.clicked.connect(self.copy_log_to_clipboard)
        lh.addStretch()
        lh.addWidget(self.btn_copy_log)
        layout.addLayout(lh)

        self.log_window = QTextEdit()
        self.log_window.setReadOnly(True)
        self.log_window.setFixedHeight(80)
        self.log_window.setStyleSheet("background: #1e293b; color: #f1f5f9; font-family: 'Consolas'; font-size: 11px;")
        layout.addWidget(self.log_window)

        self.stack.addWidget(self.page_main)  # index 0

        self.page_settings = SettingsPage()
        self.page_settings.back_requested.connect(self.switch_to_main)
        self.page_settings.saved.connect(self.on_settings_saved)
        self.stack.addWidget(self.page_settings)  # index 1

        # РЎС‚СЂР°РЅРёС†Р° 2: РїРѕРјРѕС‰СЊ
        self.page_help = self._build_help_page()
        self.stack.addWidget(self.page_help)  # index 2

        root.addWidget(self.stack)

        self.results_ready.connect(self.on_results_ready)
        self.search_completed.connect(self.on_search_completed)
        self.provider_status.connect(self.on_provider_status)
        self.log_signal.connect(self.add_log)
        self.progress_signal.connect(self.progress_bar.setValue)
        self.ip_updated.connect(self.on_ip_updated)
        QTimer.singleShot(300, self._fetch_ip)
        self.add_log("РЎРёСЃС‚РµРјР° РіРѕС‚РѕРІР°.")
        self.current_markup = 0
        self.load_history()
        self.apply_settings_to_ui()
        if self.first_run:
            QTimer.singleShot(200, self._show_welcome_dialog)

    def on_results_ready(self, data):
        self.all_data = data
        if data:
            self.all_data.sort(key=lambda x: float(x.get('price', 0)))
        self.apply_brand_filter()

    def on_search_completed(self):
        self.progress_bar.hide()
        self.btn_search.setEnabled(True)

    def on_ip_updated(self, ip):
        self.current_ip = ip
        matches = self.expected_ip and ip == self.expected_ip
        if matches:
            self.ip_indicator.setText("в—Џ")
            self.ip_indicator.setStyleSheet("font-size: 20px; color: #22c55e; background: transparent;")
            self.ip_label.setText(f"{ip}")
            self.ip_label.setStyleSheet("font-size: 16px; font-weight: 700; color: #22c55e; background: transparent; letter-spacing: 0.3px;")
            self.ip_hint.setText("IP СЃРѕРІРїР°РґР°РµС‚ вњ“")
            self.ip_hint.setStyleSheet("font-size: 10px; color: #22c55e; background: transparent;")
        elif ip == "РЅРµРґРѕСЃС‚СѓРїРµРЅ":
            self.ip_indicator.setText("в—Џ")
            self.ip_indicator.setStyleSheet("font-size: 20px; color: #ef4444; background: transparent;")
            self.ip_label.setText("РќРµРґРѕСЃС‚СѓРїРµРЅ")
            self.ip_label.setStyleSheet("font-size: 16px; font-weight: 700; color: #ef4444; background: transparent; letter-spacing: 0.3px;")
            self.ip_hint.setText("РїСЂРѕРІРµСЂСЊС‚Рµ РїРѕРґРєР»СЋС‡РµРЅРёРµ")
            self.ip_hint.setStyleSheet("font-size: 10px; color: #ef4444; background: transparent;")
        else:
            self.ip_indicator.setText("в—Џ")
            self.ip_indicator.setStyleSheet("font-size: 20px; color: #f59e0b; background: transparent;")
            self.ip_label.setText(f"{ip}")
            self.ip_label.setStyleSheet("font-size: 16px; font-weight: 700; color: #f59e0b; background: transparent; letter-spacing: 0.3px;")
            if self.expected_ip:
                self.ip_hint.setText(f"РѕР¶РёРґР°Р»СЃСЏ {self.expected_ip}")
                self.ip_hint.setStyleSheet("font-size: 10px; color: #f59e0b; background: transparent;")
            else:
                self.ip_hint.setText("С‚РµРєСѓС‰РёР№ IP (РЅРµ Р·Р°РґР°РЅ РѕР¶РёРґР°РµРјС‹Р№)")
                self.ip_hint.setStyleSheet("font-size: 10px; color: #94a3b8; background: transparent;")

    def _fetch_ip(self):
        def _run():
            try:
                import requests
                session = requests.Session()
                session.trust_env = False
                resp = session.get("https://api.ipify.org", timeout=5, proxies={"http": None, "https": None})
                ip = resp.text.strip() if resp.status_code == 200 else "РЅРµРґРѕСЃС‚СѓРїРµРЅ"
            except:
                ip = "РЅРµРґРѕСЃС‚СѓРїРµРЅ"
            self.ip_updated.emit(ip)
        threading.Thread(target=_run, daemon=True).start()

    def _show_welcome_dialog(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("Р”РѕР±СЂРѕ РїРѕР¶Р°Р»РѕРІР°С‚СЊ РІ РџСЂРѕС†РµРЅРєСѓ!")
        msg.setText(
            "Р”Р»СЏ СЂР°Р±РѕС‚С‹ СЃ РїСЂРѕРіСЂР°РјРјРѕР№ РЅРµРѕР±С…РѕРґРёРјРѕ РЅР°СЃС‚СЂРѕРёС‚СЊ РїРѕСЃС‚Р°РІС‰РёРєРѕРІ API.\n\n"
            "вЂў Emex вЂ” Р»РѕРіРёРЅ Рё РїР°СЂРѕР»СЊ РѕС‚ Р»РёС‡РЅРѕРіРѕ РєР°Р±РёРЅРµС‚Р°\n"
            "вЂў Profit-League вЂ” API-РєР»СЋС‡\n"
            "вЂў РђРІС‚РѕСЃРѕСЋР· вЂ” Р»РѕРіРёРЅ Рё РїР°СЂРѕР»СЊ\n"
            "вЂў Armtek вЂ” Р»РѕРіРёРЅ, РїР°СЂРѕР»СЊ, VKORG Рё KUNNR_RG\n"
            "вЂў Forum-Auto вЂ” Р»РѕРіРёРЅ Рё РїР°СЂРѕР»СЊ\n"
            "вЂў Mikado вЂ” Р»РѕРіРёРЅ (РєРѕРґ РєР»РёРµРЅС‚Р°) Рё РїР°СЂРѕР»СЊ\n\n"
            "вљ  Р’Р°Р¶РЅРѕ: IP РІР°С€РµРіРѕ РїРѕРґРєР»СЋС‡РµРЅРёСЏ РґРѕР»Р¶РµРЅ Р±С‹С‚СЊ\n"
            "Р·Р°СЂРµРіРёСЃС‚СЂРёСЂРѕРІР°РЅ Сѓ РєР°Р¶РґРѕРіРѕ РїРѕСЃС‚Р°РІС‰РёРєР°.\n\n"
            "РќР°Р¶РјРёС‚Рµ В«РќР°СЃС‚СЂРѕР№РєРёВ» РІ Р»РµРІРѕРј РјРµРЅСЋ Рё СѓРєР°Р¶РёС‚Рµ\n"
            "СЃРІРѕРё РґР°РЅРЅС‹Рµ, РїРѕСЃР»Рµ С‡РµРіРѕ СЃРѕС…СЂР°РЅРёС‚Рµ."
        )
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()

        # СЃРЅРёРјР°РµРј С„Р»Р°Рі РїРµСЂРІРѕРіРѕ Р·Р°РїСѓСЃРєР°
        import json as _json
        path = get_settings_path()
        self.add_log(f"РџС‹С‚Р°СЋСЃСЊ СЃРѕС…СЂР°РЅРёС‚СЊ РЅР°СЃС‚СЂРѕР№РєРё: {path}")
        try:
            with open(path, encoding="utf-8") as f:
                cfg = _json.load(f)
            cfg["first_run"] = False
            with open(path, "w", encoding="utf-8") as f:
                _json.dump(cfg, f, indent=2, ensure_ascii=False)
            self.add_log("Р¤Р»Р°Рі first_run СѓСЃРїРµС€РЅРѕ СѓСЃС‚Р°РЅРѕРІР»РµРЅ РІ False")
        except Exception as e:
            self.add_log(f"РћРЁРР‘РљРђ Р·Р°РїРёСЃРё РЅР°СЃС‚СЂРѕРµРє: {e}")
        self.first_run = False
        self.switch_to_settings()

    def on_provider_status(self, name, state):
        row = self.provider_rows.get(name)
        if not row:
            return
        if hasattr(self, 'enabled_map') and not self.enabled_map.get(name, True):
            return
        dot = row["dot"]
        st = row["status"]
        if state == "searching":
            dot.setStyleSheet("font-size: 10px; color: #2563eb; background: transparent;")
            st.setText("вџі")
            st.setStyleSheet("font-size: 12px; color: #2563eb; background: transparent;")
        elif state == "done":
            dot.setStyleSheet("font-size: 10px; color: #22c55e; background: transparent;")
            st.setText("вњ“")
            st.setStyleSheet("font-size: 12px; color: #22c55e; background: transparent;")
        elif state == "error":
            dot.setStyleSheet("font-size: 10px; color: #ef4444; background: transparent;")
            st.setText("вњ—")
            st.setStyleSheet("font-size: 12px; color: #ef4444; background: transparent;")
        else:
            dot.setStyleSheet("font-size: 10px; color: #d1d5db; background: transparent;")
            st.setText("вЏі")
            st.setStyleSheet("font-size: 11px; color: #9ca3af; background: transparent;")

    def _update_sidebar_providers(self):
        if not hasattr(self, 'provider_rows'):
            return
        for pname, row_data in self.provider_rows.items():
            enabled = self.enabled_map.get(pname, True) if hasattr(self, 'enabled_map') else True
            dot = row_data["dot"]
            nm = row_data["name"]
            st = row_data["status"]
            if enabled:
                nm.setStyleSheet("font-size: 12px; color: #374151; background: transparent;")
                dot.setStyleSheet("font-size: 10px; color: #d1d5db; background: transparent;")
                st.setText("вЏі")
                st.setStyleSheet("font-size: 11px; color: #9ca3af; background: transparent;")
            else:
                nm.setStyleSheet("font-size: 12px; color: #9ca3af; background: transparent;")
                dot.setStyleSheet("font-size: 10px; color: #e5e7eb; background: transparent;")
                st.setText("РѕС‚РєР»")
                st.setStyleSheet("font-size: 11px; color: #d1d5db; background: transparent;")

    # ============ РњР•РўРћР”Р« ============

    def load_settings(self):
        path = get_settings_path()
        _frozen = getattr(sys, 'frozen', False)
        default = {
            "emex": {"login": "", "password": ""},
            "profit_league": {"api_key": ""},
            "avtosoyuz": {"login": "", "password": ""},
            "armtek": {"login": "", "password": "", "vkorg": "", "kunnr": ""},
            "forum_auto": {"login": "", "password": ""},
            "mikado": {"login": "", "password": ""},
            "abstd": {"login": "", "password": "", "agreement_id": ""},
            "default_markup": 0,
            "default_comment": "",
            "expected_ip": "",
            "first_run": True
        }
        if _frozen:
            default["emex"]["enabled"] = False
            default["profit_league"]["enabled"] = False
        try:
            with open(path, encoding="utf-8") as f:
                cfg = json.load(f)
        except:
            cfg = default
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(default, f, indent=2, ensure_ascii=False)
        e = cfg.get("emex", {})
        p = cfg.get("profit_league", {})
        a = cfg.get("avtosoyuz", {})
        ar = cfg.get("armtek", {})
        fa = cfg.get("forum_auto", {})
        mk = cfg.get("mikado", {})
        self.providers = []
        if e.get("enabled", True):
            login_val = e.get("login", "")
            try:
                login_val = int(login_val)
            except:
                pass
            self.providers.append(
                EmexProvider(login_val, e.get("password", ""))
            )
        if p.get("enabled", True):
            self.providers.append(
                PrLgProvider(api_key=p.get("api_key", ""))
            )
        if a.get("enabled", True) and a.get("login") and a.get("password"):
            self.providers.append(
                AvtosoyuzProvider(a["login"], a["password"])
            )
        if ar.get("enabled", True) and ar.get("login") and ar.get("password") and ar.get("vkorg") and ar.get("kunnr"):
            self.providers.append(
                ArmtekProvider(ar["login"], ar["password"], ar["vkorg"], ar["kunnr"])
            )
        if fa.get("enabled", True) and fa.get("login") and fa.get("password"):
            self.providers.append(
                ForumAutoProvider(fa["login"], fa["password"])
            )
        if mk.get("enabled", True) and mk.get("login") and mk.get("password"):
            self.providers.append(
                MikadoProvider(mk["login"], mk["password"])
            )
        ab = cfg.get("abstd", {})
        if ab.get("enabled", True) and ab.get("login") and ab.get("password") and ab.get("agreement_id"):
            self.providers.append(
                AbstdProvider(ab["login"], ab["password"], ab["agreement_id"])
            )
        self.enabled_map = {
            "Emex": e.get("enabled", True),
            "Profit-League": p.get("enabled", True),
            "РђРІС‚РѕСЃРѕСЋР·": a.get("enabled", True) and bool(a.get("login") and a.get("password")),
            "Armtek": ar.get("enabled", True) and bool(ar.get("login") and ar.get("password") and ar.get("vkorg") and ar.get("kunnr")),
            "Forum-Auto": fa.get("enabled", True) and bool(fa.get("login") and fa.get("password")),
            "Mikado": mk.get("enabled", True) and bool(mk.get("login") and mk.get("password")),
            "ABSTD": ab.get("enabled", True) and bool(ab.get("login") and ab.get("password") and ab.get("agreement_id")),
        }
        self.current_markup = cfg.get("default_markup", 0)
        self.expected_ip = cfg.get("expected_ip", "")
        self.first_run = cfg.get("first_run", True)
        if hasattr(self, 'cart_comment'):
            self.cart_comment.setText(cfg.get("default_comment", ""))

    def apply_settings_to_ui(self):
        path = get_settings_path()
        try:
            with open(path, encoding="utf-8") as f:
                cfg = json.load(f)
        except:
            cfg = {}
        self.current_markup = cfg.get("default_markup", 0)
        if hasattr(self, 'markup_toggle'):
            self.markup_toggle.setChecked(self.current_markup > 0)
        if hasattr(self, 'cart_comment'):
            self.cart_comment.setText(cfg.get("default_comment", ""))

    def switch_to_main(self):
        self.stack.setCurrentIndex(0)

    def switch_to_settings(self):
        self.page_settings._fill_fields()
        self.stack.setCurrentIndex(1)

    def switch_to_help(self):
        self.stack.setCurrentIndex(2)

    def _build_help_page(self):
        page = QWidget()
        outer = QVBoxLayout(page)
        outer.setContentsMargins(20, 14, 20, 14)

        header = QHBoxLayout()
        btn_back = QPushButton("в†ђ РќР°Р·Р°Рґ")
        btn_back.setStyleSheet("""
            QPushButton { background: transparent; color: #2563eb; font-size: 13px; font-weight: 600;
                          border: none; padding: 4px 10px; }
            QPushButton:hover { color: #1d4ed8; }
        """)
        btn_back.clicked.connect(self.switch_to_main)
        header.addWidget(btn_back)
        header.addStretch()
        outer.addLayout(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: #f5f5f7; }")
        inner = QWidget()
        inner.setStyleSheet("background: white; border-radius: 12px; padding: 20px;")
        layout = QVBoxLayout(inner)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        def _hl(text, size=18, color="#1d1d1f"):
            lbl = QLabel(text)
            lbl.setWordWrap(True)
            lbl.setStyleSheet(f"font-size: {size}px; font-weight: 700; color: {color}; background: transparent;")
            return lbl

        def _p(text):
            lbl = QLabel(text)
            lbl.setWordWrap(True)
            lbl.setStyleSheet("font-size: 13px; color: #374151; background: transparent; line-height: 1.5;")
            return lbl

        def _sep():
            sep = QFrame()
            sep.setFrameShape(QFrame.Shape.HLine)
            sep.setStyleSheet("background: #e5e7eb; max-height: 1px;")
            return sep

        layout.addWidget(_hl("РџРѕРјРѕС‰СЊ", 22))
        layout.addWidget(_p(
            "РџСЂРѕРіСЂР°РјРјР° РІС‹РїРѕР»РЅСЏРµС‚ РїРѕРёСЃРє С†РµРЅ РЅР° Р°РІС‚РѕР·Р°РїС‡Р°СЃС‚Рё "
            "РїРѕ Р°СЂС‚РёРєСѓР»Сѓ РѕРґРЅРѕРІСЂРµРјРµРЅРЅРѕ Сѓ РІСЃРµС… РїРѕРґРєР»СЋС‡С‘РЅРЅС‹С… РїРѕСЃС‚Р°РІС‰РёРєРѕРІ. "
            "Р РµР·СѓР»СЊС‚Р°С‚С‹ РѕС‚РѕР±СЂР°Р¶Р°СЋС‚СЃСЏ РІ РѕР±С‰РµР№ С‚Р°Р±Р»РёС†Рµ."
        ))

        layout.addWidget(_sep())
        layout.addWidget(_hl("РќР°СЃС‚СЂРѕР№РєР°", 16))
        layout.addWidget(_p(
            "1. РќР°Р¶РјРёС‚Рµ В«РќР°СЃС‚СЂРѕР№РєРёВ» РІ Р±РѕРєРѕРІРѕРј РјРµРЅСЋ.\n"
            "2. Р—Р°РїРѕР»РЅРёС‚Рµ РґР°РЅРЅС‹Рµ РґР»СЏ РєР°Р¶РґРѕРіРѕ РїРѕСЃС‚Р°РІС‰РёРєР° (Р»РѕРіРёРЅ, РїР°СЂРѕР»СЊ, РєР»СЋС‡Рё).\n"
            "3. РќР°Р¶РјРёС‚Рµ В«РџСЂРѕРІРµСЂРёС‚СЊВ» вЂ” РµСЃР»Рё СЃРѕРµРґРёРЅРµРЅРёРµ СѓСЃРїРµС€РЅРѕ, РїРѕСЏРІРёС‚СЃСЏ Р·РµР»С‘РЅС‹Р№ СЃС‚Р°С‚СѓСЃ.\n"
            "4. РџРѕСЃС‚Р°РІСЊС‚Рµ РіР°Р»РѕС‡РєСѓ РЅР°РїСЂРѕС‚РёРІ Р°РєС‚РёРІРЅС‹С… РїРѕСЃС‚Р°РІС‰РёРєРѕРІ.\n"
            "5. РќР°Р¶РјРёС‚Рµ В«РЎРѕС…СЂР°РЅРёС‚СЊВ»."
        ))

        layout.addWidget(_sep())
        layout.addWidget(_hl("РћСЃРѕР±РµРЅРЅРѕСЃС‚Рё РїРѕСЃС‚Р°РІС‰РёРєРѕРІ", 16))

        providers_help = [
            ("Emex", "Р›РѕРіРёРЅ Рё РїР°СЂРѕР»СЊ РѕС‚ ws.emex.ru. "
                     "Р•СЃР»Рё РїСЂРѕС†РµРЅС‚ РїРѕСЃС‚Р°РІРєРё (DELIVERY%) РјРµРЅСЊС€Рµ 50%, "
                     "РїРѕР·РёС†РёСЏ СЃРєСЂС‹РІР°РµС‚СЃСЏ. Р¦РµРЅС‹ РѕС‚РѕР±СЂР°Р¶Р°СЋС‚СЃСЏ СЃ РЅР°С†РµРЅРєРѕР№."),
            ("Profit-League", "API-РєР»СЋС‡ РёР· Р»РёС‡РЅРѕРіРѕ РєР°Р±РёРЅРµС‚Р°. "
                              "РџРѕРёСЃРє РёРґС‘С‚ СЃРЅР°С‡Р°Р»Р° РїРѕ РѕСЂРёРіРёРЅР°Р»СЊРЅРѕРјСѓ Р°СЂС‚РёРєСѓР»Сѓ, "
                              "Р·Р°С‚РµРј РїРѕ РѕС‡РёС‰РµРЅРЅРѕРјСѓ. РљРѕСЂР·РёРЅР° С‡РµСЂРµР· POST /cart/add."),
            ("РђРІС‚РѕСЃРѕСЋР·", "Р›РѕРіРёРЅ Рё РїР°СЂРѕР»СЊ РѕС‚ Р»РёС‡РЅРѕРіРѕ РєР°Р±РёРЅРµС‚Р°. "
                         "РџРѕРёСЃРє С‡РµСЂРµР· GetBrands в†’ GetParts. "
                         "РўСЂРµР±СѓРµС‚СЃСЏ Р±РµР»С‹Р№ IP."),
            ("Armtek", "Р›РѕРіРёРЅ, РїР°СЂРѕР»СЊ, VKORG Рё KUNNR_RG. "
                       "Basic Auth. РџРѕРёСЃРє POST /ws_search/search. "
                       "РўСЂРµР±СѓРµС‚СЃСЏ Р±РµР»С‹Р№ IP."),
            ("Forum-Auto", "Р›РѕРіРёРЅ Рё РїР°СЂРѕР»СЊ РѕС‚ Р»РёС‡РЅРѕРіРѕ РєР°Р±РёРЅРµС‚Р°. "
                           "REST v2: /v2/listGoods + /v2/addGoodsToOrder. "
                           "Р›РёРјРёС‚ 2000 Р·Р°РїСЂРѕСЃРѕРІ/СЃСѓС‚РєРё."),
            ("Mikado", "РљРѕРґ РєР»РёРµРЅС‚Р° Рё РїР°СЂРѕР»СЊ. SOAP: service.asmx + basket.asmx. "
                       "CodeBrandStockInfo вЂ” Р±РµР· Р»РёРјРёС‚Р°. "
                       "РўСЂРµР±СѓРµС‚СЃСЏ Р±РµР»С‹Р№ IP. Р’РєР»СЋС‡РёС‚СЊ РґРѕСЃС‚СѓРї РЅР° ws_panel.asp."),
            ("ABSTD", "Р›РѕРіРёРЅ Рё РїР°СЂРѕР»СЊ РѕС‚ СЃР°Р№С‚Р° abstd.ru. "
                      "REST, auth: md5(login + md5(password)). "
                      "РџРѕРёСЃРє + РєРѕСЂР·РёРЅР° С‡РµСЂРµР· api-search / api-cart_add. "
                      "РўСЂРµР±СѓРµС‚СЃСЏ agreement_id РёР· Р›Рљ. Р‘РµР»С‹Р№ IP."),
        ]

        for name, desc in providers_help:
            row = QHBoxLayout()
            row.setSpacing(10)
            n = QLabel(name)
            n.setStyleSheet("font-size: 13px; font-weight: 700; color: #1d1d1f; "
                            "background: transparent; min-width: 120px;")
            n.setAlignment(Qt.AlignmentFlag.AlignTop)
            d = QLabel(desc)
            d.setWordWrap(True)
            d.setStyleSheet("font-size: 13px; color: #374151; background: transparent;")
            row.addWidget(n)
            row.addWidget(d, 1)
            layout.addLayout(row)

        layout.addWidget(_sep())
        layout.addWidget(_hl("IP-Р°РґСЂРµСЃ", 16))
        layout.addWidget(_p(
            "Р’СЃРµ РїРѕСЃС‚Р°РІС‰РёРєРё С‚СЂРµР±СѓСЋС‚, С‡С‚РѕР±С‹ Р·Р°РїСЂРѕСЃС‹ С€Р»Рё СЃ IP-Р°РґСЂРµСЃР°, "
            "Р·Р°СЂРµРіРёСЃС‚СЂРёСЂРѕРІР°РЅРЅРѕРіРѕ РІ РёС… СЃРёСЃС‚РµРјРµ. "
            "Р’ РЅР°СЃС‚СЂРѕР№РєР°С… РјРѕР¶РЅРѕ СѓРєР°Р·Р°С‚СЊ РѕР¶РёРґР°РµРјС‹Р№ IP вЂ” РїСЂРѕРіСЂР°РјРјР° "
            "Р±СѓРґРµС‚ СЃРІРµСЂСЏС‚СЊ С‚РµРєСѓС‰РёР№ IP Рё РїРѕРєР°Р·С‹РІР°С‚СЊ СЃРѕРІРїР°РґРµРЅРёРµ РІ Р±РѕРєРѕРІРѕР№ РїР°РЅРµР»Рё."
        ))

        layout.addWidget(_sep())
        layout.addWidget(_hl("РќР°С†РµРЅРєР°", 16))
        layout.addWidget(_p(
            "Р’ РїРѕР»Рµ В«РќР°С†РµРЅРєР° %В» Р·Р°РґР°С‘С‚СЃСЏ РїСЂРѕС†РµРЅС‚, "
            "РЅР° РєРѕС‚РѕСЂС‹Р№ СѓРІРµР»РёС‡РёРІР°СЋС‚СЃСЏ С†РµРЅС‹ РІ С‚Р°Р±Р»РёС†Рµ. "
            "РќР°С†РµРЅРєР° РґРµР№СЃС‚РІСѓРµС‚ С‚РѕР»СЊРєРѕ РЅР° РѕС‚РѕР±СЂР°Р¶РµРЅРёРµ, "
            "РІ РєРѕСЂР·РёРЅСѓ СѓС…РѕРґРёС‚ РѕСЂРёРіРёРЅР°Р»СЊРЅР°СЏ С†РµРЅР° РїРѕСЃС‚Р°РІС‰РёРєР°."
        ))

        layout.addStretch()
        scroll.setWidget(inner)
        outer.addWidget(scroll)
        return page

    def on_settings_saved(self):

        backup_dir = os.path.join(os.getcwd(), "backups")
        try:
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            for f in ["config/settings.json", "main.py", "settings_page.py"]:
                if os.path.exists(f):
                    shutil.copy2(f, os.path.join(backup_dir, os.path.basename(f) + ".backup_" + ts))
        except Exception:
            pass
        self.load_settings()
        self._update_sidebar_providers()
        if self.displayed_data:
            self.refresh_table_display()
        self.add_log("РќР°СЃС‚СЂРѕР№РєРё СЃРѕС…СЂР°РЅРµРЅС‹, РїСЂРѕРІР°Р№РґРµСЂС‹ РѕР±РЅРѕРІР»РµРЅС‹")
        if hasattr(self, 'current_ip'):
            self.on_ip_updated(self.current_ip)
        self.switch_to_main()

    def copy_log_to_clipboard(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.log_window.toPlainText())
        self.add_log(">>> РўРµРєСЃС‚ Р»РѕРіР° СЃРєРѕРїРёСЂРѕРІР°РЅ РІ Р±СѓС„РµСЂ РѕР±РјРµРЅР°!")

    def add_log(self, text):
        time_str = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_window.append(f"[{time_str}] {text}")
        self.log_window.ensureCursorVisible()

    def clean_num(self, text):
        if not text: return ""
        return re.sub(r'[^A-Z0-9]', '', str(text).upper())

    @property
    def _history_path(self):
        return get_history_path()

    def load_history(self):
        try:
            with open(self._history_path, encoding="utf-8") as f:
                items = json.load(f)
            if isinstance(items, list):
                for art in items[:20]:
                    self.search_combo.addItem(str(art))
        except:
            pass

    def save_history(self, article):
        article = article.strip().upper()
        if not article:
            return
        try:
            items = []
            try:
                with open(self._history_path, encoding="utf-8") as f:
                    items = json.load(f)
            except:
                pass
            if not isinstance(items, list):
                items = []
            if article in items:
                items.remove(article)
            items.insert(0, article)
            items = items[:20]
            with open(self._history_path, "w", encoding="utf-8") as f:
                json.dump(items, f, ensure_ascii=False)
        except:
            pass

    def update_history(self, art):
        art = art.strip().upper()
        if not art: return
        self.save_history(art)
        items = [self.search_combo.itemText(i) for i in range(self.search_combo.count())]
        if art in items: items.remove(art)
        items.insert(0, art)
        self.search_combo.clear()
        self.search_combo.addItems(items[:5])
        self.search_combo.setCurrentText(art)

    def start_search(self):
        raw_article = self.search_combo.currentText().strip()
        if not raw_article: return
        self.update_history(raw_article)
        clean_article = self.clean_num(raw_article)
        self.btn_search.setEnabled(False)
        self.table.setRowCount(0)
        self.progress_bar.setValue(0)
        self.progress_bar.show()
        for name in self.provider_rows:
            self.on_provider_status(name, "waiting")
        threading.Thread(target=self.run_query, args=(raw_article, clean_article), daemon=True).start()

    def run_query(self, raw_article, clean_article):
        all_results = []
        total = len(self.providers)
        name_map = {"EmexProvider": "Emex", "PrLgProvider": "Profit-League", "AvtosoyuzProvider": "РђРІС‚РѕСЃРѕСЋР·", "ArmtekProvider": "Armtek", "ForumAutoProvider": "Forum-Auto", "MikadoProvider": "Mikado", "AbstdProvider": "ABSTD"}
        try:
            for i, provider in enumerate(self.providers):
                cls_name = provider.__class__.__name__
                display_name = name_map.get(cls_name, cls_name)
                self.log_signal.emit(f"Р—Р°РїСЂРѕСЃ {display_name}...")
                self.provider_status.emit(display_name, "searching")
                try:
                    import time as _time
                    t0 = _time.time()
                    if cls_name == "PrLgProvider":
                        res = provider.get_prices_parallel(raw_article, clean_article)
                    else:
                        res = provider.get_prices(clean_article)
                    elapsed = _time.time() - t0
                    if res:
                        for item in res:
                            if "article" not in item or not item["article"]:
                                item["article"] = raw_article
                            res_art_clean = self.clean_num(item.get('article', ''))
                            if not res_art_clean or res_art_clean == clean_article:
                                all_results.append(item)
                        self.log_signal.emit(f"{display_name}: {len(res)} Р·Р° {elapsed:.1f}СЃ")
                    else:
                        self.log_signal.emit(f"{display_name}: РїСѓСЃС‚Рѕ Р·Р° {elapsed:.1f}СЃ")
                    self.provider_status.emit(display_name, "done")
                except Exception as e:
                    self.log_signal.emit(f"РћРЁРР‘РљРђ {display_name}: {str(e)}")
                    self.provider_status.emit(display_name, "error")
                self.progress_signal.emit(int((i + 1) / total * 100))
                self.results_ready.emit(list(all_results))
            self.search_completed.emit()
        except Exception as e:
            self.log_signal.emit(f"РљР РРўРР§Р•РЎРљРђРЇ РћРЁРР‘РљРђ: {str(e)}")
            self.results_ready.emit([])
            self.search_completed.emit()

    def update_table(self, data):
        self.displayed_data = data
        self.table.setRowCount(len(data))

        emex_bg = "#e8f4fd"
        pl_bg = "#e8f8e8"
        warehouse_colors = ["#1a237e", "#00695c", "#e65100", "#4a148c", "#01579b", "#33691e"]

        for row, item in enumerate(data):
            provider = str(item["provider"])

            self.table.setItem(row, 0, QTableWidgetItem(provider))
            self.table.setItem(row, 1, QTableWidgetItem(str(item["brand"])))
            self.table.setItem(row, 2, QTableWidgetItem(str(item.get("article", ""))))
            # Р¦Р•РќРђ СЃ СѓС‡С‘С‚РѕРј РЅР°С†РµРЅРєРё
            orig_price = float(item["price"])
            markup_val = self.current_markup if self.markup_toggle.isChecked() else 0
            display_price = orig_price * (1 + markup_val / 100)
            self.table.setItem(row, 3, NumericTableWidgetItem(f"{display_price:.2f} СЂ."))
            self.table.setItem(row, 4, NumericTableWidgetItem(str(item["days"])))
            # РџРћРЎРў.,% вЂ” С†РІРµС‚РЅРѕР№ РєСЂСѓР¶РѕРє + РїСЂРѕС†РµРЅС‚
            dp_raw = item.get("delivery_percent", "")
            if dp_raw != "" and provider == "EMEX":
                try:
                    dp_val = float(dp_raw)
                except:
                    dp_val = 0
                if dp_val >= 95:
                    dp_color = "#2e7d32"
                elif dp_val >= 80:
                    dp_color = "#f57c00"
                else:
                    dp_color = "#c62828"
                dp_text = f"в—Џ {int(dp_val)}%"
            else:
                dp_color = "#9ca3af"
                dp_text = "вЂ”"

            dp_cell = QTableWidgetItem(dp_text)
            dp_cell.setForeground(QColor(dp_color))
            dp_cell.setFont(QFont("", -1, 700))
            self.table.setItem(row, 5, dp_cell)
            # РєРѕР»-РІРѕ СЃ РєСЂР°С‚РЅРѕСЃС‚СЊСЋ
            qty = str(item["quantity"])
            mult = int(item.get("multiplicity", 1))
            display_qty = f"{qty} (РєСЂ. {mult})" if mult > 1 else qty
            self.table.setItem(row, 6, QTableWidgetItem(display_qty))
            self.table.setItem(row, 7, QTableWidgetItem(str(item.get("logo", "-"))))
            self.table.setItem(row, 8, QTableWidgetItem(str(item["name"])))

            for col in range(self.table.columnCount()):
                cell = self.table.item(row, col)
                if not cell:
                    continue

                if provider == "EMEX":
                    bg = "#edf5fd" if row % 2 == 1 else "#f5faff"
                elif provider == "Profit-League":
                    bg = "#eef9ee" if row % 2 == 1 else "#f5fcf5"
                else:
                    bg = "#ffffff" if row % 2 == 0 else "#f9f9f9"

                cell.setBackground(QColor(bg))

                if col == 0:
                    if provider == "EMEX":
                        cell.setForeground(QColor("#0066cc"))
                    else:
                        cell.setForeground(QColor("#2e7d32"))

            # РЎР РћРљ
            days_cell = self.table.item(row, 4)
            if days_cell:
                try:
                    days_val = int(str(item.get("days", "999")))
                except:
                    days_val = 999
                if days_val <= 1:
                    days_cell.setForeground(QColor("#2e7d32"))
                elif days_val <= 5:
                    days_cell.setForeground(QColor("#f57c00"))
                else:
                    days_cell.setForeground(QColor("#c62828"))

            # РџРћРЎРў.,%
            dp_cell = self.table.item(row, 5)
            if dp_cell and provider == "EMEX":
                try:
                    dp_val = float(item.get("delivery_percent", 0))
                except:
                    dp_val = 0
                if dp_val >= 95:
                    dp_cell.setForeground(QColor("#2e7d32"))
                elif dp_val >= 80:
                    dp_cell.setForeground(QColor("#f57c00"))
                else:
                    dp_cell.setForeground(QColor("#c62828"))
                dp_cell.setFont(QFont("", -1, 700))

            # РљРћР›-Р’Рћ
            qty_cell = self.table.item(row, 6)
            if qty_cell:
                try:
                    qty_val = int(re.sub(r'\D', '', str(item.get("quantity", "0")))) if re.sub(r'\D', '', str(item.get("quantity", "0"))) else 0
                except:
                    qty_val = 0
                if qty_val <= 0:
                    qty_cell.setForeground(QColor("#d32f2f"))
                    qty_cell.setFont(QFont("", -1, 700))
                elif qty_val <= 3:
                    qty_cell.setForeground(QColor("#f57c00"))
                    qty_cell.setFont(QFont("", -1, 700))
                else:
                    qty_cell.setForeground(QColor("#2e7d32"))

            # РЎРљР›РђР”
            wh_cell = self.table.item(row, 7)
            if wh_cell and provider == "Profit-League":
                wh_name = str(item.get("logo", ""))
                color_idx = abs(hash(wh_name)) % len(warehouse_colors)
                wh_cell.setForeground(QColor(warehouse_colors[color_idx]))
                wh_cell.setFont(QFont("", -1, 700))

            # Р¦Р•РќРђ
            price_cell = self.table.item(row, 3)
            if price_cell:
                if markup_val > 0:
                    price_cell.setForeground(QColor("#f57c00"))
                    price_cell.setFont(QFont("", -1, 700))
                else:
                    price_cell.setForeground(QColor("#1a237e"))
                    price_cell.setFont(QFont(""))

        self.brand_filter.blockSignals(True)
        current = self.brand_filter.currentText()
        self.brand_filter.clear()
        self.brand_filter.addItem("Р’СЃРµ Р±СЂРµРЅРґС‹")
        brands = sorted(set(str(item.get("brand", "")).strip() for item in data if item.get("brand", "").strip()))
        for b in brands:
            self.brand_filter.addItem(b)
        idx = self.brand_filter.findText(current)
        if idx >= 0:
            self.brand_filter.setCurrentIndex(idx)
        self.brand_filter.blockSignals(False)

    def refresh_table_display(self):
        if self.displayed_data:
            self.update_table(self.displayed_data)

    def on_row_selected(self):
        row = self.table.currentRow()
        if row < 0 or row >= len(self.displayed_data):
            self.qty_spin.setMaximum(9999)
            self.qty_spin.setValue(1)
            self.qty_spin.setSingleStep(1)
            self.qty_spin.setMinimum(1)
            self.btn_cart.setText("Р’ РєРѕСЂР·РёРЅСѓ")
            self.status_label.setText("")
            return

        item = self.displayed_data[row]
        stock_qty = str(item.get("quantity", "0"))
        try:
            stock_num = int(re.sub(r'\D', '', stock_qty)) if re.sub(r'\D', '', stock_qty) else 0
        except:
            stock_num = 0

        limit = max(1, stock_num)
        self.qty_spin.setMaximum(limit)
        self.qty_spin.setValue(1)
        # С€Р°Рі РїРѕ РєСЂР°С‚РЅРѕСЃС‚Рё
        mult = int(item.get("multiplicity", 1))
        self.qty_spin.setSingleStep(mult)
        self.qty_spin.setMinimum(mult)

        provider = item.get("provider", "")
        if provider == "EMEX":
            self.btn_cart.setText("Р’ РєРѕСЂР·РёРЅСѓ Emex")
        elif provider == "Profit-League":
            self.btn_cart.setText("Р’ РєРѕСЂР·РёРЅСѓ Profit-League")
        elif provider == "РђРІС‚РѕСЃРѕСЋР·":
            self.btn_cart.setText("Р’ РєРѕСЂР·РёРЅСѓ РђРІС‚РѕСЃРѕСЋР·")
        elif provider == "Armtek":
            self.btn_cart.setText("Р’ РєРѕСЂР·РёРЅСѓ Armtek")
        elif provider == "ABSTD":
            self.btn_cart.setText("Р’ РєРѕСЂР·РёРЅСѓ ABSTD")
        else:
            self.btn_cart.setText("Р’ РєРѕСЂР·РёРЅСѓ")

        if stock_num > 0:
            self.status_label.setText(f"Р”РѕСЃС‚СѓРїРЅРѕ: {stock_num} С€С‚.")
        else:
            self.status_label.setText("РќРµС‚ РІ РЅР°Р»РёС‡РёРё")

    def apply_brand_filter(self):
        if not hasattr(self, 'table') or not hasattr(self, 'all_data'):
            return
        base = self.all_data

        # С„РёР»СЊС‚СЂ РїРѕ РїСЂРѕС†РµРЅС‚Сѓ РїРѕСЃС‚Р°РІРєРё
        if self.filter_emex_dp.isChecked():
            base = [item for item in base if item.get("provider") != "EMEX" or float(item.get("delivery_percent", 0)) >= 50]

        brand = self.brand_filter.currentText()
        if not brand or brand == "Р’СЃРµ Р±СЂРµРЅРґС‹":
            self.update_table(base)
        else:
            filtered = [item for item in base if item.get("brand", "").strip() == brand]
            self.update_table(filtered)

    def add_to_cart(self):
        row = self.table.currentRow()
        if row < 0:
            self.add_log("РћРЁРР‘РљРђ: РЅРµ РІС‹Р±СЂР°РЅР° РїРѕР·РёС†РёСЏ РІ С‚Р°Р±Р»РёС†Рµ")
            return

        if row >= len(self.displayed_data):
            self.add_log("РћРЁРР‘РљРђ: СЃС‚СЂРѕРєР° РІРЅРµ РґРёР°РїР°Р·РѕРЅР° РґР°РЅРЅС‹С…")
            return

        item = dict(self.displayed_data[row])
        qty = self.qty_spin.value()

        stock_qty = str(item.get("quantity", "0"))
        try:
            stock_num = int(re.sub(r'\D', '', stock_qty)) if re.sub(r'\D', '', stock_qty) else 0
        except:
            stock_num = 0

        if stock_num > 0 and qty > stock_num:
            reply = QMessageBox.question(self, "РљРѕР»РёС‡РµСЃС‚РІРѕ",
                f"РќР° СЃРєР»Р°РґРµ С‚РѕР»СЊРєРѕ {stock_num} С€С‚. Р”РѕР±Р°РІРёС‚СЊ {qty} С€С‚.?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply != QMessageBox.StandardButton.Yes:
                return

        provider_name = item.get("provider", "")
        provider_obj = None
        for p in self.providers:
            if (provider_name == "EMEX" and isinstance(p, EmexProvider)) or \
               (provider_name == "Profit-League" and isinstance(p, PrLgProvider)) or \
               (provider_name == "РђРІС‚РѕСЃРѕСЋР·" and isinstance(p, AvtosoyuzProvider)) or \
               (provider_name == "Armtek" and isinstance(p, ArmtekProvider)) or \
               (provider_name == "Forum-Auto" and isinstance(p, ForumAutoProvider)) or \
               (provider_name == "Mikado" and isinstance(p, MikadoProvider)) or \
               (provider_name == "ABSTD" and isinstance(p, AbstdProvider)):
                provider_obj = p
                break

        if not provider_obj:
            self.add_log(f"РћРЁРР‘РљРђ: РїРѕСЃС‚Р°РІС‰РёРє {provider_name} РЅРµ РЅР°Р№РґРµРЅ")
            return

        if provider_name == "Profit-League":
            pid = item.get("article_id", "")
            wid = item.get("warehouse_id", "")
            if not pid or not wid:
                self.add_log(f"РћРЁРР‘РљРђ: article_id={pid}, warehouse_id={wid} вЂ” РЅРµ С…РІР°С‚Р°РµС‚ РґР°РЅРЅС‹С… РґР»СЏ РєРѕСЂР·РёРЅС‹")
                return

        self.add_log(f"Р”РѕР±Р°РІР»РµРЅРёРµ {item.get('article','')} x{qty} РІ РєРѕСЂР·РёРЅСѓ {provider_name}...")
        self.btn_cart.setEnabled(False)
        comment = self.cart_comment.text()
        threading.Thread(target=self._add_to_cart_thread, args=(provider_obj, item, qty, comment), daemon=True).start()

    def _add_to_cart_thread(self, provider, item, qty, comment=""):
        try:
            result = provider.add_to_basket(item, quantity=qty, comment=comment)
            if result.get("success"):
                self.log_signal.emit(f"РЈРЎРџР•РҐ: {result.get('data', 'OK')}")

            else:
                self.log_signal.emit(f"РћРЁРР‘РљРђ: {result.get('error', 'РЅРµРёР·РІРµСЃС‚РЅР°СЏ РѕС€РёР±РєР°')}")

        except Exception as e:
            self.log_signal.emit(f"РћРЁРР‘РљРђ: {str(e)}")
        finally:
            self.log_signal.emit("Р“РѕС‚РѕРІРѕ.")
            self.btn_cart.setEnabled(True)

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = SkitchenApp()
    window.show()
    sys.exit(app.exec())
