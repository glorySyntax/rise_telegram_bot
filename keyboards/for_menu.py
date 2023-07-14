from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from utils.databases import UsersDataBase
userDB = UsersDataBase()


def to_menu_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="🔷 Меню")
    kb.button(text="👤 Профиль")
    return kb.as_markup(resize_keyboard=True)

def menu_keyboard(is_admin: bool) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="👤 Профиль")
    kb.button(text="🖊 Заказать")
    kb.button(text="💳 Детализация расходов")
    if is_admin is True:
        kb.button(text="👑 Админ-панель")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)

def edit_profile_button() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="✏ Изменить")
    kb.button(text="🔷 Меню")
    kb.button(text="👛 Заработать баллы")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)

def edit_profile_buttons_menu() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="📅 Дата Рождения")
    kb.button(text="✉ Эл.Адрес")
    kb.button(text="☎ Номер телефона")
    kb.button(text="🔷 Меню")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)

def get_points_for_subscribe(tg: bool, vk: bool) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    if tg:
        kb.button(text="Telegram", callback_data='rise_tg_button')
    if vk:
        kb.button(text="ВКонтакте", callback_data='rise_vk_button')
    return kb.as_markup(resize_keyboard=True)

def confirm_subscribe_button() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Подтвердить", callback_data='confirm_button')
    return kb.as_markup(resize_keyboard=True)