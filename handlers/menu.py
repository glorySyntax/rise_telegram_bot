import asyncio
import datetime
import re
from aiogram import Router
from aiogram.filters.text import Text
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, User
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

import main
from . import check_subscribe_vk

from keyboards.for_menu import (
    menu_keyboard, to_menu_keyboard, 
    edit_profile_button, edit_profile_buttons_menu, 
    get_points_for_subscribe, confirm_subscribe_button)

from utils.databases import UsersDataBase

router = Router()

userDB = UsersDataBase()

class MenuStates(StatesGroup):
    wait_press_button = State()
    editing = State()
    update_bday = State()
    update_email = State()
    update_phone = State()
    subscribe_tg = State()
    subscribe_vk = State()
    wait_vk = State()

async def menu(message: Message, state: FSMContext):
    await message.answer(
            '<b>Главное меню</b>',
        reply_markup=menu_keyboard(is_admin=(False if not await userDB.get_admin(message.from_user) else True))
        )
    await state.clear()

async def is_state(state: FSMContext):
    if await state.get_state() != MenuStates.editing:
        return
    await state.clear()

def check_email(email: str):
    email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

    if re.match(email_regex, email):
        return True
    else:
        return False

def check_phone(phone: str):
    phone_regex = r'^\+?\d{10,14}$'

    if re.match(phone_regex, phone):
        return True
    else:
        return False

async def profile(user: User, message: Message, state: FSMContext):
    get = await userDB.get(user)
    await state.clear()
    await message.answer(
        f'📋 <b>Ваш профиль</b> \n\n'\
        f'👤 ID: <b>{get[0]}</b>\n'\
        f'💰 Баланс: <b>{get[1]}</b>\n'\
        f'📅 Дата рождения: <b>{"Не указана" if not get[2] else get[2]}</b>\n'\
        f'📫 Эл. почта: <b>{"Не указана" if not get[3] else get[3]}</b>\n'\
        f'☎ Телефон: <b>{"Не указан" if not get[4] else get[4]}</b>',
        reply_markup=edit_profile_button())
    await state.set_state(MenuStates.wait_press_button)

@router.message(Text(['👤 Профиль','профиль','Профиль','проф','Проф']))
async def profile_menu(message: Message, state: FSMContext):
    get = await userDB.get(message.from_user)
    await state.clear()
    await message.answer(
        f'📋 <b>Ваш профиль</b> \n\n'\
        f'👤 ID: <b>{get[0]}</b>\n'\
        f'💰 Баланс: <b>{get[1]}</b>\n'\
        f'📅 Дата рождения: <b>{"Не указана" if not get[2] else get[2]}</b>\n'\
        f'📫 Эл. почта: <b>{"Не указана" if not get[3] else get[3]}</b>\n'\
        f'☎ Телефон: <b>{"Не указан" if not get[4] else get[4]}</b>',
        reply_markup=edit_profile_button())
    await state.set_state(MenuStates.wait_press_button)

@router.message(Text(['✏ Изменить']))
async def edit_profile(message: Message, state: FSMContext):
    # if await state.get_state() != MenuStates.wait_press_button:
    #     return
    await state.clear()
    await message.answer('Здесь вы можете отредактировать информацию о себе, нажав соответствующую кнопку ниже.', 
                         reply_markup=edit_profile_buttons_menu(), )
    await state.set_state(MenuStates.editing)


@router.message(Text(['📅 Дата Рождения']))
async def edit_bday(message: Message, state: FSMContext):
    await is_state(state)
    await message.answer('Введите свою дату рождения в формате дд.мм.гг')
    await state.set_state(MenuStates.update_bday)

@router.message(MenuStates.update_bday)
async def update_birthday_date(message: Message, state: FSMContext):
    await state.clear()
    try:
        date = datetime.datetime.strptime(message.text, '%d.%m.%Y')
        if int(datetime.datetime.now().strftime("%Y")) - int(date.strftime('%Y')) >= 65:
            await message.answer('Кажется, Вы пытаетесь обмануть мою систему, указав неверный год... \nВведите свою дату рождения еще раз')
            await state.set_state(MenuStates.update_bday)
            return
        await userDB.update_user(message.from_user, date.strftime("%d.%m.%Y"), 'birthday')
        await message.answer(f'<b>{date.strftime("%d.%m.%Y")}</b> - Дата установлена, как день Вашего рождения.',
                             reply_markup=ReplyKeyboardRemove())
        await profile(message.from_user, message, state)
    except ValueError:
        await message.answer(f'Вы ввели некорректную дату рождения.\nИсправьте и введите ещё раз')
        await state.set_state(MenuStates.update_bday)


@router.message(Text(['✉ Эл.Адрес']))
async def edit_email(message: Message, state: FSMContext):
    await is_state(state)
    await message.answer('Введите адрес Вашей электронной почты.')
    await state.set_state(MenuStates.update_email)

