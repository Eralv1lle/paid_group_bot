from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def setup_join_kb(user_id):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Принять", callback_data=f"confirm:{user_id}"),
             InlineKeyboardButton(text="❌ Отклонить", callback_data=f"cancel:{user_id}")]
        ]
    )