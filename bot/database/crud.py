"""DB CRUD funksiyalari. Har bir funksiya o'z sessiyasini ochadi."""
from datetime import datetime, timedelta

from sqlalchemy import delete, func, select

from bot.database.engine import async_session
from bot.database.models import (
    Admin,
    GrammarQuestion,
    ListeningAudio,
    ListeningQuestion,
    ReadingPassage,
    ReadingQuestion,
    SpeakingTopic,
    TestResult,
    WritingTopic,
)


def _mcq_to_dict(row) -> dict:
    return {
        "id": row.id,
        "text": row.question_text,
        "a": row.option_a,
        "b": row.option_b,
        "c": row.option_c,
        "d": row.option_d,
        "correct": row.correct_option,
    }


# ─────────────────────────── Grammar ───────────────────────────
# Grammar savollari scripts/seed.py dagi GRAMMAR ro'yxatidan boshqariladi va bot
# ishga tushganda sync_grammar_questions() orqali avto-sinxronlanadi.
async def sync_grammar_questions(questions: list[tuple]) -> int:
    """Grammar savollarini seed ro'yxati bilan to'liq almashtiradi.

    Har bir element: (text, option_a, option_b, option_c, option_d, correct) tuple.
    Eskilari o'chiriladi, ro'yxatdagilari qayta yoziladi — shu sabab seed.py dagi
    GRAMMAR ro'yxati yagona manba bo'lib qoladi (tahrirlab, botni restart qilsangiz yangilanadi).
    """
    async with async_session() as s:
        await s.execute(delete(GrammarQuestion))
        for text, a, b, c, d, correct in questions:
            s.add(GrammarQuestion(
                question_text=text, option_a=a, option_b=b,
                option_c=c, option_d=d, correct_option=correct,
            ))
        await s.commit()
        return len(questions)


async def get_random_grammar(limit: int = 20) -> list[dict]:
    async with async_session() as s:
        res = await s.execute(
            select(GrammarQuestion).order_by(func.random()).limit(limit)
        )
        return [_mcq_to_dict(r) for r in res.scalars().all()]


# ─────────────────────────── Reading ───────────────────────────
async def add_passage(title: str, passage_text: str) -> int:
    async with async_session() as s:
        p = ReadingPassage(title=title, passage_text=passage_text)
        s.add(p)
        await s.commit()
        return p.id


async def add_reading_question(passage_id, question_text, option_a, option_b, option_c, option_d, correct_option):
    async with async_session() as s:
        s.add(ReadingQuestion(
            passage_id=passage_id, question_text=question_text, option_a=option_a,
            option_b=option_b, option_c=option_c, option_d=option_d, correct_option=correct_option,
        ))
        await s.commit()


async def passage_exists(passage_id: int) -> bool:
    async with async_session() as s:
        res = await s.execute(select(ReadingPassage.id).where(ReadingPassage.id == passage_id))
        return res.scalar_one_or_none() is not None


async def delete_passage(passage_id: int) -> bool:
    async with async_session() as s:
        obj = await s.get(ReadingPassage, passage_id)
        if not obj:
            return False
        await s.delete(obj)  # cascade -> savollar ham o'chadi
        await s.commit()
        return True


async def list_passages() -> list[dict]:
    async with async_session() as s:
        res = await s.execute(
            select(ReadingPassage.id, ReadingPassage.title, func.count(ReadingQuestion.id))
            .outerjoin(ReadingQuestion)
            .group_by(ReadingPassage.id)
            .order_by(ReadingPassage.id)
        )
        return [{"id": r[0], "title": r[1], "q_count": r[2]} for r in res.all()]


async def get_random_passage_with_questions() -> dict | None:
    async with async_session() as s:
        res = await s.execute(
            select(ReadingPassage)
            .join(ReadingQuestion)
            .group_by(ReadingPassage.id)
            .order_by(func.random())
            .limit(1)
        )
        p = res.scalars().first()
        if not p:
            return None
        qres = await s.execute(
            select(ReadingQuestion).where(ReadingQuestion.passage_id == p.id)
        )
        questions = [_mcq_to_dict(q) for q in qres.scalars().all()]
        return {"id": p.id, "title": p.title, "text": p.passage_text, "questions": questions}


# ─────────────────────────── Listening ───────────────────────────
async def add_audio(title: str, file_id: str) -> int:
    async with async_session() as s:
        a = ListeningAudio(title=title, file_id=file_id)
        s.add(a)
        await s.commit()
        return a.id


async def add_listening_question(audio_id, question_text, option_a, option_b, option_c, option_d, correct_option):
    async with async_session() as s:
        s.add(ListeningQuestion(
            audio_id=audio_id, question_text=question_text, option_a=option_a,
            option_b=option_b, option_c=option_c, option_d=option_d, correct_option=correct_option,
        ))
        await s.commit()


async def audio_exists(audio_id: int) -> bool:
    async with async_session() as s:
        res = await s.execute(select(ListeningAudio.id).where(ListeningAudio.id == audio_id))
        return res.scalar_one_or_none() is not None


async def delete_audio(audio_id: int) -> bool:
    async with async_session() as s:
        obj = await s.get(ListeningAudio, audio_id)
        if not obj:
            return False
        await s.delete(obj)
        await s.commit()
        return True


