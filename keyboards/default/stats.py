from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

stats = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Bugun kelganlar')
        ],
        [
            KeyboardButton(text='Bugungi kirim'),  # Tarbiyachi qo'shish/o'chirish & Tarbiyachi haqida ma'lumot
            KeyboardButton(text='Oy kirim')  # Bola qo'shish, o'chirish & Bola haqida ma'lumot
        ],
    ], resize_keyboard=True, one_time_keyboard=True
)
