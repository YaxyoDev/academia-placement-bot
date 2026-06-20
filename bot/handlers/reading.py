"""Reading seksiyasi (PHASE 3.3) — passage + MCQ savollar."""
import html

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.database import crud
from bot.handlers.quiz_engine import begin_section
from bot.keyboards.inline import reading_start_keyboard
from bot.states import TestStates

router = Router(name="reading")


async def start_reading(message: Message, state: FSMContext) -> None:
    passage = await crud.get_random_passage_with_questions()
    if not passage:
        await message.answer("📖 Reading: matn mavjud emas, bo'lim o'tkazib yuborildi.")
        await state.update_data(reading_correct=0, reading_total=0)
        from bot.handlers.listening import start_listening
        await start_listening(message, state)
        return

    # Savollarni keyin ishlatish uchun saqlab qo'yamiz
    await state.update_data(pending_reading=passage["questions"])
    await message.answer(
        f"📖 <b>Reading bo'limi</b>\n\n"
        f"<b>{html.escape(passage['title'])}</b>\n\n{html.escape(passage['text'])}",
        parse_mode="HTML",
        reply_markup=reading_start_keyboard(),
    )


@router.callback_query(F.data == "read_start")
async def reading_questions_start(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    questions = data.get("pending_reading", [])
    if callback.message:
        try:
            await callback.message.edit_reply_markup(reply_markup=None)
        except Exception:  # noqa: BLE001
            pass
    await callback.answer()
    if not questions:
        await state.update_data(reading_correct=0, reading_total=0)
        from bot.handlers.listening import start_listening
        await start_listening(callback.message, state)
        return
    await begin_section(callback.message, state, "reading", questions)
