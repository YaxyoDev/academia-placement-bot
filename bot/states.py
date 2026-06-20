"""FSM holatlari."""
from aiogram.fsm.state import State, StatesGroup


class TestStates(StatesGroup):
    """Foydalanuvchi test jarayoni holatlari."""
    waiting_first_name = State()
    waiting_last_name = State()
    quiz = State()       # grammar / reading / listening (section context da)
    writing = State()    # matn kutilmoqda
    speaking = State()   # ovozli xabar kutilmoqda


class AdminStates(StatesGroup):
    """Admin panel holatlari."""
    # Reading
    passage_title = State()
    passage_text = State()
    reading_q_passage_id = State()
    reading_q_poll = State()
    passage_delete = State()
    # Listening
    audio_file = State()
    audio_title = State()
    listening_q_audio_id = State()
    listening_q_poll = State()
    audio_delete = State()
    # Writing
    writing_topic_add = State()
    writing_topic_delete = State()
    # Speaking
    speaking_topic_add = State()
    speaking_topic_delete = State()
    # Adminlar
    admin_add = State()
    admin_remove = State()
