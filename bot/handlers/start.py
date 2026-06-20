"""Start, ism-familya so'rash va interrupt handler (PHASE 3.1, 3.8)."""
from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.keyboards.inline import interrupt_keyboard, start_test_keyboard
from bot.states import TestStates

router = Router(name="start")

WELCOME_TEXT = (
    "🎓 Academia IELTS ga xush kelibsiz!\n\n"
    "Placement test orqali siz ingliz tili darajangizni aniqlaymiz.\n"
    "Test 5 bo'limdan iborat: Grammar, Reading, Listening, Writing va Speaking.\n\n"
    "Boshlash uchun ismingizni kiriting:"
)

HELP_TEXT = (
    "📖 <b>Academia IELTS — Qo'llanma</b>\n\n"
    "Bu bot ingliz tili darajangizni aniqlaydi (placement test).\n\n"
    "🔹 /start — testni boshlash\n"
    "🔹 /restart — testni boshqatdan boshlash\n"
    "🔹 /help — shu qo'llanma\n\n"
    "📝 <b>Test 5 bo'limdan iborat:</b>\n"
    "1️⃣ Grammar — 20 ta savol (A/B/C/D)\n"
    "2️⃣ Reading — matn o'qib, savollarga javob\n"
    "3️⃣ Listening — audio tinglab, savollarga javob\n"
    "4️⃣ Writing — mavzu bo'yicha insho yozasiz (matn)\n"
    "5️⃣ Speaking — mavzu bo'yicha ovozli xabar yuborasiz\n\n"
    "⏭ Savolni o'tkazib yuborsangiz (Skip), u oxirida qayta so'raladi.\n"
    "🏆 Oxirida darajangiz (A1–C2) va foizingiz chiqadi."
)

ADMIN_HELP_TEXT = (
    "\n\n👤 <b>Adminlar uchun:</b>\n"
    "🔹 /admin — savol/passage/audio/topic boshqarish\n"
    "🔹 /overall — umumiy statistika (faqat superadmin)"
)


async def begin_intro(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(TestStates.waiting_first_name)
    await message.answer(WELCOME_TEXT)


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    current = await state.get_state()
    # Test davom etayotgan bo'lsa — interrupt
    if current in (TestStates.quiz.state, TestStates.writing.state, TestStates.speaking.state):
        await message.answer(
            "⚠️ Siz hozir test topshiryapsiz!\n\nNima qilmoqchisiz?",
            reply_markup=interrupt_keyboard(),
        )
        return
    await begin_intro(message, state)


@router.message(Command("restart"))
async def cmd_restart(message: Message, state: FSMContext) -> None:
    # Testni so'rovsiz boshqatdan boshlash (joriy holat tozalanadi)
    await message.answer("🔄 Test boshqatdan boshlanmoqda...")
    await begin_intro(message, state)


@router.message(Command("help"))
async def cmd_help(message: Message, state: FSMContext) -> None:
    from bot.admin.handlers import is_admin
    text = HELP_TEXT
    if await is_admin(message.from_user.id):
        text += ADMIN_HELP_TEXT
    await message.answer(text, parse_mode="HTML")


@router.message(TestStates.waiting_first_name, F.text)
async def get_first_name(message: Message, state: FSMContext) -> None:
    await state.update_data(first_name=message.text.strip())
    await state.set_state(TestStates.waiting_last_name)
    await message.answer("Familyangizni kiriting:")


@router.message(TestStates.waiting_last_name, F.text)
async def get_last_name(message: Message, state: FSMContext) -> None:
    await state.update_data(last_name=message.text.strip())
    data = await state.get_data()
    full_name = f"{data['first_name']} {data['last_name']}"
    await message.answer(
        f"Salom, {full_name}! 👋\nTestni boshlashga tayyormisiz?",
        reply_markup=start_test_keyboard(),
    )


@router.callback_query(F.data.in_({"begin_test", "begin_test_new"}))
async def begin_test(callback: CallbackQuery, state: FSMContext) -> None:
    if callback.message:
        try:
            await callback.message.edit_reply_markup(reply_markup=None)
        except Exception:  # noqa: BLE001
            pass
    await callback.answer()
    # "Yangi test" — ism qaytadan so'raladi
    if callback.data == "begin_test_new":
        await begin_intro(callback.message, state)
        return
    from bot.handlers.grammar import start_grammar
    await start_grammar(callback.message, state)


# ─────────────────────────── Interrupt callbacklar ───────────────────────────
@router.callback_query(F.data == "intr_continue")
async def interrupt_continue(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer("Test davom etmoqda")
    if callback.message:
        try:
            await callback.message.delete()
        except Exception:  # noqa: BLE001
            pass


@router.callback_query(F.data == "intr_new")
async def interrupt_new(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    if callback.message:
        try:
            await callback.message.delete()
        except Exception:  # noqa: BLE001
            pass
        await begin_intro(callback.message, state)
