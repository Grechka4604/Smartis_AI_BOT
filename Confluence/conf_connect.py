# main.py

import os
from config import USERNAME, PASSWORD, OUTPUT_DIR
from Confluence.confluence_api import get_all_pages_ids, get_page_details
from Confluence.version_cache import load_version_cache, save_version_cache, setup_logging, log_sync_result
from requests.auth import HTTPBasicAuth
import requests

POLLING_INTERVAL = 3600  # 1 час
NEW_DIR = os.path.join(OUTPUT_DIR, "new_files")
UPD_DIR = os.path.join(OUTPUT_DIR, "updated_files")
LOG_FILE = os.path.join(OUTPUT_DIR, "sync.log")
CACHE_FILE = os.path.join(OUTPUT_DIR, ".version_cache")
MAP_FILE = os.path.join(OUTPUT_DIR, "file_mapping.json")

session = requests.Session()
session.auth = HTTPBasicAuth(USERNAME, PASSWORD)


# создание дирректорий, если они не сущетсвуют
def ensure_dirs():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(NEW_DIR, exist_ok=True)
    os.makedirs(UPD_DIR, exist_ok=True)
    setup_logging(LOG_FILE)

    # проверка прав на запись
    test_file = os.path.join(OUTPUT_DIR, '.permission_test')
    try:
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
    except Exception as e:
        raise PermissionError(f"Нет прав на запись в {OUTPUT_DIR}: {str(e)}")





# основная функция синхронизации страниц
def sync_pages():
    version_cache = load_version_cache(OUTPUT_DIR)
    new_cache = {}
    new_count = 0
    updated_count = 0
    failed_files = []

    for id in get_all_pages_ids():
        page_id = id
        if not page_id:
            continue

        details = get_page_details(page_id)
        if not details:
            failed_files.append(page_id)
            continue
        filename = f"{page_id}.html"
        target_dir = NEW_DIR if page_id not in version_cache else UPD_DIR
        file_path = os.path.join(target_dir, filename)

        new_cache[page_id] = details['version']

        if page_id in version_cache and version_cache[page_id] >= details['version']:
            continue

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(details['content'])
            if page_id not in version_cache:
                new_count += 1
                print(f"Добавлен новый: {page_id}")
            else:
                updated_count += 1
                print(f"Обновлён: {page_id}")
        except Exception as e:
            failed_files.append(page_id)
            print(f"Ошибка при сохранении {filename}: {str(e)}")

    save_version_cache(new_cache, OUTPUT_DIR)
    log_sync_result(new_count, updated_count, failed_files)


