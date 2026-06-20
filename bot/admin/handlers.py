"""Admin panel handlerlari (PHASE 4)."""
import html
import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.admin import keyboards as kb
from bot.config import config
from bot.database import crud
from bot.states import AdminStates

logger = logging.getLogger(__name__)
router = Router(name="admin")


# ─────────────────────────── Ruxsatlar ───────────────────────────
def is_superadmin(user_id: int) -> bool:
    return user_id == config.superadmin_id


async def is_admin(user_id: int) -> bool:
    if user_id == config.superadmin_id or user_id in config.admin_ids:
        return True
    return await crud.is_admin(user_id)


# ─────────────────────────── Quiz poll parser ───────────────────────────
def parse_quiz_poll(poll) -> tuple[dict | None, str]:
    """Telegram quiz polldan savol ma'lumotlarini ajratish."""
    if poll is None or poll.type != "quiz":
        return None, "❌ Iltimos, oddiy emas, <b>Quiz</b> turidagi so'rovnoma yuboring."
    options = [o.text for o in poll.options]
    if len(options) != 4:
        return None, "❌ Savolda aniq 4 ta variant (A, B, C, D) bo'lishi kerak."
    if poll.correct_option_id is None:
        return None, (
            "❌ To'g'ri javob aniqlanmadi. Quiz so'rovnomani <b>botning o'ziga</b> "
            "(forward emas, yangi yaratib) yuboring."
        )
    return {
        "question_text": poll.question,
        "option_a": options[0],
        "option_b": options[1],
        "option_c": options[2],
        "option_d": options[3],
        "correct_option": "abcd"[poll.correct_option_id],
    }, ""


# ─────────────────────────── Menyu ───────────────────────────
@router.message(Command("admin"))
async def admin_menu(message: Message, state: FSMContext) -> None:
    if not await is_admin(message.from_user.id):
        return
    await state.clear()
    await message.answer(
        "⚙️ <b>Admin Panel — Academia IELTS</b>",
        parse_mode="HTML",
        reply_markup=kb.main_menu(is_superadmin(message.from_user.id)),
    )


