from aiogram.types import *
from aiogram import types
from aiogram.dispatcher import FSMContext
from datetime import datetime, date
from pytz import timezone
from keyboards.default.main_menu import main
from loader import dp, bot, db
from states.main_state import Main


@dp.message_handler(text='👫 Bolalar', state=Main.main_menu)
async def showGroupsFirst(message: Message, state: FSMContext):
    groups_markup = InlineKeyboardMarkup(row_width=2)
    groups = await db.get_all_groups()
    for group in groups:
        length = await db.count_ch_by_group(group[0])
        group_button = InlineKeyboardButton(text=f"{group[0]} ({length})", callback_data=f"group:{group[0]}")
        groups_markup.add(group_button)

    groups_markup.add(InlineKeyboardButton(text="🏠 Bosh menyu", callback_data='group:home'))

    await message.answer('🏠 Guruhni tanlang: ', reply_markup=groups_markup)
    await state.set_state("bola_group")


@dp.callback_query_handler(text_contains='group', state='bola_group')
async def show_children(call: CallbackQuery, state: FSMContext):
    data = call.data.rsplit(":")
    act = data[1]
    if act == 'home':
        await call.message.delete()
        await call.message.answer('🏠 Bosh menyu', reply_markup=main)
        await Main.main_menu.set()
    else:
        await state.update_data(
            {'group_name': act}
        )
        await call.message.delete()
        children_markup = InlineKeyboardMarkup(row_width=1)
        children = await db.get_children_byGroup(act)
        soni = len(children)
        for child in children:
            children_button = InlineKeyboardButton(text=child[0], callback_data=f"child:{child[0]}")
            children_markup.add(children_button)

        children_markup.add(InlineKeyboardButton(text="➕ Bola qo'shish", callback_data='child:add'))
        children_markup.add(InlineKeyboardButton(text="❌ Bola o'chirish", callback_data='child:remove'))
        children_markup.add(InlineKeyboardButton(text="⬅️ Ortga", callback_data="child:back"))

        await call.message.answer(f"<b>{act}</b>-guruhidagi bolalar,\nJami: {soni}-ta", reply_markup=children_markup)
        await state.set_state("bolalar_state")


@dp.callback_query_handler(text_contains='child', state='bolalar_state')
async def aboutChildren(call: CallbackQuery, state: FSMContext):
    data = call.data.rsplit(":")
    child_or_action = data[1]
    if child_or_action == 'back':
        await call.message.delete()
        groups_markup = InlineKeyboardMarkup(row_width=2)
        groups = await db.get_all_groups()
        for group in groups:
            length = await db.count_ch_by_group(group[0])
            group_button = InlineKeyboardButton(text=f"{group[0]} ({length})", callback_data=f"group:{group[0]}")
            groups_markup.add(group_button)

        groups_markup.add(InlineKeyboardButton(text="🏠 Bosh menyu", callback_data='group:home'))

        await call.message.answer('🏠 Guruhni tanlang: ', reply_markup=groups_markup)
        await state.set_state("bola_group")

    elif child_or_action == 'add':
        await call.message.delete()
        await call.message.answer("Bola to'liq ismini kiriting: ", reply_markup=ReplyKeyboardRemove())
        await state.set_state('get_child_name')

    elif child_or_action == 'remove':
        await call.message.delete()
        data = await state.get_data()
        gr = data.get('group_name')
        #wait call.message.delete()
        children_markup = InlineKeyboardMarkup(row_width=1)
        children = await db.get_children_byGroup(gr)
        for child in children:
            children_button = InlineKeyboardButton(text=child[0], callback_data=f"child:{child[0]}")
            children_markup.add(children_button)

        children_markup.add(InlineKeyboardButton(text="⬅️ Ortga", callback_data="delete:back"))

        await call.message.answer("O'chirmoqchi bo'lgan bola ustiga bosing: ", reply_markup=children_markup)
        await state.set_state('remove_ch')

    else:
        await call.message.delete()
        back_markup = InlineKeyboardMarkup(row_width=1)
        back_markup.add(InlineKeyboardButton(text="⬅️ Ortga", callback_data="orqaga"))
        child = await db.get_child_by_name(child_or_action)
        id = child[0]
        name = child[1]
        reg_date = child[2]
        group = child[3]
        photo = child[4]
        vznos = child[5]
        qarz = await db.get_child_Qarz(int(id))
        caption = f"<b>{name}</b>\n"
        caption += f"Ro'yxatdan o'tgan sanasi: {reg_date}\n"
        caption += f"Guruhi: {group}\n"
        caption += f"Oylik vznos: {vznos}\n\n"
        a = '0'
        caption += f"Qarzi: <b>{qarz[0] if qarz else a}</b>-so'm"


        file_id = photo.split('/')[-1].split('.')[0]

        await call.message.bot.send_photo(
            chat_id=call.message.chat.id,
            photo=file_id,
            caption=caption,
            reply_markup=back_markup
        )
        await state.set_state("goback")

