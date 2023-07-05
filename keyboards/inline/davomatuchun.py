from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def davomat(bola_id):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.insert(InlineKeyboardButton(text="✅ Keldi", callback_data=f"davomat:yes:{bola_id}"))
    markup.insert(InlineKeyboardButton(text="❌ Kelmadi", callback_data=f"davomat:no:{bola_id}"))
    return markup




def pulni_oldim(bola_id):
    get_markup = InlineKeyboardMarkup(row_width=1)
    get_markup.insert(InlineKeyboardButton(text="💰 Pulni oldim", callback_data=f"oldim:{bola_id}"))
    return get_markup