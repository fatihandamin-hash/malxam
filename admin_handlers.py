from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from config import ADMIN_IDS, ADMIN_GROUP_ID
from database.db import get_stats, get_users_by_gender, update_user_status, get_user, set_verified_surah_count, get_user_submissions, reset_all_data
from keyboards.builders import admin_count_keyboard, admin_panel_keyboard, contact_admin_keyboard, confirm_reset_keyboard
from states import AdminStates
import os


router = Router()
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")

def is_admin(user_id):
    return user_id in ADMIN_IDS

@router.message(Command("admin"))
async def cmd_admin(message: Message):
    if not is_admin(message.from_user.id):
        return
    await show_admin_panel(message)

async def show_admin_panel(message: Message):
    total, pending, approved = await get_stats()
    msg = (
        "🛡️ ADMIN ПАНЕЛЬ\n\n"
        f"📊 СТАТИСТИКА:\n"
        f"- Всего участников: {total}\n"
        f"- На проверке: {pending}\n"
        f"- Одобрено: {approved}\n\n"
        "Выберите действие:"
    )
    await message.answer(msg, reply_markup=admin_panel_keyboard())

@router.callback_query(F.data == "admin_refresh")
async def callback_refresh(callback: CallbackQuery):
    total, pending, approved = await get_stats()
    msg = (
        "🛡️ ADMIN ПАНЕЛЬ\n\n"
        f"📊 СТАТИСТИКА:\n"
        f"- Всего участников: {total}\n"
        f"- На проверке: {pending}\n"
        f"- Одобрено: {approved}\n\n"
        "Выберите действие:"
    )
    await callback.message.edit_text(msg, reply_markup=admin_panel_keyboard())

@router.callback_query(F.data.startswith("verify_"))
async def callback_verify(callback: CallbackQuery, bot: Bot):
    action, decision, user_id_str = callback.data.split("_")
    user_id = int(user_id_str)
    
    if ADMIN_IDS and callback.from_user.id not in ADMIN_IDS:
        await callback.answer("⛔ Только админы могут это делать", show_alert=True)
        return

    if decision == "approve":
        # Ask for count
        await callback.message.edit_text(
            f"✅ Одобрение участника {user_id}.\n"
            "Сколько СУР он прочитал правильно? (Выберите или введите вручную)",
            reply_markup=admin_count_keyboard(user_id)
        )
    else:
        await update_user_status(user_id, "rejected")
        await bot.send_message(user_id, "❌ Ваша заявка была отклонена администратором.")
        await callback.message.edit_text(
            f"{callback.message.text}\n\n"
            f"Решение: ❌ ОТКЛОНЕНО (Админ: {callback.from_user.full_name})"
        )
    await callback.answer()

@router.callback_query(F.data.startswith("count_"))
async def callback_count(callback: CallbackQuery, state: FSMContext, bot: Bot):
    # count_{user_id}_{count|manual}
    parts = callback.data.split("_")
    user_id = int(parts[1])
    value = parts[2]
    
    if value == "manual":
        await callback.message.edit_text(f"Введите количество сур для участника {user_id} (числом):")
        await state.update_data(target_user_id=user_id)
        await state.set_state(AdminStates.waiting_for_count)
    else:
        count = int(value)
        await finalize_approval(bot, callback.message, user_id, count, callback.from_user.full_name)
    
    await callback.answer()

@router.message(AdminStates.waiting_for_count)
async def manual_count_input(message: Message, state: FSMContext, bot: Bot):
    try:
        count = int(message.text)
        data = await state.get_data()
        user_id = data['target_user_id']
        
        await finalize_approval(bot, message, user_id, count, message.from_user.full_name)
        await state.clear()
    except ValueError:
        await message.answer("❌ Введите число!")

