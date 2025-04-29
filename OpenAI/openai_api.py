from openai import AsyncOpenAI, OpenAI
from config import OPEN_AI_API_KEY, ASSISTIANT_ID, VECTORE_ID, OUTPUT_DIR, INSTRUCTIONS
import asyncio
import os
from OpenAI.file_mapping import save_mappings, load_mappings

# инициализируем асинхронного клиента
async_client = AsyncOpenAI(api_key=OPEN_AI_API_KEY)
assistant = async_client.beta.assistants.retrieve(ASSISTIANT_ID)

# инициализируем синхронного клиента
client = OpenAI(api_key=OPEN_AI_API_KEY)

vectorstoreid = VECTORE_ID





# метод для удаления файлов из векторного хранилища
def delete_files(file_id):
    try:
        file_delete = client.vector_stores.files.delete(
            vector_store_id=vectorstoreid, file_id=file_id,
        )
    except Exception as e:
        print(f"Ошибка удаления '{file_id}': {str(e)}")



# обновленный метод загрузки файлов с маппингом идентификаторо и имен файлов
def upload_files(file_paths):
    file_mapping = load_mappings(OUTPUT_DIR)
    
    for path in file_paths:
        file_name = os.path.basename(path)
            
        try:
            with open(path, "rb") as f:
                print(f"Загружаем: {file_name}")
                file_batch = client.vector_stores.file_batches.upload_and_poll(
                    vector_store_id=vectorstoreid,
                    files=[f]
                )
                
                if file_batch.status == 'completed':
                    files = client.vector_stores.file_batches.list_files(
                        vector_store_id=vectorstoreid,
                        batch_id=file_batch.id
                    )
                    if files.data:
                        file_mapping[file_name] = files.data[0].id
                        save_mappings(file_mapping, OUTPUT_DIR)
                        print(f"Успешно: '{file_name}' → ID {files.data[0].id}")
                        if file_name in file_mapping:
                            print(f"Обновлён ID для существующего имени файла")
                        
        except Exception as e:
            print(f"Ошибка загрузки '{file_name}': {str(e)}")
    
    return file_mapping





# функция для отладки
def list_of_files():
    list_of_files = client.vector_stores.files.list(vector_store_id=VECTORE_ID)
    for file in list_of_files:
        print(file, end = "\n\n")









# асинхронная функция запросов
async def get_assistant_response(user_message: str) -> str:
    try:
        thread = await async_client.beta.threads.create() 
        
        await async_client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_message
        )
        
        run = await async_client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=ASSISTIANT_ID,
            instructions=INSTRUCTIONS
        )
        
        start_time = asyncio.get_event_loop().time()
        while True:
            run_status = await async_client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
            
            if run_status.status == "completed":
                break
            elif run_status.status == "failed":
                raise RuntimeError("Ассистент не смог обработать запрос")
            elif asyncio.get_event_loop().time() - start_time > 30:
                raise TimeoutError("Превышено время ожидания")
                
            await asyncio.sleep(0.5)
        
        messages = await async_client.beta.threads.messages.list(
            thread_id=thread.id,
            limit=1
        )
        return messages.data[0].content[0].text.value
        
    except TimeoutError:
        return "⌛ Ассистент долго отвечает. Попробуйте сократить запрос."
    except Exception as e:
        return f"⚠️ Произошла ошибка: {str(e)}"




    

