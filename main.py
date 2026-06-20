"""Bot kirish nuqtasi — polling (PHASE 2, 7).

Ishga tushirish: PlacementBot papkasidan turib
    python main.py
"""
import os
import sys

# main.py loyiha ildizida turadi — `bot` paketi topilishi uchun shu papkani
# sys.path ga qo'shamiz (qaysi papkadan ishga tushirilishidan qat'i nazar ishlaydi).
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    BotCommand,
    BotCommandScopeChat,
    BotCommandScopeDefault,
)

from bot.config import config
from bot.database import crud
from bot.database.engine import init_db
from bot.admin import handlers as admin_handlers
from scripts.seed import GRAMMAR
from bot.handlers import (
    grammar,
    listening,
    quiz_engine,
    reading,
    result,
    speaking,
    start,
    writing,
)


# Oddiy foydalanuvchilar ko'radigan menyu komandalar
USER_COMMANDS = [
    BotCommand(command="start", description="Testni boshlash"),
    BotCommand(command="restart", description="Testni boshqatdan boshlash"),
    BotCommand(command="help", description="Qo'llanma"),
]

# Superadmin qo'shimcha ko'radigan komandalar
ADMIN_COMMANDS = USER_COMMANDS + [
    BotCommand(command="admin", description="Admin panel"),
    BotCommand(command="overall", description="Umumiy statistika"),
]


async def setup_commands(bot: Bot) -> None:
    """Telegram menyu komandalarini o'rnatish."""
    await bot.set_my_commands(USER_COMMANDS, scope=BotCommandScopeDefault())
    if config.superadmin_id:
        try:
            await bot.set_my_commands(
                ADMIN_COMMANDS, scope=BotCommandScopeChat(chat_id=config.superadmin_id)
            )
        except Exception:  # noqa: BLE001
            # Superadmin hali bot bilan suhbat ochmagan bo'lishi mumkin — muhim emas
            pass


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    await init_db()

    # Grammar savollari seed.py dagi GRAMMAR ro'yxatidan avto-sinxronlanadi.
    # Savolni o'zgartirish uchun scripts/seed.py ni tahrirlab, botni qayta ishga tushiring.
    count = await crud.sync_grammar_questions(GRAMMAR)
    logging.getLogger(__name__).info("Grammar savollari sinxronlandi: %d ta", count)

    session = AiohttpSession()
    if config.disable_ssl_verify:
        # Bu mashinada CA sertifikat ishlamaydi (korporativ proksi). VPS da o'chirib qo'ying.
        session._connector_init["ssl"] = False
        logging.getLogger(__name__).warning("SSL tekshiruvi o'chirilgan (DISABLE_SSL_VERIFY).")

    bot = Bot(
        token=config.bot_token,
        session=session,
        default=DefaultBotProperties(parse_mode=None),
    )
    dp = Dispatcher(storage=MemoryStorage())

    # Router tartibi muhim: admin → start → quiz engine → seksiyalar
    dp.include_router(admin_handlers.router)
    dp.include_router(start.router)
    dp.include_router(quiz_engine.router)
    dp.include_router(grammar.router)
    dp.include_router(reading.router)
    dp.include_router(listening.router)
    dp.include_router(writing.router)
    dp.include_router(speaking.router)
    dp.include_router(result.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await setup_commands(bot)
    logging.getLogger(__name__).info("Bot ishga tushdi (polling).")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.getLogger(__name__).info("Bot to'xtatildi.")
