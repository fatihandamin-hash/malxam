from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from config import CHANNEL_URL

def check_sub_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Подписаться на канал", url=CHANNEL_URL)],
        [InlineKeyboardButton(text="✅ Я подписался", callback_data="check_subscription")]
    ])

def gender_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="👨 Мужской", callback_data="gender_male"),
            InlineKeyboardButton(text="👩 Женский", callback_data="gender_female")
        ]
    ])

def recording_keyboard():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="✅ Завершить отправку")]
    ], resize_keyboard=True)

def admin_verification_keyboard(user_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Одобрить", callback_data=f"verify_approve_{user_id}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"verify_reject_{user_id}")
        ]
    ])

def admin_count_keyboard(user_id):
    # Buttons for 1-10, and a manual input option
    buttons = []
    row1 = [InlineKeyboardButton(text=str(i), callback_data=f"count_{user_id}_{i}") for i in range(1, 6)]
    row2 = [InlineKeyboardButton(text=str(i), callback_data=f"count_{user_id}_{i}") for i in range(6, 11)]
    row3 = [InlineKeyboardButton(text="Ввести вручную", callback_data=f"count_{user_id}_manual")]
    
    return InlineKeyboardMarkup(inline_keyboard=[row1, row2, row3])

def admin_panel_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Обновить статистику", callback_data="admin_refresh")],
        [
            InlineKeyboardButton(text="🏆 Победитель (М)", callback_data="winner_male"),
            InlineKeyboardButton(text="🏆 Победитель (Ж)", callback_data="winner_female")
        ]
    ])

def contact_admin_keyboard(admin_username):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🆘 Написать админу", url=f"https://t.me/{admin_username}")]
    ])

def confirm_reset_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚠️ ДА, СБРОСИТЬ ВСЕХ", callback_data="confirm_global_reset")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_global_reset")]
    ])

