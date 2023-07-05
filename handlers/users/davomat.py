from aiogram.types import *
from aiogram.dispatcher import FSMContext
from datetime import datetime
from pytz import timezone
from loader import dp, bot, db
from keyboards.inline.davomatuchun import davomat
import calendar
import asyncio


def get_total_workdays(year, month):
    _, total_days = calendar.monthrange(year, month)
    total_workdays = sum(1 for day in range(1, total_days + 1) if calendar.weekday(year, month, day) < 5)
    return total_workdays


def todaysWorkday(year, month):
    _, total_days = calendar.monthrange(year, month)
    current_date = datetime.now()
    # Calculate the current working day
    working_day = 0
    for day in range(1, total_days + 1):
        weekday = calendar.weekday(year, month, day)
        if weekday < 5:  # Monday to Friday are considered workdays
            working_day += 1
        if day == current_date.day:
            break

    return working_day


@dp.message_handler(text='🔰 Davomat qilish', state="*")
async def show_groups(message: Message, state: FSMContext):
    groups = await db.get_all_groups()
    grps_list = [group[0] for group in groups]

    groups_markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    groups_markup.add(*grps_list)

    await message.answer("Guruhni tanlang: ", reply_markup=groups_markup)
    await state.set_state("get_g_group")


@dp.message_handler(state='get_g_group')
async def send_all_children(message: Message, state: FSMContext):
    group = message.text
    children = await db.get_Allchildren_byGroup(group)
    current_date = datetime.now()
    year, month = current_date.year, current_date.month
    ish_kunlari = get_total_workdays(year, month)

    for child in children:
        name, reg_date, group, photo = child[1], child[2], child[3], child[4]
        hozirgi_ish_kuni = todaysWorkday(year, month)
        bola_id = child[0]
        qarz = await db.get_child_Qarz(bola_id)
        vznos_bola = await db.get_child_vznos(bola_id)
        caption = f"<b>{name}</b>\n"
        caption += f"Ro'yxatdan o'tgan sanasi: {reg_date}\n"
        caption += f"Guruhi: {group}\n\n"
        caption += f"Oylik vznosi: <b>{vznos_bola[0]}-so'm</b>\n\n"
        no = '0'
        caption += f"<b>💵 Qarzi: <i>{qarz[0] if qarz else no}</i>-so'm</b>\n\n"
        caption += f"Bu oy <b>{ish_kunlari}</b>-ish kunidan iborat!\n\n"
        caption += f"Bugun bu oyning <b>{hozirgi_ish_kuni}</b>-chi ish kuni!"

        file_id = photo.split('/')[-1].split('.')[0]
        await asyncio.sleep(0.4)
        await bot.send_photo(
            chat_id=message.chat.id,
            photo=file_id,
            caption=caption,
            reply_markup=davomat(child[0])
        )

    await state.set_state('get_davomat')


