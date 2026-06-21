"""Foydalanuvchi bot uchun inline klaviaturalar."""
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def quiz_keyboard() -> InlineKeyboardMarkup:
    """A B C D + Skip tugmalari (MCQ savollar uchun)."""
    b = InlineKeyboardBuilder()
    for letter in ("a", "b", "c", "d"):
        b.button(text=letter.upper(), callback_data=f"qa:{letter}")
    b.button(text="⏭ Skip", callback_data="qskip")
    b.adjust(4, 1)
    return b.as_markup()


def start_test_keyboard() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="✅ Testni boshlash", callback_data="begin_test")
    return b.as_markup()


def interrupt_keyboard() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="✅ Davom etish", callback_data="intr_continue")
    b.button(text="🔄 Yangi test boshlash", callback_data="intr_new")
    b.adjust(2)
    return b.as_markup()


def reading_start_keyboard() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="📖 Savollarni boshlash", callback_data="read_start")
    return b.as_markup()


def listening_start_keyboard() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="🎧 Audioni tinglash", callback_data="listen_start")
    return b.as_markup()


def listening_quiz_keyboard() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="✅ Savollarni boshlash", callback_data="listen_quiz")
    return b.as_markup()


def speaking_skip_keyboard() -> InlineKeyboardMarkup:
    """Speaking topic uchun 'Javob bera olmayman' (o'sha topicga 0 ball)."""
    b = InlineKeyboardBuilder()
    b.button(text="⏭ Javob bera olmayman", callback_data="speak_skip")
    return b.as_markup()


def new_test_keyboard() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="🔄 Yangi test", callback_data="begin_test_new")
    return b.as_markup()
