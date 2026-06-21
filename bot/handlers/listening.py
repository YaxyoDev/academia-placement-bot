"""Listening seksiyasi (PHASE 3.4) — audio + MCQ savollar."""
import html

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.database import crud
from bot.handlers.quiz_engine import begin_section
from bot.keyboards.inline import listening_quiz_keyboard, listening_start_keyboard

router = Router(name="listening")


async def _to_writing(message: Message, state: FSMContext) -> None:
    await state.update_data(listening_correct=0, listening_total=0)
    from bot.handlers.writing import start_writing
    await start_writing(message, state)


async def start_listening(message: Message, state: FSMContext) -> None:
    audio = await crud.get_random_audio_with_questions()
    if not audio:
        await message.answer("🎧 Listening: audio mavjud emas, bo'lim o'tkazib yuborildi.")
        await _to_writing(message, state)
        return

    await state.update_data(
        pending_listening=audio["questions"],
        listening_file_id=audio["file_id"],
    )
    await message.answer(
        f"🎧 <b>Listening bo'limi</b>\n\n{html.escape(audio['title'])}",
        parse_mode="HTML",
        reply_markup=listening_start_keyboard(),
    )


@router.callback_query(F.data == "listen_start")
async def listening_play_audio(callback: CallbackQuery, state: FSMContext) -> None:
    """1-bosqich: audioni yuborish + 'Savollarni boshlash' tugmasi."""
    data = await state.get_data()
    file_id = data.get("listening_file_id")

    if callback.message:
        try:
            await callback.message.edit_reply_markup(reply_markup=None)
        except Exception:  # noqa: BLE001
            pass
    await callback.answer()

    if not (file_id and callback.message):
        await _to_writing(callback.message, state)
        return

    # Audioni yuborish (tagida "Savollarni boshlash" tugmasi bilan).
    # Audio chatda qoladi — foydalanuvchi savollar paytida qayta tinglay oladi.
    kb = listening_quiz_keyboard()
    for sender in ("answer_audio", "answer_voice", "answer_document"):
        try:
            await getattr(callback.message, sender)(file_id, reply_markup=kb)
            break
        except Exception:  # noqa: BLE001
            continue


@router.callback_query(F.data == "listen_quiz")
async def listening_questions_start(callback: CallbackQuery, state: FSMContext) -> None:
    """2-bosqich: savollarni boshlash (audio chatda qoladi — qayta tinglsa bo'ladi)."""
    data = await state.get_data()
    questions = data.get("pending_listening", [])

    await callback.answer()

    # "Savollarni boshlash" tugmasini olib tashlaymiz (audio xabar o'zi qoladi)
    if callback.message:
        try:
            await callback.message.edit_reply_markup(reply_markup=None)
        except Exception:  # noqa: BLE001
            pass

    if not questions:
        await _to_writing(callback.message, state)
        return
    await begin_section(callback.message, state, "listening", questions)