async def list_audios() -> list[dict]:
    async with async_session() as s:
        res = await s.execute(
            select(ListeningAudio.id, ListeningAudio.title, func.count(ListeningQuestion.id))
            .outerjoin(ListeningQuestion)
            .group_by(ListeningAudio.id)
            .order_by(ListeningAudio.id)
        )
        return [{"id": r[0], "title": r[1], "q_count": r[2]} for r in res.all()]


async def get_random_audio_with_questions() -> dict | None:
    async with async_session() as s:
        res = await s.execute(
            select(ListeningAudio)
            .join(ListeningQuestion)
            .group_by(ListeningAudio.id)
            .order_by(func.random())
            .limit(1)
        )
        a = res.scalars().first()
        if not a:
            return None
        qres = await s.execute(
            select(ListeningQuestion).where(ListeningQuestion.audio_id == a.id)
        )
        questions = [_mcq_to_dict(q) for q in qres.scalars().all()]
        return {"id": a.id, "title": a.title, "file_id": a.file_id, "questions": questions}


# ─────────────────────────── Writing topics ───────────────────────────
async def add_writing_topic(topic_text: str):
    async with async_session() as s:
        s.add(WritingTopic(topic_text=topic_text))
        await s.commit()


async def delete_writing_topic(tid: int) -> bool:
    async with async_session() as s:
        res = await s.execute(delete(WritingTopic).where(WritingTopic.id == tid))
        await s.commit()
        return res.rowcount > 0


async def list_writing_topics() -> list[dict]:
    async with async_session() as s:
        res = await s.execute(select(WritingTopic).order_by(WritingTopic.id))
        return [{"id": r.id, "text": r.topic_text} for r in res.scalars().all()]


async def get_random_writing_topic() -> dict | None:
    async with async_session() as s:
        res = await s.execute(select(WritingTopic).order_by(func.random()).limit(1))
        r = res.scalars().first()
        return {"id": r.id, "text": r.topic_text} if r else None


# ─────────────────────────── Speaking topics ───────────────────────────
async def add_speaking_topic(topic_text: str):
    async with async_session() as s:
        s.add(SpeakingTopic(topic_text=topic_text))
        await s.commit()


async def delete_speaking_topic(tid: int) -> bool:
    async with async_session() as s:
        res = await s.execute(delete(SpeakingTopic).where(SpeakingTopic.id == tid))
        await s.commit()
        return res.rowcount > 0


async def list_speaking_topics() -> list[dict]:
    async with async_session() as s:
        res = await s.execute(select(SpeakingTopic).order_by(SpeakingTopic.id))
        return [{"id": r.id, "text": r.topic_text} for r in res.scalars().all()]


async def get_random_speaking_topics(limit: int = 6) -> list[dict]:
    async with async_session() as s:
        res = await s.execute(select(SpeakingTopic).order_by(SpeakingTopic.id).limit(limit))
        return [{"id": r.id, "text": r.topic_text} for r in res.scalars().all()]


# ─────────────────────────── Adminlar ───────────────────────────
async def add_admin(telegram_id: int, name: str = "") -> bool:
    async with async_session() as s:
        exists = await s.execute(select(Admin).where(Admin.telegram_id == telegram_id))
        if exists.scalar_one_or_none():
            return False
        s.add(Admin(telegram_id=telegram_id, name=name))
        await s.commit()
        return True


async def remove_admin(telegram_id: int) -> bool:
    async with async_session() as s:
        res = await s.execute(delete(Admin).where(Admin.telegram_id == telegram_id))
        await s.commit()
        return res.rowcount > 0


async def list_admins() -> list[dict]:
    async with async_session() as s:
        res = await s.execute(select(Admin).order_by(Admin.id))
        return [{"telegram_id": r.telegram_id, "name": r.name} for r in res.scalars().all()]


async def is_admin(telegram_id: int) -> bool:
    async with async_session() as s:
        res = await s.execute(select(Admin.id).where(Admin.telegram_id == telegram_id))
        return res.scalar_one_or_none() is not None


# ─────────────────────────── Natijalar ───────────────────────────
async def save_result(**kwargs) -> int:
    async with async_session() as s:
        r = TestResult(**kwargs)
        s.add(r)
        await s.commit()
        return r.id


async def get_stats() -> dict:
    now = datetime.utcnow()
    today_start = datetime(now.year, now.month, now.day)
    week_start = today_start - timedelta(days=today_start.weekday())

    async with async_session() as s:
        total = (await s.execute(select(func.count(TestResult.id)))).scalar() or 0
        today = (await s.execute(
            select(func.count(TestResult.id)).where(TestResult.created_at >= today_start)
        )).scalar() or 0
        week = (await s.execute(
            select(func.count(TestResult.id)).where(TestResult.created_at >= week_start)
        )).scalar() or 0
        avg = (await s.execute(select(func.avg(TestResult.percentage)))).scalar() or 0

        levels = {lvl: 0 for lvl in ("A1", "A2", "B1", "B2", "C1", "C2")}
        lvl_res = await s.execute(
            select(TestResult.level, func.count(TestResult.id)).group_by(TestResult.level)
        )
        for lvl, cnt in lvl_res.all():
            if lvl in levels:
                levels[lvl] = cnt

        return {
            "total": total,
            "today": today,
            "week": week,
            "avg": round(avg, 1),
            "levels": levels,
        }
