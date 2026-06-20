"""Writing seksiyasi (PHASE 3.5) — Gemini baholaydi."""
import html

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.database import crud
from bot.services.gemini_service import evaluate_writing
from bot.states import TestStates

router = Router(name="writing")


async def start_writing(message: Message, state: FSMContext) -> None:
    topic = await crud.get_random_writing_topic()
    if not topic:
        await message.answer("✍️ Writing: mavzu mavjud emas, bo'lim o'tkazib yuborildi.")
        await state.update_data(writing_score=0, writing_feedback="Mavzu mavjud emas edi.")
        from bot.handlers.speaking import start_speaking
        await start_speaking(message, state)
        return

    await state.update_data(writing_topic=topic["text"])
    await state.set_state(TestStates.writing)
    await message.answer(
        f"✍️ <b>Writing bo'limi</b>\n\n"
        f"<b>Mavzu:</b> {html.escape(topic['text'])}\n\n"
        f"Iltimos, shu mavzuda ingliz tilida insho yozing (kamida 100 so'z) "
        f"va matn ko'rinishida yuboring.",
        parse_mode="HTML",
    )


@router.message(TestStates.writing, F.text)
async def receive_writing(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    topic = data.get("writing_topic", "")
    await message.answer("⏳ Insho baholanmoqda...")

    score, feedback = await evaluate_writing(topic, message.text)
    await state.update_data(writing_score=score, writing_feedback=feedback)

    from bot.handlers.speaking import start_speaking
    await start_speaking(message, state)


@router.message(TestStates.writing)
async def writing_wrong_type(message: Message, state: FSMContext) -> None:
    await message.answer("✍️ Iltimos, inshoni matn ko'rinishida yozib yuboring.")
