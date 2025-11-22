from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from config import CHANNEL_ID, ADMIN_GROUP_ID, ADMIN_IDS
from keyboards.builders import check_sub_keyboard, gender_keyboard, recording_keyboard, admin_verification_keyboard, contact_admin_keyboard

from database.db import add_user, update_user_gender, update_user_status, add_submission, get_user_submissions, get_user, delete_user_data
from states import Registration
import datetime
import os

router = Router()

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin") # Fallback

async def is_subscribed(bot: Bot, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        print(f"Error checking subscription: {e}")
        return False

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, bot: Bot):
    await state.clear()
    user_id = message.from_user.id
    
    # Check if user already exists and has a status that prevents re-submission
    user = await get_user(user_id)
    if user and user['status'] in ['pending', 'approved', 'rejected']:
        status_msg = {
            'pending': "⏳ Ваша заявка уже на проверке. Ожидайте.",
            'approved': "✅ Вы уже участвуете в конкурсе!",
            'rejected': "❌ Ваша заявка была отклонена."
        }
        await message.answer(
            status_msg.get(user['status'], "Вы уже зарегистрированы.") + 
            "\n\n🔄 Если вы хотите начать заново (сбросить прогресс), отправьте команду /reset"
        )
        return

    await add_user(user_id, message.from_user.username, message.from_user.full_name)

    
    if await is_subscribed(bot, user_id):
        await message.answer(
            "Ассаламу алейкум! 👋\n"
            "Добро пожаловать на 'HAFIZ CHALLENGE'!\n\n"
            "✅ Подписка проверена!\n"
            "Теперь выбери свой пол:",
            reply_markup=gender_keyboard()
        )
        await state.set_state(Registration.waiting_for_gender)
    else:
        await message.answer(
            "Ассаламу алейкум! 👋\n"
            "Добро пожаловать на 'HAFIZ CHALLENGE'!\n\n"
            "⚠️ ВАЖНО: Ты должен быть подписан на наш канал\n"
            "Проверяю подписку...",
            reply_markup=check_sub_keyboard()
        )

@router.callback_query(F.data == "check_subscription")
async def callback_check_sub(callback: CallbackQuery, state: FSMContext, bot: Bot):
    if await is_subscribed(bot, callback.from_user.id):
        await callback.message.edit_text(
            "✅ Подписка проверена!\n"
            "Теперь выбери свой пол:",
            reply_markup=gender_keyboard()
        )
        await state.set_state(Registration.waiting_for_gender)
    else:
        await callback.answer("❌ Вы все еще не подписаны!", show_alert=True)

@router.message(Command("reset"))
async def cmd_reset(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        return
        
    await state.clear()
    await delete_user_data(message.from_user.id)
    await message.answer(
        "🔄 [ADMIN] Ваш прогресс сброшен.\n"
        "Вы можете начать заново через /start"
    )


@router.callback_query(F.data.startswith("gender_"))

async def callback_gender(callback: CallbackQuery, state: FSMContext):
    gender = "male" if callback.data == "gender_male" else "female"
    gender_text = "Мужской" if gender == "male" else "Женский"
    
    await update_user_gender(callback.from_user.id, gender)
    
    await callback.message.edit_text(
        f"Выбрано: {gender_text}\n\n"
        "⚠️ **ВАЖНОЕ ПРАВИЛО** ⚠️\n"
        "Ты должен прочитать **ВСЕ** суры, которые знаешь наизусть, **ПРЯМО СЕЙЧАС**.\n"
        "У тебя будет только **ОДНА ПОПЫТКА**.\n"
        "Потом добавить суры будет **НЕЛЬЗЯ**.\n\n"
        "Каждую суру отправляй отдельным голосовым сообщением.\n"
        "Когда закончишь все, нажми кнопку '✅ Завершить отправку'."
    )
    await callback.message.answer("👇 Начинай отправлять голосовые:", reply_markup=recording_keyboard())
    await state.set_state(Registration.collecting_voices)
    await callback.answer()

@router.message(Registration.collecting_voices, F.voice)
async def handle_voice(message: Message):
    await add_submission(message.from_user.id, message.voice.file_id)
    await message.answer("✅ Получено. Отправь следующую или нажми 'Завершить отправку'")

@router.message(Registration.collecting_voices, F.text == "✅ Завершить отправку")
async def finish_recording(message: Message, state: FSMContext, bot: Bot):
    user_id = message.from_user.id
    submissions = await get_user_submissions(user_id)
    
    if not submissions:
        await message.answer("⚠️ Ты не отправил ни одной суры! Отправь хотя бы одну.")
        return

    await update_user_status(user_id, "pending")
    
    user = await get_user(user_id)
    gender_text = "Мужской" if user['gender'] == "male" else "Женский"
    
    await message.answer(
        "✅ Все голосовые получены!\n\n"
        f"📊 Статистика:\n"
        f"📱 Пол: {gender_text}\n"
        f"🎤 Файлов отправлено: {len(submissions)}\n"
        f"🕐 Время: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        "Отправляю на проверку... ⏳\n"
        "Если возникнут вопросы, свяжись с админом.",
        reply_markup=contact_admin_keyboard(ADMIN_USERNAME)
    )
    
    # Send to Admin Group
    admin_msg = (
        "🎤 НОВАЯ ЗАПИСЬ ДЛЯ ПРОВЕРКИ\n\n"
        f"👤 Участник: @{message.from_user.username or 'NoUsername'} ({message.from_user.full_name})\n"
        f"📱 ID: {user_id}\n"
        f"👨/👩 Категория: {gender_text}\n"
        f"📊 Файлов: {len(submissions)}\n"
        f"🕐 Время отправки: {datetime.datetime.now().strftime('%H:%M')}\n\n"
        "📌 ГОЛОСОВЫЕ СООБЩЕНИЯ:"
    )
    
    await bot.send_message(ADMIN_GROUP_ID, admin_msg)
    
    for file_id in submissions:
        await bot.send_voice(ADMIN_GROUP_ID, file_id)
        
    await bot.send_message(
        ADMIN_GROUP_ID, 
        "✅ Проверь качество чтения\n❌ Если не подходит - отклони",
        reply_markup=admin_verification_keyboard(user_id)
    )
    
    await message.answer(
        "✅ Ваше чтение отправлено на проверку!\n\n"
        "📋 Статус: ⏳ На проверке\n"
        "🏆 Ожидание результатов\n\n"
        "Спасибо за участие! 🤲"
    )
    await state.clear()