@dp.callback_query_handler(text_contains='davomat', state='get_davomat')
async def make_davomat(call: CallbackQuery, state: FSMContext):
    data = call.data.rsplit(":")
    status, bola_id = data[1], data[2]
    time_format = '%Y-%m-%d'
    formatted_now = datetime.now(timezone('Asia/Tashkent')).strftime(time_format)

    attendance_record = await db.get_attendance_by_date(int(bola_id), formatted_now)

    if attendance_record:
        # Attendance already made on the same day, inform the user
        await call.answer("⚠️ Bu bola uchun Davomat allaqachon amalga oshirilgan!", show_alert=True)


    else:
        # status if else
        if status == 'yes':
            # await call.message.delete()
            await db.add_attendance(int(bola_id), formatted_now, 1)

            edited_markup = InlineKeyboardMarkup(row_width=1)
            edited_markup.add(InlineKeyboardButton(text='✅ Kelgan!', callback_data='kelgan'))
            current_date = datetime.now()
            year, month = current_date.year, current_date.month
            total_workdays = get_total_workdays(year, month)

            name = await db.get_child_name_id(bola_id)
            reg_date = await db.get_child_regdate_id(bola_id)
            group = await db.get_child_group_id(bola_id)

            hozirgi_ish_kuni = todaysWorkday(year, month)
            # hozirgi ish kuni ifelse
            if hozirgi_ish_kuni == total_workdays:
                current_date = datetime.now()
                year, month = current_date.year, current_date.month
                ish_kunlari = get_total_workdays(year, month)

                child_vznos = await db.get_child_vznos(bola_id)
                kuniga = child_vznos[0] / ish_kunlari
                kuniga = round(kuniga)

                original_qarz = await db.get_child_Qarz(bola_id)
                original_qarz = original_qarz[0]

                qarz = original_qarz + kuniga
                await db.update_child_qarz(int(qarz), int(bola_id))
                qoldiq = await db.get_child_Qarz(bola_id)
                vznos_bola = await db.get_child_vznos(bola_id)
                caption = f"<b>{name[0]}</b>\n"
                caption += f"Ro'yxatdan o'tgan sanasi: {reg_date[0]}\n"
                caption += f"Guruhi: {group[0]}\n\n"
                caption += f"Oylik vznosi: <b>{vznos_bola[0]}-so'm</b>\n\n"
                caption += f"<b><i>Bugun vznos olishni unutmang!</i></b>\n\n"
                caption += f"💵 Olishingiz kerak bo'lgan summa: <b>{qoldiq[0]}-so'm</b>\n\n"
                caption += f"Bu oy <b>{ish_kunlari}</b>-ish kunidan iborat!\n\n"
                caption += f"Bugun bu oyning oxirgi ish kuni bo'lganligi sababli, bu bola qarzi 0-ga tenglashtirildi!"

                await bot.edit_message_caption(
                    chat_id=call.from_user.id,
                    message_id=call.message.message_id,
                    caption=caption
                )
                await db.update_child_qarz(0, int(bola_id))

            # hozirgi ish kuni ifelse
            else:
                current_date = datetime.now()
                year, month = current_date.year, current_date.month
                ish_kunlari = get_total_workdays(year, month)

                child_vznos = await db.get_child_vznos(bola_id)
                kuniga = child_vznos[0] / ish_kunlari
                kuniga = round(kuniga)

                original_qarz = await db.get_child_Qarz(bola_id)
                original_qarz = original_qarz[0]

                qarz = original_qarz + kuniga
                await db.update_child_qarz(int(qarz), int(bola_id))
                qoldiq = await db.get_child_Qarz(bola_id)
                vznos_bola = await db.get_child_vznos(bola_id)

                caption = f"<b>{name[0]}</b>\n"
                caption += f"Ro'yxatdan o'tgan sanasi: {reg_date[0]}\n"
                caption += f"Guruhi: {group[0]}\n\n"
                caption += f"Oylik vznosi: <b>{vznos_bola[0]}-so'm</b>\n\n"
                no = '0'
                caption += f"<b>💵 Qarzi: <i>{qoldiq[0] if qoldiq[0] else no}</i>-so'm</b>\n\n"
                caption += f"Bu oy <b>{ish_kunlari}</b>-ish kunidan iborat!\n\n"
                caption += f"Bugun bu oyninng <b>{hozirgi_ish_kuni}</b>-chi ish kuni!"

                await bot.edit_message_caption(
                    chat_id=call.from_user.id,
                    message_id=call.message.message_id,
                    caption=caption
                )
                await call.message.edit_reply_markup(edited_markup)

        else:
            name = await db.get_child_name_id(bola_id)
            reg_date = await db.get_child_regdate_id(bola_id)
            group = await db.get_child_group_id(bola_id)
            current_date = datetime.now()
            year, month = current_date.year, current_date.month
            hozirgi_ish_kuni = todaysWorkday(year, month)
            total_workdays = get_total_workdays(year, month)
            if hozirgi_ish_kuni == total_workdays:
                current_date = datetime.now()
                year, month = current_date.year, current_date.month
                ish_kunlari = get_total_workdays(year, month)

                child_vznos = await db.get_child_vznos(bola_id)
                kuniga = child_vznos[0] / ish_kunlari
                kuniga = round(kuniga)

                original_qarz = await db.get_child_Qarz(bola_id)
                original_qarz = original_qarz[0]

                qarz = original_qarz + kuniga
                await db.update_child_qarz(int(qarz), int(bola_id))
                qoldiq = await db.get_child_Qarz(bola_id)
                vznos_bola = await db.get_child_vznos(bola_id)
                caption = f"<b>{name[0]}</b>\n"
                caption += f"Ro'yxatdan o'tgan sanasi: {reg_date[0]}\n"
                caption += f"Guruhi: {group[0]}\n\n"
                caption += f"Oylik vznosi: <b>{vznos_bola[0]}-so'm</b>\n\n"
                caption += f"<b><i>Bugun vznos olishni unutmang!</i></b>\n\n"
                caption += f"💵 Olishingiz kerak bo'lgan summa: <b>{qoldiq[0]}-so'm</b>\n\n"
                caption += f"Bu oy <b>{ish_kunlari}</b>-ish kunidan iborat!\n\n"
                caption += f"Bugun bu oyning oxirgi ish kuni bo'lganligi sababli, bu bola qarzi 0-ga tenglashtirildi!"

                await bot.edit_message_caption(
                    chat_id=call.from_user.id,
                    message_id=call.message.message_id,
                    caption=caption
                )
                await db.update_child_qarz(0, int(bola_id))
                await db.add_payment_history(int(bola_id), qoldiq)


            else:
                current_date = datetime.now()
                year, month = current_date.year, current_date.month
                ish_kunlari = get_total_workdays(year, month)
                await db.add_attendance(int(bola_id), formatted_now, 0)
                edited_markup = InlineKeyboardMarkup(row_width=1)
                edited_markup.add(InlineKeyboardButton(text='❌ Kelmagan!', callback_data='kelmagan'))
                qoldiq = await db.get_child_Qarz(bola_id)
                vznos_bola = await db.get_child_vznos(bola_id)
                caption = f"<b>{name[0]}</b>\n"
                caption += f"Ro'yxatdan o'tgan sanasi: {reg_date[0]}\n"
                caption += f"Guruhi: {group[0]}\n\n"
                caption += f"Oylik vznosi: <b>{vznos_bola[0]}-so'm</b>\n\n"
                no = '0'
                caption += f"<b>💵 Qarzi: <i>{qoldiq[0] if qoldiq[0] else no}</i>-so'm</b>\n\n"
                caption += f"Bu oy <b>{ish_kunlari}</b>-ish kunidan iborat!\n\n"
                caption += f"Bugun bu oyning <b>{hozirgi_ish_kuni}</b>-chi ish kuni!"
                await bot.edit_message_caption(
                    chat_id=call.from_user.id,  # ID of the chat where the message is sent
                    message_id=call.message.message_id,  # ID of the message you want to edit
                    caption=caption  # The updated text for the message
                )
                await call.message.edit_reply_markup(edited_markup)
