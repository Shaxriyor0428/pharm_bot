import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from bot.config.database import init_db, close_db
from bot.config.env import BOT_TOKEN
from bot.start_router import router


async def on_startup():
    await init_db()
    print("✅ Database connected")

async def on_shutdown():
    await close_db()
    print("❌ Database closed")


async def main():
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    dp.include_router(router)

    # startup & shutdown handlers
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    print("🚀 Bot started successfully!")
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Bot stopped")
