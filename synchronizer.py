from Confluence.conf_connect import ensure_dirs, sync_pages
from OpenAI.vs_sync import sync_new_files, sync_updated_files
import time
import datetime

POLLING_INTERVAL = 3600

def main():
    ensure_dirs()
    while True:
        sync_pages()
        # print("begin")
        # sync_new_files()
        # sync_updated_files()
        # print("end")

        time.sleep(POLLING_INTERVAL)

if __name__ == "__main__":
    main()



