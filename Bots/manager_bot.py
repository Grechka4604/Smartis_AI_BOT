import asyncio

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.methods import SendMessage
from config import BOT_TOKEN
from OpenAI.openai_api import get_assistant_response
from datetime import datetime
from .Keyboards.ClientFeedback import get_feedback_keyboard
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

SHEET_NAME = 'all_results'
SPREADSHEET_ID = '1UgSpHlR_dfYYgfIkVYOwfsarwrS0x4q_Q-XtcRM_TyA'
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
user_data = {}
creds = Credentials.from_service_account_file('credentials.json',
                                              scopes=['https://www.googleapis.com/auth/spreadsheets'])

service = build('sheets', 'v4', credentials=creds)


def run_bot():
    asyncio.run(dp.start_polling(bot))


async def append_to_sheet(data: list):
    """
    Собираем статистику по ответам в гугл таблицы. Однажды перенесём сбор статистики в БД, но пока оставим так.

    Формат таблицы: Дата | Запрос пользователя | Ответ бота | Помог ли бот

    :param data:
    :return:
    """
    range_name = SHEET_NAME + '!A:D'
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=range_name
    ).execute()
    values = result.get('values', [])
    next_row = len(values) + 1 if values else 1

    body = {'values': [data]}
    service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=f'{SHEET_NAME}!A{next_row}',
        valueInputOption='USER_ENTERED',
        body=body
    ).execute()


@dp.message(CommandStart())
async def command_start(message: types.Message):
    """
    Стартовое сообщение бота при запуске команды /start

    :param message:
    :return:
    """
    await message.answer('Привет! Напиши мне что-нибудь — я знаю все про Smartis')


@dp.message(F.text.lower().in_({'да', 'нет'}))
async def handle_feedback(message: types.Message) -> SendMessage | None:
    """
    Обработка сообщения, когда оно состоит из "да" или "нет".
    Также сохраняем статистику в гугл таблицы, подробнее см. описание append_to_sheet()

    :param message:
    :return:
    """

    user_id = message.from_user.id
    if user_id in user_data:
        row = [
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            user_data[user_id]['question'],
            user_data[user_id]['answer'],
            message.text
        ]
        try:
            await append_to_sheet(row)
        except:
            service = build('sheets', 'v4', credentials=creds)
            await append_to_sheet(row)
        del user_data[user_id]
    if message.text.lower() == 'да':
        await message.answer('Отлично! Рад, что смог помочь!', reply_markup=types.ReplyKeyboardRemove())
    else:
        await message.answer('Жаль, что не смог помочь. Постараюсь улучшиться!',
                             reply_markup=types.ReplyKeyboardRemove())


@dp.message()
async def handle_user_message(message: types.Message) -> SendMessage | None:
    """
    Ответ на запрос пользователя, поиск информации в документации.

    :param message: Пришедшее сообщение
    :return: SendMessage|None
    """

    if message.text.lower() in {'да', 'нет'}:
        return

    await message.answer('Думаю над ответом...')
    user_id = message.from_user.id

    try:
        reply = await get_assistant_response(message.text)
        await message.answer(reply)

        user_data[user_id] = {
            'question': message.text,
            'answer': reply
        }

        await message.answer('Помог ли вам этот ответ?', reply_markup=get_feedback_keyboard())
    except Exception as e:
        await message.answer(f'❌ Произошла ошибка: {e}')
