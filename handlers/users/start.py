from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart
from keyboards.default.main_menu import main
from loader import dp
from data.config import ADMINS
from aiogram.dispatcher import FSMContext
from states.main_state import Main


@dp.message_handler(CommandStart(), chat_id=ADMINS, state="*")
async def bot_start(message: types.Message, state: FSMContext):
    await message.answer('🏠 Bosh menyu', reply_markup=main)
    await Main.main_menu.set()

