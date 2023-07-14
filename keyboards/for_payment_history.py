from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from utils.databases import UsersDataBase
userDB = UsersDataBase()

def paginator_buttons(page: int, pages: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    if page == 1:
        kb.button(text="🛑", callback_data='block_button')
    elif page > 1:
        kb.button(text="◀", callback_data='left_button')
    if page >= pages:
        kb.button(text="🛑", callback_data='block_button')
    elif page < pages:
        kb.button(text="▶", callback_data='right_button')
    return kb.as_markup(resize_keyboard=True)