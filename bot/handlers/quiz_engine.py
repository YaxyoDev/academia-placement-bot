"""MCQ seksiyalar uchun umumiy yadro (Grammar / Reading / Listening).

Savollar FSMContext da saqlanadi. Skip qilingan savollar oxirida qaytadan so'raladi.
Seksiya tugagach keyingi seksiya avtomatik boshlanadi.
"""
import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.keyboards.inline import quiz_keyboard
from bot.states import TestStates

logger = logging.getLogger(__name__)
router = Router(name="quiz_engine")

SECTION_TITLES = {
    "grammar": "📝 Grammar & Vocabulary",
    "reading": "📖 Reading",
    "listening": "🎧 Listening",
}


def _format_question(header: str, pos: int, total: int, q: dict) -> str:
    return (
        f"{header}\n"
        f"Savol {pos}/{total}\n\n"
        f"{q['text']}\n\n"
        f"A) {q['a']}\n"
        f"B) {q['b']}\n"
        f"C) {q['c']}\n"
        f"D) {q['d']}"
    )


async def begin_section(message: Message, state: FSMContext, section: str, questions: list[dict]) -> None:
    """Yangi MCQ seksiyani boshlash."""
    await state.update_data(
        section=section,
        all_questions=questions,         # ball hisoblash uchun original ro'yxat
        queue=list(questions),           # so'raladigan savollar navbati
        answers={},                      # {str(qid): 'a'|'b'|'c'|'d'}
        skipped=[],                      # skip qilingan savol dictlar
        retrying=False,
        pass_total=len(questions),
    )
    await state.set_state(TestStates.quiz)
    await _send_current(message, state)


async def _send_current(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    queue = data["queue"]
    q = queue[0]
    pass_total = data["pass_total"]
    pos = pass_total - len(queue) + 1
    header = "⏭ Qaytarilgan savol" if data["retrying"] else SECTION_TITLES.get(data["section"], "")
    await message.answer(_format_question(header, pos, pass_total, q), reply_markup=quiz_keyboard())


@router.callback_query(TestStates.quiz, F.data.startswith("qa:"))
async def on_answer(callback: CallbackQuery, state: FSMContext) -> None:
    letter = callback.data.split(":", 1)[1]
    data = await state.get_data()
    queue = data["queue"]
    if not queue:
        await callback.answer()
        return
    q = queue[0]
    answers = data["answers"]
    answers[str(q["id"])] = letter
    await state.update_data(answers=answers)

    if callback.message:
        await callback.message.edit_text(
            callback.message.text + f"\n\n✅ Tanlangan javob: {letter.upper()}"
        )
    await callback.answer()
    await _advance(callback.message, state)


@router.callback_query(TestStates.quiz, F.data == "qskip")
async def on_skip(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    queue = data["queue"]
    if not queue:
        await callback.answer()
        return
    q = queue[0]
    # Faqat birinchi o'tishda skip ro'yxatiga qo'shiladi
    if not data["retrying"]:
        skipped = data["skipped"]
        skipped.append(q)
        await state.update_data(skipped=skipped)

    if callback.message:
        await callback.message.edit_text(callback.message.text + "\n\n⏭ O'tkazib yuborildi")
    await callback.answer("O'tkazib yuborildi")
    await _advance(callback.message, state)


async def _advance(message: Message, state: FSMContext) -> None:
    """Navbatdagi savolga o'tish yoki seksiyani yakunlash."""
    data = await state.get_data()
    queue = data["queue"]
    queue.pop(0)
    await state.update_data(queue=queue)

    if queue:
        await _send_current(message, state)
        return

    # Joriy o'tish tugadi
    if not data["retrying"] and data["skipped"]:
        skipped = data["skipped"]
        await message.answer(
            f"⏭ Siz {len(skipped)} ta savolni o'tkazib yubordingiz. Endi ularga javob bering!"
        )
        await state.update_data(
            queue=list(skipped),
            skipped=[],
            retrying=True,
            pass_total=len(skipped),
        )
        await _send_current(message, state)
        return

    await _finalize_section(message, state)


async def _finalize_section(message: Message, state: FSMContext) -> None:
    """Seksiya ballini hisoblab, keyingi seksiyaga o'tish."""
    data = await state.get_data()
    section = data["section"]
    all_questions = data["all_questions"]
    answers = data["answers"]

    correct = sum(
        1 for q in all_questions if answers.get(str(q["id"])) == q["correct"]
    )
    total = len(all_questions)
    await state.update_data(**{f"{section}_correct": correct, f"{section}_total": total})

    # Keyingi seksiya (lazy import — circular importdan qochish uchun)
    if section == "grammar":
        from bot.handlers.reading import start_reading
        await start_reading(message, state)
    elif section == "reading":
        from bot.handlers.listening import start_listening
        await start_listening(message, state)
    elif section == "listening":
        from bot.handlers.writing import start_writing
        await start_writing(message, state)
