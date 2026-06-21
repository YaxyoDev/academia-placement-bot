"""Natija hisoblash va ko'rsatish (PHASE 3.7)."""
import html

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.database import crud
from bot.keyboards.inline import new_test_keyboard
from bot.utils.scoring import pct, percentage_to_level, total_percentage

router = Router(name="result")


async def show_result(message: Message, state: FSMContext) -> None:
    data = await state.get_data()

    first_name = data.get("first_name", "")
    last_name = data.get("last_name", "")
    full_name = f"{first_name} {last_name}".strip()

    # ── Ballar ──
    g_correct = data.get("grammar_correct", 0)
    g_total = data.get("grammar_total", 0)
    r_correct = data.get("reading_correct", 0)
    r_total = data.get("reading_total", 0)
    l_correct = data.get("listening_correct", 0)
    l_total = data.get("listening_total", 0)
    writing_score = data.get("writing_score", 0)
    writing_feedback = data.get("writing_feedback", "")
    speaking_scores = data.get("speaking_scores", [])
    speaking_feedbacks = data.get("speaking_feedbacks", [])
    speaking_avg = round(sum(speaking_scores) / len(speaking_scores), 1) if speaking_scores else 0.0

    # ── Foizlar ──
    g_pct = pct(g_correct, g_total)
    r_pct = pct(r_correct, r_total)
    l_pct = pct(l_correct, l_total)
    w_pct = pct(writing_score, 10)
    s_pct = pct(speaking_avg, 10)

    total_pct = total_percentage([g_pct, r_pct, l_pct, w_pct, s_pct])
    total_level = percentage_to_level(total_pct)

    # ── Natija xabari ──
    text = (
        f"👤 <b>{html.escape(full_name)}</b>\n\n"
        f"📝 Grammar &amp; Vocabulary: {g_pct:g}% — {percentage_to_level(g_pct)}\n"
        f"📖 Reading:   {r_pct:g}% — {percentage_to_level(r_pct)}\n"
        f"🎧 Listening: {l_pct:g}% — {percentage_to_level(l_pct)}\n"
        f"✍️ Writing:   {w_pct:g}% — {percentage_to_level(w_pct)}\n"
        f"🎤 Speaking:  {s_pct:g}% — {percentage_to_level(s_pct)}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🏆 <b>Total: {total_pct:g}% — {total_level}</b>"
    )
    await message.answer(text, parse_mode="HTML")

    # ── Feedbacklar alohida ──
    if writing_feedback:
        await message.answer(
            f"✍️ <b>Writing izohi:</b>\n{html.escape(writing_feedback)}", parse_mode="HTML"
        )
    if speaking_feedbacks:
        parts = ["🎤 <b>Speaking izohlari:</b>"]
        for i, fb in enumerate(speaking_feedbacks, 1):
            parts.append(f"{i}. {html.escape(fb)}")
        await message.answer("\n".join(parts), parse_mode="HTML")

    # ── DB ga saqlash ──
    total_score = g_correct + r_correct + l_correct + writing_score + speaking_avg
    await crud.save_result(
        first_name=first_name,
        last_name=last_name,
        grammar_score=g_correct,
        reading_score=r_correct,
        listening_score=l_correct,
        writing_score=writing_score,
        writing_feedback=writing_feedback,
        speaking_score=speaking_avg,
        speaking_feedback=" | ".join(speaking_feedbacks),
        total_score=round(total_score, 1),
        percentage=total_pct,
        level=total_level,
    )

    # ── Keyingi odam uchun reset ──
    await state.clear()
    await message.answer(
        "✅ Test yakunlandi! Keyingi odam uchun tugmani bosing yoki /start yuboring.",
        reply_markup=new_test_keyboard(),
    )
