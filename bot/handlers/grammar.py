"""Grammar seksiyasi (PHASE 3.2) — 20 ta MCQ savol."""
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.database import crud
from bot.handlers.quiz_engine import begin_section

router = Router(name="grammar")


async def start_grammar(message: Message, state: FSMContext) -> None:
    questions = await crud.get_random_grammar(20)
    if not questions:
        await message.answer("📝 Grammar: savollar mavjud emas, bo'lim o'tkazib yuborildi.")
        await state.update_data(grammar_correct=0, grammar_total=0)
        from bot.handlers.reading import start_reading
        await start_reading(message, state)
        return
    await message.answer("📝 <b>Grammar bo'limi boshlandi</b>", parse_mode="HTML")
    await begin_section(message, state, "grammar", questions)