@dp.callback_query_handler(text='orqaga', state="goback")
async def moveBack(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    gr = data.get('group_name')
    await call.message.delete()
    children_markup = InlineKeyboardMarkup(row_width=1)
    children = await db.get_children_byGroup(gr)
    soni = len(children)
    for child in children:
        children_button = InlineKeyboardButton(text=child[0], callback_data=f"child:{child[0]}")
        children_markup.add(children_button)

    children_markup.add(InlineKeyboardButton(text="➕ Bola qo'shish", callback_data='child:add'))
    children_markup.add(InlineKeyboardButton(text="❌ Bola o'chirish", callback_data='child:remove'))
    children_markup.add(InlineKeyboardButton(text="⬅️ Ortga", callback_data="child:back"))

    await call.message.answer(f"<b>{gr}</b>-guruhidagi bolalar,\nJami: {soni}-ta", reply_markup=children_markup)
    await state.set_state("bolalar_state")


@dp.callback_query_handler(text_contains='delete', state='remove_ch')
async def removeBola(call: CallbackQuery, state: FSMContext):
    data = call.data.rsplit(":")
    child = data[1]
    if child == 'back':
        data = await state.get_data()
        gr = data.get('group_name')
        await call.message.delete()
        children_markup = InlineKeyboardMarkup(row_width=1)
        children = await db.get_children_byGroup(gr)
        soni = len(children)
        for child in children:
            children_button = InlineKeyboardButton(text=child[0], callback_data=f"child:{child[0]}")
            children_markup.add(children_button)

        children_markup.add(InlineKeyboardButton(text="➕ Bola qo'shish", callback_data='child:add'))
        children_markup.add(InlineKeyboardButton(text="❌ Bola o'chirish", callback_data='child:remove'))
        children_markup.add(InlineKeyboardButton(text="⬅️ Ortga", callback_data="child:back"))

        await call.message.answer(f"<b>{gr}</b>-guruhidagi bolalar,\nJami: {soni}-ta", reply_markup=children_markup)
        await state.set_state("bolalar_state")


    else:
        data = await state.get_data()
        gr = data.get('group_name')
        await db.delete_child_by_name(child)
        await call.message.answer("✅ Bola muvaffaqiyatli o'chirildi!")
        children_markup = InlineKeyboardMarkup(row_width=1)
        children = await db.get_children_byGroup(gr)
        for child in children:
            children_button = InlineKeyboardButton(text=child[0], callback_data=f"child:{child[0]}")
            children_markup.add(children_button)

        children_markup.add(InlineKeyboardButton(text="🏠 Bosh menyu", callback_data='child:home'))
        await call.message.edit_reply_markup(children_markup)
        await state.set_state("remove_ch")


@dp.message_handler(state='get_child_name')
async def getChildName(message: Message, state: FSMContext):
    child_name = message.text
    is_child = await db.is_Child(child_name)
    if is_child is None:

        await state.update_data({'child_name': child_name})
        time_format = '%Y-%m-%d %H:%M:%S'
        formatted_now = datetime.now(timezone('Asia/Tashkent')).strftime(time_format)
        #datetime_object = datetime.strptime(formatted_now, "%Y-%m-%d %H:%M:%S")
        await state.update_data(
            {'reg_date': formatted_now}
        )

        d = await state.get_data()
        name = d.get('child_name')

        await message.answer(f"{name}-oylik vznosini kiriting:")
        await state.set_state("get_vznos")


    else:
        await message.answer(f"{child_name}-ismli bola bazada mavjud!\n\nQayta kiriting:")
        return



@dp.message_handler(state='get_vznos')
async def saveVznos(message: Message, state: FSMContext):
    vznos = message.text
    if vznos.isdigit():
        await state.update_data(
            {"bola_vznos": vznos}
        )
        d = await state.get_data()
        name = d.get('child_name')
        await message.answer(f"<b>{name}</b>-ni rasmini yuboring!")
        await state.set_state('get_child_photo')

    else:
        await message.answer("Summani kiritishda xatolik bor!\nIltimos, faqat sonlar kiriting!")
        return

# Handler for receiving a photo message
@dp.message_handler(content_types=types.ContentTypes.PHOTO, state="get_child_photo")
async def handle_photo(message: types.Message, state: FSMContext):
    # Save the photo to a file
    photo = message.photo[-1]  # Get the largest available photo
    photo_path = f"photos/{photo.file_id}.jpg"  # Path to save the photo
    await photo.download(destination_file=photo_path)

    data = await state.get_data()
    name = data.get('child_name')
    reg_date = data.get('reg_date')
    group_name = data.get('group_name')
    vznos = data.get('bola_vznos')

    #print(type(reg_date))
    await db.add_child(name, reg_date, group_name, photo_path, int(vznos))
    await message.answer("Bola bazaga qo'shildi!")


    caption = f"<b>{name}</b>\n"
    caption += f"Ro'yxatdan o'tgan sanasi: {reg_date}\n"
    caption += f"Guruhi: {group_name}\n"
    caption += f"Oylik vznos: {vznos}"

    # Send the photo using send_photo
    await message.bot.send_photo(
        chat_id=message.chat.id,
        photo=types.InputFile(photo_path),
        caption=caption
    )

    children_markup = InlineKeyboardMarkup(row_width=1)
    children = await db.get_children_byGroup(group_name)
    soni = len(children)
    for child in children:
        children_button = InlineKeyboardButton(text=child[0], callback_data=f"child:{child[0]}")
        children_markup.add(children_button)

    children_markup.add(InlineKeyboardButton(text="➕ Bola qo'shish", callback_data='child:add'))
    children_markup.add(InlineKeyboardButton(text="❌ Bola o'chirish", callback_data='child:remove'))
    children_markup.add(InlineKeyboardButton(text="⬅️ Ortga", callback_data="child:back"))

    await message.answer(f"<b>{group_name}</b>-guruhidagi bolalar,\nJami: {soni}-ta", reply_markup=children_markup)
    await state.set_state("bolalar_state")

