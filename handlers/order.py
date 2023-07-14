import datetime
import re
import aiofiles
from aiogram import Router
from aiogram.filters.text import Text
from aiogram.filters import StateFilter
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from keyboards.for_menu import menu_keyboard, to_menu_keyboard, edit_profile_button, edit_profile_buttons_menu

from utils.databases import UsersDataBase

router = Router()

userDB = UsersDataBase()

async def read_file(filename):
    async with aiofiles.open(filename, mode='r') as file:
        content = await file.read()
        return content

@router.message(Text(['🖊 Заказать','заказать','Заказать','заказ','Сделать заказать', 'сделать заказ']))
async def order(message: Message, state: FSMContext):
    get = await userDB.get(message.from_user)
    await state.clear()
    content = await read_file("utils/ordering_message.txt")
    await message.answer(content)