"""SQLAlchemy modellar (PHASE 1 — Database Schema)."""
from datetime import datetime

from sqlalchemy import ForeignKey, Integer, String, Text, Float, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


# ─────────────────────────── Grammar ───────────────────────────
class GrammarQuestion(Base):
    __tablename__ = "grammar_questions"

    id: Mapped[int] = mapped_column(primary_key=True)
    question_text: Mapped[str] = mapped_column(Text)
    option_a: Mapped[str] = mapped_column(Text)
    option_b: Mapped[str] = mapped_column(Text)
    option_c: Mapped[str] = mapped_column(Text)
    option_d: Mapped[str] = mapped_column(Text)
    correct_option: Mapped[str] = mapped_column(String(1))  # 'a' / 'b' / 'c' / 'd'
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


# ─────────────────────────── Reading ───────────────────────────
class ReadingPassage(Base):
    __tablename__ = "reading_passages"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(Text)
    passage_text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    questions: Mapped[list["ReadingQuestion"]] = relationship(
        back_populates="passage", cascade="all, delete-orphan"
    )


class ReadingQuestion(Base):
    __tablename__ = "reading_questions"

    id: Mapped[int] = mapped_column(primary_key=True)
    passage_id: Mapped[int] = mapped_column(ForeignKey("reading_passages.id", ondelete="CASCADE"))
    question_text: Mapped[str] = mapped_column(Text)
    option_a: Mapped[str] = mapped_column(Text)
    option_b: Mapped[str] = mapped_column(Text)
    option_c: Mapped[str] = mapped_column(Text)
    option_d: Mapped[str] = mapped_column(Text)
    correct_option: Mapped[str] = mapped_column(String(1))

    passage: Mapped["ReadingPassage"] = relationship(back_populates="questions")


# ─────────────────────────── Listening ───────────────────────────
class ListeningAudio(Base):
    __tablename__ = "listening_audios"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(Text)
    file_id: Mapped[str] = mapped_column(Text)  # Telegram file_id
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    questions: Mapped[list["ListeningQuestion"]] = relationship(
        back_populates="audio", cascade="all, delete-orphan"
    )


class ListeningQuestion(Base):
    __tablename__ = "listening_questions"

    id: Mapped[int] = mapped_column(primary_key=True)
    audio_id: Mapped[int] = mapped_column(ForeignKey("listening_audios.id", ondelete="CASCADE"))
    question_text: Mapped[str] = mapped_column(Text)
    option_a: Mapped[str] = mapped_column(Text)
    option_b: Mapped[str] = mapped_column(Text)
    option_c: Mapped[str] = mapped_column(Text)
    option_d: Mapped[str] = mapped_column(Text)
    correct_option: Mapped[str] = mapped_column(String(1))

    audio: Mapped["ListeningAudio"] = relationship(back_populates="questions")


# ─────────────────────────── Writing / Speaking ───────────────────────────
class WritingTopic(Base):
    __tablename__ = "writing_topics"

    id: Mapped[int] = mapped_column(primary_key=True)
    topic_text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class SpeakingTopic(Base):
    __tablename__ = "speaking_topics"

    id: Mapped[int] = mapped_column(primary_key=True)
    topic_text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


# ─────────────────────────── Adminlar ───────────────────────────
class Admin(Base):
    __tablename__ = "admins"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(Integer, unique=True)
    name: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


# ─────────────────────────── Natijalar ───────────────────────────
class TestResult(Base):
    __tablename__ = "test_results"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(Text)
    last_name: Mapped[str] = mapped_column(Text)

    grammar_score: Mapped[int] = mapped_column(Integer, default=0)
    reading_score: Mapped[int] = mapped_column(Integer, default=0)
    listening_score: Mapped[int] = mapped_column(Integer, default=0)

    writing_score: Mapped[int] = mapped_column(Integer, default=0)
    writing_feedback: Mapped[str] = mapped_column(Text, default="")

    speaking_score: Mapped[float] = mapped_column(Float, default=0.0)
    speaking_feedback: Mapped[str] = mapped_column(Text, default="")

    total_score: Mapped[float] = mapped_column(Float, default=0.0)
    percentage: Mapped[float] = mapped_column(Float, default=0.0)
    level: Mapped[str] = mapped_column(String(2), default="A1")

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
