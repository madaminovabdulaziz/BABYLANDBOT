from aiogram.types import *
from aiogram.dispatcher import FSMContext
from keyboards.default.main_menu import main
from loader import dp, bot, db
from states.main_state import Main


@dp.message_handler(text="👩‍🍼 Tarbiyachilar", state=Main.main_menu)
async def show_t(message: Message, state: FSMContext):
    teachers_markup = InlineKeyboardMarkup(row_width=2)
    teachers = await db.get_all_teachers()
    for teacher in teachers:
        teacher_button = InlineKeyboardButton(text=teacher[0], callback_data=f"teacher:{teacher[0]}")
        teachers_markup.add(teacher_button)

    teachers_markup.add(InlineKeyboardButton(text="➕ Tarbiyachi qo'shish", callback_data='teacher:add'))
    teachers_markup.add(InlineKeyboardButton(text="❌ Tarbiyachi o'chirish", callback_data='teacher:remove'))
    teachers_markup.add(InlineKeyboardButton(text="🏠 Bosh menyu", callback_data='teacher:home'))

    await message.answer('👩‍🍼 Tarbiyachilar: ', reply_markup=teachers_markup)
    await state.set_state("teachers_state")


@dp.callback_query_handler(text_contains='teacher', state='teachers_state')
async def next_t_step(call: CallbackQuery, state: FSMContext):
    data = call.data.rsplit(":")
    name_or_act = data[1]
    if name_or_act == 'add':
        await call.message.delete()
        await call.message.answer("Tarbiyachi to'liq ismini kiriting:\n\nMisol: <b>Aziza Azizova</b>")
        await state.set_state('get_t_name')

    elif name_or_act == 'remove':
        t = await db.get_all_teachers()
        if len(t) == 0:
            await call.message.answer("Hamma tarbiyachilar o'chirilgan!")
            await call.message.answer('🏠 Bosh menyu', reply_markup=main)
            await Main.main_menu.set()
        else:
            teachers_markup = InlineKeyboardMarkup(row_width=2)
            teachers = await db.get_all_teachers()
            for teacher in teachers:
                teacher_button = InlineKeyboardButton(text=teacher[0], callback_data=f"del:{teacher[0]}")
                teachers_markup.add(teacher_button)



            await call.message.answer("O'chirmoqchi bo'lgan tarbiyachini tanlang: ", reply_markup=teachers_markup)
            await state.set_state("teachers_delete")


    elif name_or_act == 'home':
        await call.message.delete()
        await call.message.answer('🏠 Bosh menyu', reply_markup=main)
        await Main.main_menu.set()

    else:
        pass


@dp.message_handler(state='get_t_name')
async def get_teacherName(message: Message, state: FSMContext):
    name = message.text
    if len(name.split()) == 2:
        await state.update_data(
            {'name': name}
        )
        await message.answer('Tarbiyachi telefon raqamini kiriting: ')
        await state.set_state('get_t_num')
    else:
        await message.answer("Tarbiyachi to'liq ismini kiriting!\n\nMisol: <b>Aziza Azizova</b>")
        return


@dp.message_handler(state='get_t_num')
async def get_teacherNum(message: Message, state: FSMContext):
    number = message.text
    if number.isdigit():
        data = await state.get_data()
        name = data.get('name')
        is_T = await db.get_teacher_name(name)
        if is_T is None:
            await db.add_teacher(name, number)
            await message.answer("✅ Tarbiyachi muvaffaqiyatli qo'shildi!")
            await message.answer('🏠 Bosh menyu', reply_markup=main)
            await Main.main_menu.set()
        else:
            await message.answer("Bunday ismli tarbiyachi bazada mavjud!\n\nBoshqa tarbiyachi qo'shing!")
            await message.answer("Tarbiyachi to'liq ismini kiriting:\n\nMisol: <b>Aziza Azizova</b>")
            await state.set_state('get_t_name')
    else:
        await message.answer('Telefon raqamda xatolik bor!\nQayta kiriting!')
        return


@dp.callback_query_handler(text_contains='del', state='teachers_delete')
async def deleteTeacherss(call: CallbackQuery, state: FSMContext):
    data = call.data.rsplit(":")
    teacher = data[1]
    gr_name = await db.get_group_name_by_teacher(teacher)
    await db.delete_teacher_by_name(teacher)
    await db.delete_group_by_teacher(teacher)
    await db.delete_children_by_Group(gr_name[0])
    await call.message.answer("✅ Tarbiyachi muvaffaqiyatli o'chirildi!")
    teachers_markup = InlineKeyboardMarkup(row_width=2)
    teachers = await db.get_all_teachers()
    for teacher in teachers:
        teacher_button = InlineKeyboardButton(text=teacher[0], callback_data=f"del:{teacher[0]}")
        teachers_markup.add(teacher_button)
        if len(teachers) == 0:
            await call.message.answer("Hamma tarbiyachilar o'chirildi!")
            await call.message.answer('🏠 Bosh menyu', reply_markup=main)
            await Main.main_menu.set()

    await call.message.edit_reply_markup(teachers_markup)
    await state.set_state("teachers_delete")