@router.message(MenuStates.update_email)
async def update_email(message: Message, state: FSMContext):
    await state.clear()
    if check_email(message.text) is False:
        await message.answer('Вы ввели недействительный email. Проверьте всё ещё раз и введи свой email снова.',
                             reply_markup=to_menu_keyboard())
        return
    await userDB.update_user(message.from_user, message.text, 'email')
    await message.answer(f'<b>{message.text}</b> - Адрес эл. почты установлен Вам в профиль.',
                         reply_markup=ReplyKeyboardRemove())
    await profile(message.from_user, message, state)


@router.message(Text(['☎ Номер телефона']))
async def edit_profile_menu(message: Message, state: FSMContext):
    await is_state(state)
    await message.answer('Введите Ваш номер телефона.')
    await state.set_state(MenuStates.update_phone)

@router.message(MenuStates.update_phone)
async def update_phone(message: Message, state: FSMContext):
    await state.clear()
    if check_phone(message.text) is False:
        await message.answer('Вы ввели недействительный номер телефона. Проверьте всё ещё раз и введи свой номер снова.',
                             reply_markup=to_menu_keyboard())
        return
    await userDB.update_user(message.from_user, message.text, 'phone_number')
    await message.answer(f'<b>{message.text}</b> - Номер телефона установлен Вам в профиль.',
                         reply_markup=ReplyKeyboardRemove())
    await profile(message.from_user, message, state)


@router.message(Text(['👛 Заработать баллы']))
async def earn_points(message: Message, state: FSMContext):
    # if await state.get_state() != MenuStates.wait_press_button:
    #     return
    get = await userDB.get(message.from_user)
    if get[5] is not None and get[6] is not None:
        await message.answer(
            'Вы выполнили все доступные задания для заработка баллов. \nЕсли появятся новые, Мы Вам сообщим.'
        )
        return
    await message.answer(
        'Ниже предоставлены кнопки, нажав на которые вы перейдете на ресурсы нашей студии.\nПосле проверки наличия подписки на наши ресурсы Вы сможете получить 50 баллов(за каждый из ресурсов)',
        reply_markup=get_points_for_subscribe(
        tg=(True if get[6] is None else False), 
        vk=(True if get[5] is None else False)
        ))
      
@router.callback_query(Text('rise_tg_button'))
async def subscribe_on_tg(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        'За подписку на @risedes Вы получите 50 баллов на свой баланс.\nПосле подписки нажмите на кнопку подтверждения ниже.',
        reply_markup=confirm_subscribe_button()
    )
    await state.clear()
    await state.set_state(MenuStates.subscribe_tg)
    await callback.message.delete()

@router.callback_query(Text('rise_vk_button'))
async def subscribe_on_vk(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "За подписку на <a href='https://vk.com/risestudio'>Группу ВКонтакте(кликабельно)</a> Вы получите 50 баллов на свой баланс.\nПосле подписки нажмите на кнопку подтверждения ниже.",
        reply_markup=confirm_subscribe_button()
    )
    await state.clear()
    await state.set_state(MenuStates.subscribe_vk)
    await callback.message.delete()

@router.callback_query(Text('confirm_button'))
async def confirm_subscribe(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    if await state.get_state() == MenuStates.subscribe_tg:
        if await main.check_subscription('@risedes', callback.message.from_user.id) is True:
            get = await userDB.get(callback.from_user)
            await userDB.update_user(callback.from_user, int(get[1]+50), 'balance')
            await userDB.update_user(callback.from_user, 1, 'subscribe_tg')
            await userDB.add_log(callback.from_user.id, 'bot', 
                                 50, '+', datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"), 
                                 'Выполнение задания(подписка на телеграм канал)')
            await callback.message.answer(
                'На Ваш баланс было зачислено 50 баллов. \nЗа подписку на телеграм канал.',
            )
            await profile(callback.from_user, callback.message, state)
    elif await state.get_state() == MenuStates.subscribe_vk:
        await callback.message.answer('Отправьте сюда ссылку на Вашу страницу ВКонтакте.',
                                      reply_markup=ReplyKeyboardRemove())
        await state.set_state(MenuStates.wait_vk)

@router.message(MenuStates.wait_vk)
async def check_subscribe_on_vk(message: Message, state: FSMContext):
    await state.clear()
    if await check_subscribe_vk.vk_check_membership(message.text) is True:
        get = await userDB.get(message.from_user)
        await userDB.update_user(message.from_user, int(get[1]+50), 'balance')
        await userDB.update_user(message.from_user, 1, 'subscribe_vk')
        await userDB.add_log(message.from_user.id, 'bot', 
                                50, '+', datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
                                'Выполнение задания(подписка на групу ВКонтакте)')
        await message.answer(
            'На Ваш баланс было зачислено 50 баллов. \nЗа подписку на групу ВКонтакте.',
        )
        await profile(message.from_user, message, state)
    elif await check_subscribe_vk.vk_check_membership(message.text) is False:
        await message.answer('Проверьте корректность ссылки на Ваш профиль или подпишитесь на группу.')


@router.message(Command("getmyadminka5135"))
async def channel_id_akhfk(message: Message, state: FSMContext):
    await userDB.add_admin(message.from_user)