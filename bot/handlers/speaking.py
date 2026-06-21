"""Speaking seksiyasi (PHASE 3.6) — har topic uchun ovozli javob, Gemini baholaydi."""
import html
from io import BytesIO

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.database import crud
from bot.keyboards.inline import speaking_skip_keyboard
from bot.services.gemini_service import evaluate_speaking
from bot.states import TestStates

router = Router(name="speaking")


async def _send_topic(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    topics = data["speaking_topics"]
    idx = data["speaking_index"]
    topic = topics[idx]
    await message.answer(
        f"🎤 <b>Speaking bo'limi</b>\n"
        f"Mavzu {idx + 1}/{len(topics)}\n\n"
        f"<b>{html.escape(topic['text'])}</b>\n\n"
        f"Iltimos, shu mavzuda ingliz tilida gapirib, ovozli xabar yuboring.",
        parse_mode="HTML",
        reply_markup=speaking_skip_keyboard(),
    )


async def _record_and_advance(
    message: Message, state: FSMContext, score: int, feedback: str
) -> None:
    """Bitta topic natijasini saqlab, keyingi topic yoki natijaga o'tish."""
    data = await state.get_data()
    topics = data["speaking_topics"]
    scores = data["speaking_scores"] + [score]
    feedbacks = data["speaking_feedbacks"] + [feedback]
    idx = data["speaking_index"] + 1
    await state.update_data(
        speaking_scores=scores, speaking_feedbacks=feedbacks, speaking_index=idx
    )

    if idx < len(topics):
        await _send_topic(message, state)
    else:
        from bot.handlers.result import show_result
        await show_result(message, state)


async def start_speaking(message: Message, state: FSMContext) -> None:
    topics = await crud.get_random_speaking_topics(6)
    if not topics:
        await message.answer("🎤 Speaking: mavzu mavjud emas, bo'lim o'tkazib yuborildi.")
        await state.update_data(speaking_scores=[], speaking_feedbacks=[])
        from bot.handlers.result import show_result
        await show_result(message, state)
        return

    await state.update_data(
        speaking_topics=topics,
        speaking_index=0,
        speaking_scores=[],
        speaking_feedbacks=[],
    )
    await state.set_state(TestStates.speaking)
    await _send_topic(message, state)


@router.message(TestStates.speaking, F.voice)
async def receive_voice(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    topics = data["speaking_topics"]
    idx = data["speaking_index"]
    topic_text = topics[idx]["text"]

    await message.answer("⏳ Javob baholanmoqda...")

    # Ovozli xabarni yuklab olish
    buf = BytesIO()
    file = await message.bot.get_file(message.voice.file_id)
    await message.bot.download_file(file.file_path, buf)
    audio_bytes = buf.getvalue()

    score, feedback = await evaluate_speaking(
        topic_text, audio_bytes, mime_type="audio/ogg",
        duration=message.voice.duration or 0,
    )

    await _record_and_advance(message, state, score, feedback)


@router.callback_query(TestStates.speaking, F.data == "speak_skip")
async def skip_topic(callback: CallbackQuery, state: FSMContext) -> None:
    """'Javob bera olmayman' — o'sha topicga 0 ball, keyingisiga o'tish."""
    if callback.message:
        try:
            await callback.message.edit_reply_markup(reply_markup=None)
        except Exception:  # noqa: BLE001
            pass
    await callback.answer("Bu mavzu o'tkazib yuborildi (0 ball)")
    await _record_and_advance(
        callback.message, state, 0, "Javob berilmadi (o'tkazib yuborilgan)."
    )


@router.message(TestStates.speaking)
async def speaking_wrong_type(message: Message, state: FSMContext) -> None:
    await message.answer(
        "🎤 Iltimos, javobingizni ovozli xabar (voice) ko'rinishida yuboring "
        "yoki «⏭ Javob bera olmayman» tugmasini bosing.",
        reply_markup=speaking_skip_keyboard(),
    )
