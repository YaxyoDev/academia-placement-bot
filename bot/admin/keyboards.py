"""Admin panel klaviaturalari (PHASE 4)."""
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def main_menu(is_superadmin: bool) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    if is_superadmin:
        b.button(text="👤 Adminlar boshqaruvi", callback_data="adm:admins")
    b.button(text="📖 Reading", callback_data="adm:reading")
    b.button(text="🎧 Listening", callback_data="adm:listening")
    b.button(text="✍️ Writing", callback_data="adm:writing")
    b.button(text="🎤 Speaking", callback_data="adm:speaking")
    b.adjust(1)
    return b.as_markup()


def _back_button(b: InlineKeyboardBuilder) -> None:
    b.button(text="⬅️ Orqaga", callback_data="adm:back")


def reading_menu() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="➕ Passage qo'shish", callback_data="adm:reading:addp")
    b.button(text="➕ Passagega savol qo'shish", callback_data="adm:reading:addq")
    b.button(text="🗑 Passage o'chirish", callback_data="adm:reading:del")
    b.button(text="📋 Passagelar ro'yxati", callback_data="adm:reading:list")
    _back_button(b)
    b.adjust(1)
    return b.as_markup()


def listening_menu() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="➕ Audio qo'shish", callback_data="adm:listening:adda")
    b.button(text="➕ Audioga savol qo'shish", callback_data="adm:listening:addq")
    b.button(text="🗑 Audio o'chirish", callback_data="adm:listening:del")
    b.button(text="📋 Audiolar ro'yxati", callback_data="adm:listening:list")
    _back_button(b)
    b.adjust(1)
    return b.as_markup()


def writing_menu() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="➕ Topic qo'shish", callback_data="adm:writing:add")
    b.button(text="🗑 Topic o'chirish", callback_data="adm:writing:del")
    b.button(text="📋 Topiclar ro'yxati", callback_data="adm:writing:list")
    _back_button(b)
    b.adjust(1)
    return b.as_markup()


def speaking_menu() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="➕ Topic qo'shish", callback_data="adm:speaking:add")
    b.button(text="🗑 Topic o'chirish", callback_data="adm:speaking:del")
    b.button(text="📋 Topiclar ro'yxati", callback_data="adm:speaking:list")
    _back_button(b)
    b.adjust(1)
    return b.as_markup()


def admins_menu() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="➕ Admin qo'shish", callback_data="adm:admins:add")
    b.button(text="🗑 Admin o'chirish", callback_data="adm:admins:del")
    b.button(text="📋 Adminlar ro'yxati", callback_data="adm:admins:list")
    _back_button(b)
    b.adjust(1)
    return b.as_markup()
