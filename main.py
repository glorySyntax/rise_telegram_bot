import asyncio
import logging
import aiogram

from aiogram import Bot, Dispatcher, Router
from aiogram.filters import Command
from aiogram.filters.text import Text
from aiogram.types import Message, ChatMember
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

from handlers import menu, order, payment_history, admin
from keyboards.for_menu import menu_keyboard

from config import TOKEN
from utils.databases import UsersDataBase


router = Router()

userDB = UsersDataBase()

@router.message(Command("start"),)
@router.message(Text(['🔷 Меню','меню','Меню','/start']))
async def cmd_start(message: Message, state: FSMContext):
    if await userDB.get(message.from_user) is None:
        await userDB.reg_user(message.from_user)
        await message.answer(
            "Вы были успешно зарегистрированы в системе. \nПерезапустите бота, чтобы начать работу с ним. \n/start",
            )
    else:
        await message.answer(
            '<b>Главное меню</b>',
        reply_markup=menu_keyboard(is_admin=(False if not await userDB.get_admin(message.from_user) else True))
        )
    chat = await bot.get_chat()
    await state.clear()

bot = Bot(TOKEN, parse_mode="HTML")
dp = Dispatcher(storage=MemoryStorage())

async def main() -> None:
    dp.include_router(router)

    dp.include_routers(menu.router, order.router, payment_history.router, admin.router)
    await userDB.create_table()

    await dp.start_polling(bot)

async def check_subscription(chat_id, user_id):
    try:
        chat_member = await bot.get_chat_member(chat_id=chat_id, user_id=user_id)
        return True
    except:
        return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())