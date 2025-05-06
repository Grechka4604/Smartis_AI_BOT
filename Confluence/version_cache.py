import os
import logging

CACHE_FILENAME = ".version_cache"

# выгрузка текущго кэша
def load_version_cache(output_dir):
    cache = {}
    path = os.path.join(output_dir, CACHE_FILENAME)
    if os.path.exists(path):
        with open(path, 'r') as f:
            for line in f:
                parts = line.strip().split('|')
                if len(parts) == 2:
                    cache[parts[0]] = int(parts[1])
    return cache

# закгрузка нового кэша
def save_version_cache(cache, output_dir):
    path = os.path.join(output_dir, CACHE_FILENAME)
    with open(path, 'w') as f:
        for page_id, version in cache.items():
            f.write(f"{page_id}|{version}\n")

# логирование
def setup_logging(log_path):
    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        encoding='utf-8'
    )

# выгрузка статистики
def log_sync_result(new_count, updated_count, failed_files):
    msg = (
        f"Синхронизация завершена: "
        f"{new_count} новых, {updated_count} обновлено, {len(failed_files)} с ошибками"
    )
    logging.info(msg)
    if failed_files:
        logging.error("Не удалось обработать файлы: " + ", ".join(failed_files))
