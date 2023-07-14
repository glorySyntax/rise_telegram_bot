from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from utils.databases import UsersDataBase
userDB = UsersDataBase()

def amenu_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="➕ Снять/выдать баллы")
    kb.button(text="📜 История баллов")
    kb.button(text="💬 Рассылка")
    kb.button(text="✏ Текст заказа")
    kb.button(text="📊 Статистика")
    kb.button(text="🔷 Меню")
    kb.adjust(2)
    return kb.as_markup()