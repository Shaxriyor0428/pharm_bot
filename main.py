import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config.env import BOT_TOKEN
from bot.services.api import close_client
from bot.start_router import router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def on_shutdown():
    await close_client()
    logger.info("🛑 Bot stopped")


async def main():
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
    # Eslatma: MemoryStorage — bot qayta ishga tushsa FSM holati (kutilayotgan
    # location/video) yo'qoladi; foydalanuvchi /start dan qayta boshlaydi.
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    dp.include_router(router)
    dp.shutdown.register(on_shutdown)

    logger.info("🚀 Bot started successfully!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
