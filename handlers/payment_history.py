import asyncio
import json
import aiofiles
from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.filters.text import Text
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from keyboards.for_menu import menu_keyboard, edit_profile_button, edit_profile_buttons_menu
from keyboards.for_payment_history import paginator_buttons

from utils.databases import UsersDataBase

router = Router()

userDB = UsersDataBase()


@router.message(Text('💳 Детализация расходов'))
async def payment_history(message: Message, state: FSMContext,):
    msg = ''
    page = 1
    # for row in await userDB.get_payment_history(message.from_user):
    #     msg += f'<b>{row[4]}{row[3]} баллов</b>\nДата: {row[5]}. \nАдминистратора: {row[2] if row[2] != "bot" else "система"}\nПричина: {row[6]}\n\n'
    #     count += 1
    i = 0
    count = (len(await userDB.get_payment_history(message.from_user.id)))
    if count >= 5:
        pages = int(count/5)
        for row in await userDB.get_payment_history(message.from_user.id):
            if i < 5:
                msg += f'<b>{row[4]}{row[3]} баллов</b>\nДата: {row[5]}. \nАдминистратора: {row[2] if row[2] != "bot" else "система"}\nПричина: {row[6]}\n\n'
                i += 1
        if count > 5:
            if count/5 > pages:
                pages += 1
            reply_markup = paginator_buttons(page, pages)
            msg += f'<b>{page}</b> из <b>{pages}</b> страниц'
            await userDB.pages(message.from_user, page, pages, 1)
    else:
        for row in await userDB.get_payment_history(message.from_user.id):
            msg += f'<b>{row[4]}{row[3]} баллов</b>\nДата: {row[5]}. \nАдминистратор: {row[2] if row[2] != "bot" else "система"}\nПричина: {row[6]}\n\n'
        reply_markup=menu_keyboard(is_admin=(False if not await userDB.get_admin(message.from_user) else True))

    await message.answer(msg, reply_markup=reply_markup)

@router.callback_query(Text('block_button'))
async def block_button_click(callback: CallbackQuery, state: FSMContext):
    pass

@router.callback_query(Text('right_button'))
async def right_button_click(callback: CallbackQuery, state: FSMContext):
    i = 0
    msg = ''
    page = await userDB.pages(callback.from_user, 0, 0, 4)
    k = (page[1]*5)
    for i in range(5):
        if k < (len(await userDB.get_payment_history(callback.from_user.id))):
            rows = await userDB.get_payment_history(callback.from_user.id)
            row = rows[k]
            msg += f'<b>{row[4]}{row[3]} баллов</b>\nДата: {row[5]}. \nАдминистратора: {row[2] if row[2] != "bot" else "система"}\nПричина: {row[6]}\n\n'
            i += 1
            k+=1
    msg += f'<b>{page[1]+1}</b> из <b>{page[2]}</b> страниц'
    reply_markup = paginator_buttons((page[1]+1), page[2])
    await callback.message.edit_text(msg)
    await callback.message.edit_reply_markup(reply_markup=reply_markup)
    await userDB.pages(callback.from_user, 0, 0, 2)

@router.callback_query(Text('left_button'))
async def left_button_click(callback: CallbackQuery, state: FSMContext):
    i = 0
    msg = ''
    page = await userDB.pages(callback.from_user, 0, 0, 4)
    k = (page[1]*5-5*2)
    for i in range(5):
        rows = await userDB.get_payment_history(callback.from_user.id)
        row = rows[k]
        msg += f'<b>{row[4]}{row[3]} баллов</b>\nДата: {row[5]}. \nАдминистратора: {row[2] if row[2] != "bot" else "система"}\nПричина: {row[6]}\n\n'
        i += 1
        k += 1
    msg += f'<b>{page[1]-1}</b> из <b>{page[2]}</b> страниц'
    reply_markup = paginator_buttons((page[1]-1), page[2])
    await callback.message.edit_text(msg)
    await callback.message.edit_reply_markup(reply_markup=reply_markup)
    await userDB.pages(callback.from_user, 0, 0, 3)