@router.callback_query(F.data == "adm:back")
async def back_to_main(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.answer()
    await callback.message.edit_text(
        "⚙️ <b>Admin Panel — Academia IELTS</b>",
        parse_mode="HTML",
        reply_markup=kb.main_menu(is_superadmin(callback.from_user.id)),
    )


@router.callback_query(F.data == "adm:reading")
async def menu_reading(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.answer()
    await callback.message.edit_text("📖 <b>Reading boshqaruvi</b>", parse_mode="HTML",
                                     reply_markup=kb.reading_menu())


@router.callback_query(F.data == "adm:listening")
async def menu_listening(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.answer()
    await callback.message.edit_text("🎧 <b>Listening boshqaruvi</b>", parse_mode="HTML",
                                     reply_markup=kb.listening_menu())


@router.callback_query(F.data == "adm:writing")
async def menu_writing(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.answer()
    await callback.message.edit_text("✍️ <b>Writing topiclar</b>", parse_mode="HTML",
                                     reply_markup=kb.writing_menu())


@router.callback_query(F.data == "adm:speaking")
async def menu_speaking(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.answer()
    await callback.message.edit_text("🎤 <b>Speaking topiclar</b>", parse_mode="HTML",
                                     reply_markup=kb.speaking_menu())


@router.callback_query(F.data == "adm:admins")
async def menu_admins(callback: CallbackQuery, state: FSMContext) -> None:
    if not is_superadmin(callback.from_user.id):
        await callback.answer("Faqat superadmin uchun", show_alert=True)
        return
    await state.clear()
    await callback.answer()
    await callback.message.edit_text("👤 <b>Adminlar boshqaruvi</b>", parse_mode="HTML",
                                     reply_markup=kb.admins_menu())


# Grammar savollari admin paneldan emas, scripts/seed.py dagi GRAMMAR ro'yxatidan
# boshqariladi (bot ishga tushganda avto-sinxronlanadi). Shu sabab bu yerda grammar yo'q.


# ═══════════════════════════ READING ═══════════════════════════
@router.callback_query(F.data == "adm:reading:addp")
async def reading_add_passage(callback: CallbackQuery, state: FSMContext) -> None:
    if await crud.list_passages():
        await callback.answer()
        await callback.message.answer(
            "⚠️ Bazada allaqachon bitta passage bor. Faqat <b>1 ta</b> passage bo'lishi mumkin.\n"
            "Yangisini qo'shish uchun avval «🗑 Passage o'chirish» orqali eskisini o'chiring.",
            parse_mode="HTML",
            reply_markup=kb.reading_menu(),
        )
        return
    await state.set_state(AdminStates.passage_title)
    await callback.answer()
    await callback.message.answer("📖 Passage sarlavhasini yuboring:")


@router.message(AdminStates.passage_title, F.text)
async def reading_passage_title(message: Message, state: FSMContext) -> None:
    await state.update_data(passage_title=message.text.strip())
    await state.set_state(AdminStates.passage_text)
    await message.answer("Endi passage matnini yuboring:")


@router.message(AdminStates.passage_text, F.text)
async def reading_passage_text(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    pid = await crud.add_passage(data["passage_title"], message.text.strip())
    await state.clear()
    await message.answer(
        f"✅ Passage qo'shildi. ID: <b>{pid}</b>\n"
        f"Savol qo'shish uchun «➕ Passagega savol qo'shish» tugmasidan foydalaning.",
        parse_mode="HTML",
        reply_markup=kb.reading_menu(),
    )


@router.callback_query(F.data == "adm:reading:addq")
async def reading_add_question(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AdminStates.reading_q_passage_id)
    await callback.answer()
    await callback.message.answer("📖 Savol qo'shiladigan Passage ID raqamini yuboring:")


@router.message(AdminStates.reading_q_passage_id, F.text)
async def reading_q_passage(message: Message, state: FSMContext) -> None:
    if not message.text.strip().isdigit():
        await message.answer("❌ Faqat raqam yuboring.")
        return
    pid = int(message.text.strip())
    if not await crud.passage_exists(pid):
        await message.answer("❌ Bunday Passage ID topilmadi. Qaytadan kiriting:")
        return
    await state.update_data(passage_id=pid)
    await state.set_state(AdminStates.reading_q_poll)
    await message.answer(
        "Endi shu passage uchun <b>Quiz</b> so'rovnoma yuboring (4 variant + to'g'ri javob).",
        parse_mode="HTML",
    )


@router.message(AdminStates.reading_q_poll, F.poll)
async def reading_q_save(message: Message, state: FSMContext) -> None:
    data, err = parse_quiz_poll(message.poll)
    if not data:
        await message.answer(err, parse_mode="HTML")
        return
    state_data = await state.get_data()
    await crud.add_reading_question(passage_id=state_data["passage_id"], **data)
    await state.clear()
    await message.answer("✅ Reading savoli qo'shildi.", reply_markup=kb.reading_menu())


@router.callback_query(F.data == "adm:reading:del")
async def reading_del(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AdminStates.passage_delete)
    await callback.answer()
    await callback.message.answer("🗑 O'chiriladigan Passage ID raqamini yuboring (savollar ham o'chadi):")


@router.message(AdminStates.passage_delete, F.text)
async def reading_do_delete(message: Message, state: FSMContext) -> None:
    if not message.text.strip().isdigit():
        await message.answer("❌ Faqat raqam yuboring.")
        return
    ok = await crud.delete_passage(int(message.text.strip()))
    await state.clear()
    msg = "✅ Passage va unga bog'liq savollar o'chirildi." if ok else "❌ Bunday ID topilmadi."
    await message.answer(msg, reply_markup=kb.reading_menu())


@router.callback_query(F.data == "adm:reading:list")
async def reading_list(callback: CallbackQuery) -> None:
    await callback.answer()
    rows = await crud.list_passages()
    if not rows:
        text = "📖 Passagelar yo'q."
    else:
        text = "📖 <b>Passagelar:</b>\n" + "\n".join(
            f"ID {r['id']} — {html.escape(r['title'])} ({r['q_count']} ta savol)" for r in rows
        )
    await callback.message.answer(text, parse_mode="HTML", reply_markup=kb.reading_menu())


# ═══════════════════════════ LISTENING ═══════════════════════════
@router.callback_query(F.data == "adm:listening:adda")
async def listening_add_audio(callback: CallbackQuery, state: FSMContext) -> None:
    if await crud.list_audios():
        await callback.answer()
        await callback.message.answer(
            "⚠️ Bazada allaqachon bitta audio bor. Faqat <b>1 ta</b> audio bo'lishi mumkin.\n"
            "Yangisini qo'shish uchun avval «🗑 Audio o'chirish» orqali eskisini o'chiring.",
            parse_mode="HTML",
            reply_markup=kb.listening_menu(),
        )
        return
    await state.set_state(AdminStates.audio_file)
    await callback.answer()
    await callback.message.answer("🎧 Audio faylni yuboring (audio, voice yoki document):")


@router.message(AdminStates.audio_file, F.audio | F.voice | F.document)
async def listening_audio_received(message: Message, state: FSMContext) -> None:
    if message.audio:
        file_id = message.audio.file_id
    elif message.voice:
        file_id = message.voice.file_id
    else:
        file_id = message.document.file_id
    await state.update_data(audio_file_id=file_id)
    await state.set_state(AdminStates.audio_title)
    await message.answer("✅ Audio qabul qilindi. Endi audio sarlavhasini yuboring:")


@router.message(AdminStates.audio_file)
async def listening_audio_wrong(message: Message) -> None:
    await message.answer("❌ Iltimos, audio fayl yuboring.")


@router.message(AdminStates.audio_title, F.text)
async def listening_audio_title(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    aid = await crud.add_audio(message.text.strip(), data["audio_file_id"])
    await state.clear()
    await message.answer(
        f"✅ Audio qo'shildi. ID: <b>{aid}</b>\n"
        f"Savol qo'shish uchun «➕ Audioga savol qo'shish» tugmasidan foydalaning.",
        parse_mode="HTML",
        reply_markup=kb.listening_menu(),
    )


@router.callback_query(F.data == "adm:listening:addq")
async def listening_add_question(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AdminStates.listening_q_audio_id)
    await callback.answer()
    await callback.message.answer("🎧 Savol qo'shiladigan Audio ID raqamini yuboring:")


@router.message(AdminStates.listening_q_audio_id, F.text)
async def listening_q_audio(message: Message, state: FSMContext) -> None:
    if not message.text.strip().isdigit():
        await message.answer("❌ Faqat raqam yuboring.")
        return
    aid = int(message.text.strip())
    if not await crud.audio_exists(aid):
        await message.answer("❌ Bunday Audio ID topilmadi. Qaytadan kiriting:")
        return
    await state.update_data(audio_id=aid)
    await state.set_state(AdminStates.listening_q_poll)
    await message.answer(
        "Endi shu audio uchun <b>Quiz</b> so'rovnoma yuboring (4 variant + to'g'ri javob).",
        parse_mode="HTML",
    )


@router.message(AdminStates.listening_q_poll, F.poll)
async def listening_q_save(message: Message, state: FSMContext) -> None:
    data, err = parse_quiz_poll(message.poll)
    if not data:
        await message.answer(err, parse_mode="HTML")
        return
    state_data = await state.get_data()
    await crud.add_listening_question(audio_id=state_data["audio_id"], **data)
    await state.clear()
    await message.answer("✅ Listening savoli qo'shildi.", reply_markup=kb.listening_menu())


@router.callback_query(F.data == "adm:listening:del")
async def listening_del(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AdminStates.audio_delete)
    await callback.answer()
    await callback.message.answer("🗑 O'chiriladigan Audio ID raqamini yuboring (savollar ham o'chadi):")


@router.message(AdminStates.audio_delete, F.text)
async def listening_do_delete(message: Message, state: FSMContext) -> None:
    if not message.text.strip().isdigit():
        await message.answer("❌ Faqat raqam yuboring.")
        return
    ok = await crud.delete_audio(int(message.text.strip()))
    await state.clear()
    msg = "✅ Audio va unga bog'liq savollar o'chirildi." if ok else "❌ Bunday ID topilmadi."
    await message.answer(msg, reply_markup=kb.listening_menu())


@router.callback_query(F.data == "adm:listening:list")
async def listening_list(callback: CallbackQuery) -> None:
    await callback.answer()
    rows = await crud.list_audios()
    if not rows:
        text = "🎧 Audiolar yo'q."
    else:
        text = "🎧 <b>Audiolar:</b>\n" + "\n".join(
            f"ID {r['id']} — {html.escape(r['title'])} ({r['q_count']} ta savol)" for r in rows
        )
    await callback.message.answer(text, parse_mode="HTML", reply_markup=kb.listening_menu())


# ═══════════════════════════ WRITING ═══════════════════════════
@router.callback_query(F.data == "adm:writing:add")
async def writing_add(callback: CallbackQuery, state: FSMContext) -> None:
    if await crud.list_writing_topics():
        await callback.answer()
        await callback.message.answer(
            "⚠️ Bazada allaqachon bitta Writing topic bor. Faqat <b>1 ta</b> topic bo'lishi mumkin.\n"
            "Yangisini qo'shish uchun avval «🗑 Topic o'chirish» orqali eskisini o'chiring.",
            parse_mode="HTML",
            reply_markup=kb.writing_menu(),
        )
        return
    await state.set_state(AdminStates.writing_topic_add)
    await callback.answer()
    await callback.message.answer("✍️ Yangi Writing topic matnini yuboring:")


@router.message(AdminStates.writing_topic_add, F.text)
async def writing_save(message: Message, state: FSMContext) -> None:
    await crud.add_writing_topic(message.text.strip())
    await state.clear()
    await message.answer("✅ Writing topic qo'shildi.", reply_markup=kb.writing_menu())


@router.callback_query(F.data == "adm:writing:del")
async def writing_del(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AdminStates.writing_topic_delete)
    await callback.answer()
    await callback.message.answer("🗑 O'chiriladigan topic ID raqamini yuboring:")


@router.message(AdminStates.writing_topic_delete, F.text)
async def writing_do_delete(message: Message, state: FSMContext) -> None:
    if not message.text.strip().isdigit():
        await message.answer("❌ Faqat raqam yuboring.")
        return
    ok = await crud.delete_writing_topic(int(message.text.strip()))
    await state.clear()
    msg = "✅ O'chirildi." if ok else "❌ Bunday ID topilmadi."
    await message.answer(msg, reply_markup=kb.writing_menu())


@router.callback_query(F.data == "adm:writing:list")
async def writing_list(callback: CallbackQuery) -> None:
    await callback.answer()
    rows = await crud.list_writing_topics()
    await callback.message.answer(_format_list(rows, "Writing topiclar"),
                                  reply_markup=kb.writing_menu())


# ═══════════════════════════ SPEAKING ═══════════════════════════
@router.callback_query(F.data == "adm:speaking:add")
async def speaking_add(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AdminStates.speaking_topic_add)
    await callback.answer()
    await callback.message.answer("🎤 Yangi Speaking topic matnini yuboring:")


@router.message(AdminStates.speaking_topic_add, F.text)
async def speaking_save(message: Message, state: FSMContext) -> None:
    await crud.add_speaking_topic(message.text.strip())
    await state.clear()
    await message.answer("✅ Speaking topic qo'shildi.", reply_markup=kb.speaking_menu())


@router.callback_query(F.data == "adm:speaking:del")
async def speaking_del(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AdminStates.speaking_topic_delete)
    await callback.answer()
    await callback.message.answer("🗑 O'chiriladigan topic ID raqamini yuboring:")


@router.message(AdminStates.speaking_topic_delete, F.text)
async def speaking_do_delete(message: Message, state: FSMContext) -> None:
    if not message.text.strip().isdigit():
        await message.answer("❌ Faqat raqam yuboring.")
        return
    ok = await crud.delete_speaking_topic(int(message.text.strip()))
    await state.clear()
    msg = "✅ O'chirildi." if ok else "❌ Bunday ID topilmadi."
    await message.answer(msg, reply_markup=kb.speaking_menu())


@router.callback_query(F.data == "adm:speaking:list")
async def speaking_list(callback: CallbackQuery) -> None:
    await callback.answer()
    rows = await crud.list_speaking_topics()
    await callback.message.answer(_format_list(rows, "Speaking topiclar"),
                                  reply_markup=kb.speaking_menu())


# ═══════════════════════════ ADMINLAR (faqat superadmin) ═══════════════════════════
@router.callback_query(F.data == "adm:admins:add")
async def admins_add(callback: CallbackQuery, state: FSMContext) -> None:
    if not is_superadmin(callback.from_user.id):
        await callback.answer("Faqat superadmin uchun", show_alert=True)
        return
    await state.set_state(AdminStates.admin_add)
    await callback.answer()
    await callback.message.answer("👤 Yangi admin Telegram ID raqamini yuboring:")


@router.message(AdminStates.admin_add, F.text)
async def admins_do_add(message: Message, state: FSMContext) -> None:
    if not is_superadmin(message.from_user.id):
        await state.clear()
        return
    raw = message.text.strip()
    if not raw.isdigit():
        await message.answer("❌ Faqat raqamli ID yuboring.")
        return
    ok = await crud.add_admin(int(raw))
    await state.clear()
    msg = "✅ Admin qo'shildi." if ok else "ℹ️ Bu admin allaqachon mavjud."
    await message.answer(msg, reply_markup=kb.admins_menu())


@router.callback_query(F.data == "adm:admins:del")
async def admins_del(callback: CallbackQuery, state: FSMContext) -> None:
    if not is_superadmin(callback.from_user.id):
        await callback.answer("Faqat superadmin uchun", show_alert=True)
        return
    await state.set_state(AdminStates.admin_remove)
    await callback.answer()
    await callback.message.answer("🗑 O'chiriladigan admin Telegram ID raqamini yuboring:")


@router.message(AdminStates.admin_remove, F.text)
async def admins_do_del(message: Message, state: FSMContext) -> None:
    if not is_superadmin(message.from_user.id):
        await state.clear()
        return
    raw = message.text.strip()
    if not raw.isdigit():
        await message.answer("❌ Faqat raqamli ID yuboring.")
        return
    ok = await crud.remove_admin(int(raw))
    await state.clear()
    msg = "✅ Admin o'chirildi." if ok else "❌ Bunday admin topilmadi."
    await message.answer(msg, reply_markup=kb.admins_menu())


@router.callback_query(F.data == "adm:admins:list")
async def admins_list(callback: CallbackQuery) -> None:
    if not is_superadmin(callback.from_user.id):
        await callback.answer("Faqat superadmin uchun", show_alert=True)
        return
    await callback.answer()
    rows = await crud.list_admins()
    if not rows:
        text = "👤 DB da adminlar yo'q (faqat superadmin)."
    else:
        text = "👤 <b>Adminlar:</b>\n" + "\n".join(
            f"ID {r['telegram_id']}" + (f" — {r['name']}" if r['name'] else "") for r in rows
        )
    await callback.message.answer(text, parse_mode="HTML", reply_markup=kb.admins_menu())


# ═══════════════════════════ /overall (superadmin) ═══════════════════════════
@router.message(Command("overall"))
async def overall_stats(message: Message) -> None:
    if not is_superadmin(message.from_user.id):
        return
    s = await crud.get_stats()
    lv = s["levels"]
    text = (
        "📊 <b>Academia IELTS — Umumiy statistika</b>\n\n"
        f"👥 Jami testlar: {s['total']}\n"
        f"📅 Bugun: {s['today']}\n"
        f"📅 Bu hafta: {s['week']}\n\n"
        "🏆 <b>Daraja taqsimoti:</b>\n"
        f"A1 — {lv['A1']} ta\n"
        f"A2 — {lv['A2']} ta\n"
        f"B1 — {lv['B1']} ta\n"
        f"B2 — {lv['B2']} ta\n"
        f"C1 — {lv['C1']} ta\n"
        f"C2 — {lv['C2']} ta\n\n"
        f"📈 O'rtacha ball: {s['avg']:g}%"
    )
    await message.answer(text, parse_mode="HTML")


# ─────────────────────────── Helper ───────────────────────────
def _format_list(rows: list[dict], title: str) -> str:
    if not rows:
        return f"📋 {title}: bo'sh."
    lines = [f"📋 <b>{title}:</b>"]
    for r in rows:
        text = r["text"]
        short = text[:60] + ("…" if len(text) > 60 else "")
        lines.append(f"ID {r['id']} — {html.escape(short)}")
    return "\n".join(lines)
