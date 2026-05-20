#!/usr/bin/env python3
"""
Скрипт для создания и восстановления бэкапов файлов
"""

import shutil
import os
import sys
from datetime import datetime
import argparse


def backup_file(filepath):
    """Создание бэкапа файла"""
    if not os.path.exists(filepath):
        print(f"Ошибка: файл {filepath} не существует")
        return False

    filepath = os.path.abspath(filepath)
    backup_dir = os.path.join(os.path.dirname(filepath), "backups")
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.basename(filepath)
    backup_path = os.path.join(backup_dir, f"{filename}.backup_{timestamp}")

    try:
        shutil.copy2(filepath, backup_path)
        print(f"OK Создан бэкап: {backup_path}")
        return True
    except Exception as e:
        print(f"Ошибка при создании бэкапа: {e}")
        return False


def restore_file(filepath, backup_timestamp=None):
    """Восстановление файла из бэкапа"""
    filepath = os.path.abspath(filepath)
    backup_dir = os.path.join(os.path.dirname(filepath), "backups")

    if backup_timestamp:
        backup_path = os.path.join(backup_dir,
            f"{os.path.basename(filepath)}.backup_{backup_timestamp}")
    else:
        if not os.path.exists(backup_dir):
            print(f"Директория бэкапов не найдена: {backup_dir}")
            return False

        all_files = os.listdir(backup_dir)
        prefix = os.path.basename(filepath)
        matches = [f for f in all_files
                   if f.startswith(prefix) and ".backup_" in f]
        if not matches:
            print(f"Бэкапы для {filepath} не найдены")
            return False

        matches.sort(reverse=True)
        backup_path = os.path.join(backup_dir, matches[0])

    if not os.path.exists(backup_path):
        print(f"Бэкап {backup_path} не найден")
        return False

    try:
        shutil.copy2(backup_path, filepath)
        print(f"OK Восстановлен: {filepath} из {os.path.basename(backup_path)}")
        return True
    except Exception as e:
        print(f"Ошибка при восстановлении: {e}")
        return False


def restore_settings_backup():
    """Восстановление настроек из бэкапа"""
    from config_path import get_config_dir
    backup_dir = get_config_dir()
    backup_path = os.path.join(backup_dir, "settings.json.backup")

    if not os.path.exists(backup_path):
        print("Бэкап настроек не найден")
        return False

    try:
        shutil.copy2(backup_path, "config/settings.json")
        print("OK Настройки восстановлены из бэкапа")
        return True
    except Exception as e:
        print(f"Ошибка при восстановлении настроек: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Создание и восстановление бэкапов")
    parser.add_argument("action", choices=["backup", "restore"],
                        help="Действие")
    parser.add_argument("filepath", nargs="?", help="Путь к файлу")
    parser.add_argument("--timestamp", help="Таймстамп бэкапа (для restore)")
    args = parser.parse_args()

    if args.action == "backup":
        if not args.filepath:
            parser.error("Для backup необходимо указать filepath")
        backup_file(args.filepath)
    elif args.action == "restore":
        if not args.filepath:
            parser.error("Для restore необходимо указать filepath")
        restore_file(args.filepath, args.timestamp)


if __name__ == "__main__":
    main()
