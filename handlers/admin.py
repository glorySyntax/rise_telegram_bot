import datetime
import re
import aiofiles
from aiogram import Router, Bot
from aiogram.filters import Command, StateFilter
from aiogram.filters.text import Text
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from keyboards.for_apanel import amenu_keyboard
import main

from utils.databases import UsersDataBase

router = Router()

userDB = UsersDataBase()

class AdminStates(StatesGroup):
    in_apanel = State()
    wait_id = State()
    wait_id2 = State()
    wait_id3 = State()
    broadcast = State()
    wait_order_text = State()

async def write_file(text: str):
    async with aiofiles.open('utils/ordering_message.txt', mode='w') as file:
        content = await file.write(text)
        return content

async def broadcast_message(bot: Bot, message: Message):
    n = 0
    users = await userDB.all_users()
    for user in users:
        await bot.send_message(chat_id=int(user[0]),
                               text=f"{message.text}")
        n+=1
    return (f"{n} из {len(users)} получили рассылку")

async def check_apanel_state(state: FSMContext):
    if await state.get_state() != AdminStates.in_apanel:
        return 
    await state.clear()

@router.message(Text('👑 Админ-панель'))
async def apanel_general_menu(message: Message, state: FSMContext):
    await state.clear()
    await message.answer('Админ-панель',
                         reply_markup=amenu_keyboard())
    await state.set_state(AdminStates.in_apanel)
    
@router.message(Text('➕ Снять/выдать баллы'))
async def apanel_add_or_remove_points(message: Message, state: FSMContext):
    await check_apanel_state(state)
    await state.set_state(AdminStates.wait_id)
    await state.set_data(["points"])
    await message.answer('Отправьте сюда ID пользователя')

@router.message(Text('📜 История баллов'))
async def apanel_logs_points_got_user(message: Message, state: FSMContext):
    await check_apanel_state(state)
    await state.set_state(AdminStates.wait_id)
    await state.set_data(["history"])
    await message.answer('Отправьте сюда ID пользователя')

@router.message(AdminStates.wait_id)
async def add_or_remove_points(message: Message, state: FSMContext):
    act = await state.get_data()
    msg = ''
    global uid
    try:
        uid = int(message.text)
    except:
        await message.answer('ID может состоять только из цифр.')
        await apanel_general_menu(message, state)
        return
    if not await userDB.get2(uid):
        await message.answer('Пользователь не найден в базе.')
        await apanel_general_menu(message, state)
        return
    await state.clear()
    if act[0] == 'points':
        get = await userDB.get2(uid)
        await message.answer(f'Пользователь найден в базе.\nБаланс пользователя: <b>{get[1]}</b>\nВведите действие и количество баллов. Например: +100 - прибавить 100 баллов, -350 - отнять 350 баллов.\n\n<b>Без пробелов где-либо</b>')
        await state.set_state(AdminStates.wait_id2)
    if act[0] == 'history':
        i = 0
        rows = await userDB.get_payment_history(message.from_user.id)
        if rows[i][2] != "bot":
            adm = 'система'
        else:
            adm = rows[i][2]
        for row in await userDB.get_payment_history(message.from_user.id):
            msg += f'<b>{row[4]}{row[3]} баллов</b>\nДата: {row[5]}. \nАдминистратор: {row[2] if row[2] != "bot" else "система"}\nПричина: {row[6]}\n\n'
        else:
            await message.answer(msg)
                

@router.message(AdminStates.wait_id2)
async def add_or_remove_points2(message: Message, state: FSMContext):
    global action, count
    msg = message.text
    action = msg[0]
    if not action in ['-','+']:
        await message.answer('Первым символом сообщения может быть только - или +.')
        await apanel_general_menu(message, state)
        return
    countt = re.findall(r'\d+(?:\.\d+)?', msg)
    count = countt[0]
    await message.answer('Введите причину Вашего действия.')
    await state.set_state(AdminStates.wait_id3)

@router.message(AdminStates.wait_id3)
async def add_or_remove_points3(message: Message, state: FSMContext):
    await state.clear()
    reason = message.text
    await userDB.update_balance(uid, action, count)
    await userDB.add_log(uid, message.from_user.id, 
                         count, action, 
                         datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
                         reason)
    get = await userDB.get2(uid)
    await message.answer(
        f'Пользователю <b>{uid}</b> был изменен баланс на <b>{action}{count}</b>\nТекущий баланс пользователя: <b>{get[1]}</b>')
    await apanel_general_menu(message, state)

@router.message(Text('💬 Рассылка'))
async def apanel_send_for_all(message: Message, state: FSMContext):
    await check_apanel_state(state)
    await state.set_state(AdminStates.broadcast)
    await message.answer("Введите текст для рассылки:")
    
@router.message(AdminStates.broadcast)
async def process_broadcast_message(message: Message, state: FSMContext):
    txt = await broadcast_message(main.bot, message)
    await state.clear()
    await message.answer(f"Рассылка завершена! {txt}")

@router.message(Text('✏ Текст заказа'))
async def edit_order_text(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(AdminStates.wait_order_text)
    await message.answer(
        'Отправьте сюда текст, который будет отображаться пользователям при заказе')
    
@router.message(AdminStates.wait_order_text)
async def change_order_text(message: Message, state: FSMContext):
    await state.clear()
    await write_file(message.text)
    await message.answer('Текст обновлён.')