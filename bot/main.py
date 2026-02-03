import asyncio
import logging
import sys
from pathlib import Path

# Add project root to path for direct execution
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from aiogram import Bot, Dispatcher, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Message

from bot.config import settings
from bot.database.models import Database
from bot.handlers import admin, chat_parser

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


async def main():
    """Main entry point."""
    logger.info("Starting bot...")
    logger.info(f"Admin IDs: {settings.admin_ids}")
    logger.info(f"RU Pay-in chat ID: {settings.ru_payin_chat_id}")
    logger.info(f"ENG Pay-in chat ID: {settings.eng_payin_chat_id}")
    logger.info(f"Pay-out chat ID: {settings.payout_chat_id}")
    
    # Ensure data directory exists
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # Initialize database
    db = Database(settings.database_url)
    await db.create_tables()
    logger.info("Database tables created")
    
    # Initialize bot with default properties
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    
    # Initialize dispatcher
    dp = Dispatcher()
    
    # Debug router - logs all messages (register last to not interfere)
    debug_router = Router(name="debug")
    
    @debug_router.message()
    async def debug_handler(message: Message):
        logger.info(
            f"[DEBUG] Chat ID: {message.chat.id}, "
            f"Type: {message.chat.type}, "
            f"From: {message.from_user.id if message.from_user else 'N/A'}, "
            f"Text: {message.text[:50] if message.text else 'None'}..."
        )
    
    # Register routers
    dp.include_router(admin.router)
    dp.include_router(chat_parser.router)
    dp.include_router(debug_router)  # Last - catches everything else
    
    try:
        logger.info("Bot started successfully")
        await dp.start_polling(bot, db=db)
    finally:
        await db.close()
        logger.info("Database connection closed")
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
