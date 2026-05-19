import os
import sys

APP_NAME = "Проценка"


def get_config_dir():
    """Возвращает путь к папке конфигурации.
    Для .exe: %APPDATA%\\Проценка\\
    Для скрипта: папка проекта\\config\\
    """
    if getattr(sys, 'frozen', False):
        # Запуск из .exe — используем AppData
        base = os.environ.get('APPDATA', os.path.expanduser('~'))
        path = os.path.join(base, APP_NAME)
    else:
        # Запуск из скрипта — используем config/ рядом с проектом
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config")
    os.makedirs(path, exist_ok=True)
    return path


def get_settings_path():
    return os.path.join(get_config_dir(), "settings.json")


def get_history_path():
    return os.path.join(get_config_dir(), "history.json")
