from OpenAI.openai_api import delete_files, upload_files
import os
from config import OUTPUT_DIR
from OpenAI.file_mapping import return_id


# загркзка обновленных страниц
def sync_updated_files():
    path = os.path.join(OUTPUT_DIR, "updated_files")
    for file in os.listdir(path):
        try:
            file_path = os.path.join(path, file)  
            if os.path.isfile(file_path):  
                id = return_id(file, OUTPUT_DIR)
                delete_files(id)
                upload_files([file_path]) 
                os.remove(file_path)
        except Exception as e:
            print(f"Ошибка при загрузке файла {file}: {e}")



# загрузка новых страниц
def sync_new_files():
    path = os.path.join(OUTPUT_DIR, "new_files")
    for file in os.listdir(path):
        try:
            file_path = os.path.join(path, file)  
            if os.path.isfile(file_path):  
                upload_files([file_path]) 
                os.remove(file_path)
        except Exception as e:
            print(f"Ошибка при загрузке файла {file}: {e}")
        
