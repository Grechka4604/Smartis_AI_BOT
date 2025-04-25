from openai import AsyncOpenAI
from config import OPEN_AI_API_KEY, ASSISTIANT_ID, VECTORE_ID
import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command


client = AsyncOpenAI(api_key=OPEN_AI_API_KEY)
assistant = client.beta.assistants.retrieve(ASSISTIANT_ID)
vectorstoreid = VECTORE_ID

# функция загрузки файлов
# принимает на вход массив из путей к файлам
def upload_files(file_paths):
    try:
        file_streams = [open(path, "rb") for path in file_paths]
        file_batch = client.vector_stores.file_batches.upload_and_poll(
            vector_store_id = vectorstoreid, files=file_streams
        )
        print(file_batch.status)
        print(file_batch.file_counts)
    
    except Exception as e:
        print(f"error {str()}")

# функция для отладки
def list_of_files():
    list_of_files = client.vector_stores.files.list(vector_store_id=VECTORE_ID)
    for file in list_of_files:
        print(file, end = "\n\n")


async def get_assistant_response(user_message: str) -> str:
    """Получение ответа от ассистента с обработкой всех ошибок"""
    try:
        # 1. Создаем тред (теперь с await!)
        thread = await client.beta.threads.create()  # Важно: await работает в 1.76.0+
        
        # 2. Добавляем сообщение
        await client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_message
        )
        
        # 3. Запускаем ассистента
        run = await client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=ASSISTIANT_ID
        )
        
        # 4. Ожидаем ответ (таймаут 30 сек)
        start_time = asyncio.get_event_loop().time()
        while True:
            run_status = await client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
            
            if run_status.status == "completed":
                break
            elif run_status.status == "failed":
                raise RuntimeError("Ассистент не смог обработать запрос")
            elif asyncio.get_event_loop().time() - start_time > 30:
                raise TimeoutError("Превышено время ожидания")
                
            await asyncio.sleep(0.5)  # Оптимальный интервал проверки
        
        # 5. Получаем ответ
        messages = await client.beta.threads.messages.list(
            thread_id=thread.id,
            limit=1
        )
        return messages.data[0].content[0].text.value
        
    except TimeoutError:
        return "⌛ Ассистент долго отвечает. Попробуйте сократить запрос."
    except Exception as e:
        return f"⚠️ Произошла ошибка: {str(e)}"




    

