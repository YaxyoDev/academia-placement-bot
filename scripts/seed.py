"""Namuna ma'lumot bilan to'ldirish (test uchun).

Ishga tushirish:  python -m scripts.seed
Listening uchun audio file_id qo'lda admin panel orqali qo'shiladi (bu yerda audio yo'q).
"""
import asyncio
import sys

from bot.database.engine import init_db
from bot.database import crud

# Windows konsolida emoji chiqishi uchun
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:  # noqa: BLE001
    pass

# ─────────────────────────── Grammar savollari ───────────────────────────
# BU RO'YXAT YAGONA MANBA. Bot har safar ishga tushganda (main.py) shu ro'yxat
# DB ga avto-sinxronlanadi (eskilari o'chib, shulari qayta yoziladi).
# Savolni o'zgartirmoqchi/qo'shmoqchi bo'lsangiz — shu yerdan tahrirlab, botni qayta ishga tushiring.
# Format: ("savol matni", "A varianti", "B", "C", "D", "to'g'ri javob harfi: a/b/c/d")
GRAMMAR = [
    ("She ___ to school every day.", "go", "goes", "going", "gone", "b"),
    ("I have lived here ___ 2010.", "for", "since", "from", "at", "b"),
    ("This is ___ interesting book.", "a", "an", "the", "—", "b"),
    ("They ___ playing football now.", "is", "am", "are", "be", "c"),
    ("If it rains, we ___ stay home.", "will", "would", "are", "have", "a"),
    ("He is taller ___ his brother.", "then", "than", "that", "as", "b"),
    ("I'm interested ___ music.", "on", "at", "in", "for", "c"),
    ("She has ___ finished her work.", "yet", "still", "already", "ever", "c"),
    ("There ___ many people at the party.", "was", "were", "is", "has", "b"),
    ("I ___ never been to Paris.", "have", "has", "had", "am", "a"),
    ("Could you ___ me the salt?", "pass", "passing", "passed", "to pass", "a"),
    ("The film was ___ boring.", "too", "enough", "such", "very much", "a"),
    ("We must ___ our homework.", "did", "doing", "do", "to do", "c"),
    ("He runs ___ than me.", "fast", "faster", "fastest", "more fast", "b"),
    ("I look forward ___ you.", "to see", "seeing", "to seeing", "see", "c"),
    ("Neither John ___ Mary came.", "or", "nor", "and", "but", "b"),
    ("By next year I ___ graduated.", "will", "will have", "have", "had", "b"),
    ("It's the best film I've ___ seen.", "never", "ever", "yet", "still", "b"),
    ("She suggested ___ to the cinema.", "go", "to go", "going", "went", "c"),
    ("I wish I ___ more time.", "have", "had", "has", "having", "b"),
]

READING_PASSAGE = (
    "The Honey Bee",
    ("Honey bees are social insects that live in colonies. A single colony can contain "
     "up to 60,000 bees. The queen bee lays all the eggs, while worker bees collect "
     "nectar and pollen. Bees communicate through a special 'waggle dance' that tells "
     "other bees where to find flowers. Without bees, many plants could not reproduce."),
)
READING_QUESTIONS = [
    ("How many bees can one colony contain?", "6,000", "60,000", "600", "16,000", "b"),
    ("Who lays the eggs?", "Worker bees", "The queen", "Drones", "All bees", "b"),
    ("What do worker bees collect?", "Water only", "Nectar and pollen", "Wax", "Honey only", "b"),
    ("How do bees communicate?", "Sound", "Waggle dance", "Colors", "Smell only", "b"),
    ("Why are bees important for plants?", "They eat pests", "They help reproduction",
     "They make soil", "They bring rain", "b"),
]

WRITING_TOPICS = [
    "Describe your typical day. What do you usually do from morning to evening?",
    "Some people prefer to live in a big city, others in a small town. Which do you prefer and why?",
    "Write about a person who has influenced your life.",
]

SPEAKING_TOPICS = [
    "Tell me about your hometown.",
    "What is your favourite hobby and why do you enjoy it?",
    "Describe your best friend.",
    "What did you do last weekend?",
    "Talk about your future plans.",
    "What kind of music do you like?",
]


async def run() -> None:
    await init_db()

    # Grammar bu yerda qo'shilmaydi — bot ishga tushganda main.py avto-sinxronlaydi.
    print(f"ℹ️ Grammar ({len(GRAMMAR)} ta) bot ishga tushganda avto-qo'shiladi (sync).")

    pid = await crud.add_passage(*READING_PASSAGE)
    for q in READING_QUESTIONS:
        await crud.add_reading_question(pid, *q)
    print(f"✅ Reading passage (ID {pid}) + {len(READING_QUESTIONS)} ta savol qo'shildi")

    for t in WRITING_TOPICS:
        await crud.add_writing_topic(t)
    print(f"✅ {len(WRITING_TOPICS)} ta writing topic qo'shildi")

    for t in SPEAKING_TOPICS:
        await crud.add_speaking_topic(t)
    print(f"✅ {len(SPEAKING_TOPICS)} ta speaking topic qo'shildi")

    print("\nℹ️ Listening audio /admin orqali qo'lda qo'shiladi (audio file kerak).")
    print("Tayyor! Endi botni ishga tushiring: python -m bot.main")


if __name__ == "__main__":
    asyncio.run(run())
