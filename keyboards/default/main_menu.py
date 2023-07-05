from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='🔰 Davomat qilish')
        ],
        [
            KeyboardButton(text='👩‍🍼 Tarbiyachilar'),  # Tarbiyachi qo'shish/o'chirish & Tarbiyachi haqida ma'lumot
            KeyboardButton(text='👫 Bolalar')  # Bola qo'shish, o'chirish & Bola haqida ma'lumot
        ],
        [
            KeyboardButton(text='🏠 Guruhlar'),  # Guruh qo'shish/O'chirish & Guruh haqida ma'lumot
        ],
        [
            KeyboardButton(text="📊 Statistika ko'rish")
        ]
    ], resize_keyboard=True, one_time_keyboard=True
)
