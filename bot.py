from aiogram import Bot, Dispatcher, types
import asyncio
from aiogram.filters import CommandStart
from config import BOT_TOKEN
from OpenAI.openai_api import get_assistant_response



bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer("Привет! Напиши мне что-нибудь — я знаю все про Smartis")


@dp.message()
async def handle_user_message(message: types.Message):
    await message.answer("🤖 Думаю над ответом...")  

    try:
        reply = await get_assistant_response(message.text)
        await message.answer(reply, parse_mode="Markdown")  

    except Exception as e:
        await message.answer(f"❌ Произошла ошибка: {e}") 



async def main():
    await dp.start_polling(bot)
if __name__ == "__main__":
    asyncio.run(main())