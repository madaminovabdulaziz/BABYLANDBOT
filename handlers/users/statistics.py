from aiogram.types import *
from aiogram.dispatcher import FSMContext
from pytz import timezone
from datetime import datetime
from keyboards.default.main_menu import main
from keyboards.default.stats import stats
from loader import dp, bot, db
from states.main_state import Main


@dp.message_handler(text="📊 Statistika ko'rish", state=Main.main_menu)
async def showMenu(message: Message, state: FSMContext):
    await message.answer("Tanlang: ", reply_markup=stats)
    await state.set_state("select_stats")


btn = ["Bugun kelganlar", "Bugungi kirim", "Oy kirim"]


@dp.message_handler(text=btn, state="select_stats")
async def showStats(message: Message, state: FSMContext):
    time_format = '%Y-%m-%d'
    formatted_now = datetime.now(timezone('Asia/Tashkent')).strftime(time_format)
    action = message.text
    if action == btn[0]:
        today_count = await db.count_todays_comed(formatted_now)
        obshi = await db.count_children()

        await message.answer(f"""
Bugun: {formatted_now}

Umimiy <b>{obshi[0]}</b>-ta boladan <b>{today_count}</b>-ta keldi!
        """)
        await message.answer("Tanlang: ", reply_markup=stats)
        await state.set_state("select_stats")

    elif action == btn[1]:
        kirim = await db.bugungi_kirim(formatted_now)
        await message.answer(f"Bugun sizning kirimingiz: <b>{kirim[0]}</b>-so'm")
        await message.answer("Tanlang: ", reply_markup=stats)
        await state.set_state("select_stats")


    elif action == btn[2]:
        oylik_kriim = await db.oylik_kirim()
        oy = oylik_kriim[1]
        await message.answer(f"Bu oy {oylik_kriim[0]}-ning {oy}-oyi\n\nBu oy kirim: <b>{oylik_kriim[2]}</b>-so'm")
        await message.answer("Tanlang: ", reply_markup=stats)
        await state.set_state("select_stats")