async def finalize_approval(bot: Bot, message: Message, user_id: int, count: int, admin_name: str):
    await update_user_status(user_id, "approved")
    await set_verified_surah_count(user_id, count)
    
    # Notify User
    await bot.send_message(
        user_id, 
        f"✅ Ваша заявка ОДОБРЕНА!\n"
        f"📖 Засчитано сур: {count}\n\n"
        f"Если есть вопросы, пишите: @{ADMIN_USERNAME}",
        reply_markup=contact_admin_keyboard(ADMIN_USERNAME)
    )
    
    # Update Admin Message
    # If message is from callback (edit_text) or reply (answer)
    # We can't easily edit the original message if it was a reply to a text input.
    # But if it was a callback, we can edit.
    try:
        await message.edit_text(
            f"✅ Участник {user_id} ОДОБРЕН.\n"
            f"📖 Сур: {count}\n"
            f"Админ: {admin_name}"
        )
    except:
        await message.answer(
            f"✅ Участник {user_id} ОДОБРЕН.\n"
            f"📖 Сур: {count}\n"
            f"Админ: {admin_name}"
        )

@router.callback_query(F.data.startswith("winner_"))
async def callback_winner_list(callback: CallbackQuery):
    gender = "male" if callback.data == "winner_male" else "female"
    gender_text = "Мужчины" if gender == "male" else "Женщины"
    
    users = await get_users_by_gender(gender)
    
    if not users:
        await callback.answer("Нет одобренных участников в этой категории", show_alert=True)
        return

    text = f"🏆 КАНДИДАТЫ ({gender_text}):\n\n"
    text += "ID | Имя | Сур\n"
    text += "---|-----|----\n"
    
    # Limit to top 20
    for u in users[:20]:
        text += f"{u['user_id']} | {u['full_name'][:10]} | {u['verified_surah_count']}\n"
        
    text += "\nДля выбора победителя используйте команду:\n/win [user_id]"
    
    await callback.message.edit_text(text, reply_markup=admin_panel_keyboard())

@router.message(Command("win"))
async def cmd_win(message: Message, bot: Bot):
    if not is_admin(message.from_user.id):
        return
        
    try:
        args = message.text.split()
        if len(args) < 2:
            await message.answer("⚠️ Использование: /win [user_id]")
            return
            
        winner_id = int(args[1])
        user = await get_user(winner_id)
        
        if not user:
            await message.answer("❌ Пользователь не найден")
            return
            
        await message.answer(
            "🎉 ПОБЕДИТЕЛЬ ВЫБРАН!\n"
            f"Имя: @{user['username']} ({user['full_name']})\n"
            f"Категория: {user['gender']}\n"
            f"Сур (подтверждено): {user['verified_surah_count']}\n\n"
            "🏆 Награда: Gemini Pro на 1 год"
        )
        
        await bot.send_message(
            winner_id,
            "🎉 ПОЗДРАВЛЯЕМ! ТЫ ПОБЕДИТЕЛЬ!\n\n"
            "Ты выиграл **Gemini Pro на 1 год**!\n\n"
            f"Администратор @{ADMIN_USERNAME} свяжется с тобой для передачи приза. 🤲"
        )
        
    except ValueError:
        await message.answer("❌ ID должен быть числом")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")

@router.message(Command("reset_contest"))
async def cmd_reset_contest(message: Message):
    if not is_admin(message.from_user.id):
        return
    
    await message.answer(
        "⚠️ **ВНИМАНИЕ! ЭТО ОПАСНОЕ ДЕЙСТВИЕ!** ⚠️\n\n"
        "Вы собираетесь полностью **УДАЛИТЬ ВСЕХ УЧАСТНИКОВ** и все их данные.\n"
        "Конкурс начнется с чистого листа.\n\n"
        "Вы уверены?",
        reply_markup=confirm_reset_keyboard()
    )

@router.callback_query(F.data == "confirm_global_reset")
async def callback_confirm_reset(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return

    await reset_all_data()
    await callback.message.edit_text("✅ **БАЗА ДАННЫХ ОЧИЩЕНА!**\nКонкурс начат заново.")
    await callback.answer()

@router.callback_query(F.data == "cancel_global_reset")
async def callback_cancel_reset(callback: CallbackQuery):
    await callback.message.edit_text("❌ Сброс отменен.")
    await callback.answer()

