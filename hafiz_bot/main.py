import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from database.db import init_db
from handlers import user_handlers, admin_handlers

async def main():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    
    if not BOT_TOKEN:
        print("Error: BOT_TOKEN is not set in .env or config.py")
        return

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    
    dp.include_router(user_handlers.router)
    dp.include_router(admin_handlers.router)
    
    await init_db()
    
    print("Bot started...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped")
