from aiogram import types
from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def get_feedback_keyboard() -> ReplyKeyboardMarkup:
    """
    Стандартная раскладка клавиатуры на 2 кнопки "Да" и "Нет". Вынесена в отдельный скрипт
    для последующего переиспользования в боте для разработчиков.

    :return: ReplyKeyboardMarkup
    """

    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text='Да'))
    builder.add(types.KeyboardButton(text='Нет'))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)
