from aiogram.types import *
from aiogram.dispatcher import FSMContext

from keyboards.default.main_menu import main
from loader import dp, bot, db
from states.main_state import Main


@dp.message_handler(text='🏠 Guruhlar', state=Main.main_menu)
async def show_groups(message: Message, state: FSMContext):
    groups_markup = InlineKeyboardMarkup(row_width=2)
    groups = await db.get_all_groups()
    for group in groups:
        group_button = InlineKeyboardButton(text=group[0], callback_data=f"group:{group[0]}")
        groups_markup.add(group_button)

    groups_markup.add(InlineKeyboardButton(text="➕ Guruh qo'shish", callback_data='group:add'))
    groups_markup.add(InlineKeyboardButton(text="❌ Guruh o'chirish", callback_data='group:remove'))
    groups_markup.add(InlineKeyboardButton(text="🏠 Bosh menyu", callback_data='group:home'))

    await message.answer('🏠 Guruhlar: ', reply_markup=groups_markup)
    await state.set_state("groups_state")


@dp.callback_query_handler(text_contains='group', state='groups_state')
async def next_t_step(call: CallbackQuery, state: FSMContext):
    data = call.data.rsplit(":")
    name_or_act = data[1]
    if name_or_act == 'add':
        await call.message.delete()
        await call.message.answer("Guruh nomini kiriting:")
        await state.set_state('get_g_name')

    elif name_or_act == 'remove':
        t = await db.get_all_groups()
        if len(t) == 0:
            await call.message.answer("Hamma guruhlar o'chirilgan!")
            await call.message.answer('🏠 Bosh menyu', reply_markup=main)
            await Main.main_menu.set()
        else:
            groups_markup = InlineKeyboardMarkup(row_width=2)
            groups = await db.get_all_groups()
            for group in groups:
                group_button = InlineKeyboardButton(text=group[0], callback_data=f"group:{group[0]}")
                groups_markup.add(group_button)

            await call.message.answer("O'chirmoqchi bo'lgan guruhni tanlang: ", reply_markup=groups_markup)
            await state.set_state("groups_delete")

    elif name_or_act == 'home':
        await call.message.delete()
        await call.message.answer('🏠 Bosh menyu', reply_markup=main)
        await Main.main_menu.set()
    else:
        pass


@dp.message_handler(state='get_g_name')
async def get_groupName(message: Message, state: FSMContext):
    name = message.text
    await state.update_data(
        {'group_name': name}
    )
    teachers_markup = InlineKeyboardMarkup(row_width=1)
    teachers = await db.get_all_teachers()
    print(teachers)
    for teacher in teachers:
        teacher_button = InlineKeyboardButton(text=teacher[0], callback_data=f"teacher:{teacher[0]}")
        teachers_markup.add(teacher_button)
    await message.answer('Guruh tarbiyachisini tanlang: ', reply_markup=teachers_markup)
    await state.set_state('get_t_group')


@dp.callback_query_handler(text_contains='teacher', state='get_t_group')
async def getTeachergroup(call: CallbackQuery, state: FSMContext):
    data = call.data.rsplit(":")
    teacher = data[1]
    datta = await state.get_data()
    group_name = datta.get('group_name')
    await db.add_group(group_name, teacher)
    await call.message.delete()
    await call.message.answer("✅ Guruh muvaffaqiyatli qo'shildi!")
    await call.message.answer('🏠 Bosh menyu', reply_markup=main)
    await Main.main_menu.set()


@dp.callback_query_handler(text_contains='group', state='groups_delete')
async def deleteTeacherss(call: CallbackQuery, state: FSMContext):
    data = call.data.rsplit(":")
    teacher = data[1]
    await db.delete_group_by_name(teacher)
    await call.message.answer("✅ Guruh muvaffaqiyatli o'chirildi!")
    groups_markup = InlineKeyboardMarkup(row_width=2)
    groups = await db.get_all_groups()
    for teacher in groups:
        teacher_button = InlineKeyboardButton(text=teacher[0], callback_data=f"del:{teacher[0]}")
        groups_markup.add(teacher_button)
        if len(groups) == 0:
            await call.message.answer("Hamma guruhlar o'chirildi!")
            await call.message.answer('🏠 Bosh menyu', reply_markup=main)
            await Main.main_menu.set()

    await call.message.edit_reply_markup(groups_markup)
    await state.set_state("groups_delete")
