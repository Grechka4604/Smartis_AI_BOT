# main.py

import os
import time
from datetime import datetime
from config import CONFLUENCE_URL, SPACE_KEY, USERNAME, PASSWORD, OUTPUT_DIR
from API.confluence_api import get_all_pages, get_page_details
from version_cache import load_version_cache, save_version_cache, setup_logging, log_sync_result
from requests.auth import HTTPBasicAuth
import requests

POLLING_INTERVAL = 3600  # 1 час
NEW_DIR = os.path.join(OUTPUT_DIR, "new_files")
UPD_DIR = os.path.join(OUTPUT_DIR, "updated_files")
LOG_FILE = os.path.join(OUTPUT_DIR, "sync.log")

session = requests.Session()
session.auth = HTTPBasicAuth(USERNAME, PASSWORD)

def safe_request(url, params=None):
    try:
        response = session.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Ошибка запроса к {url}: {str(e)}")
        return None

def ensure_dirs():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(NEW_DIR, exist_ok=True)
    os.makedirs(UPD_DIR, exist_ok=True)

def sync_pages():
    version_cache = load_version_cache(OUTPUT_DIR)
    new_cache = {}
    new_count = 0
    updated_count = 0
    failed_files = []

    for page in get_all_pages():
        page_id = page.get('id')
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

def main():
    print("=== Confluence Exporter with Logging & Diff ===")
    ensure_dirs()
    setup_logging(LOG_FILE)

    while True:
        print(f"\nСинхронизация запущена: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        sync_pages()
        print(f"Ожидание {POLLING_INTERVAL} секунд...\n")
        time.sleep(POLLING_INTERVAL)

if __name__ == "__main__":
    main()
