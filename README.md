# 🎓 Academia IELTS — Placement Test Bot

Telegram bot orqali ingliz tili darajasini aniqlovchi placement test (kiosk rejimi, o'zbek tilida).
5 seksiya: **Grammar → Reading → Listening → Writing → Speaking**. Writing va Speaking ni
**Gemini 2.5 Flash** baholaydi, oxirida CEFR daraja (A1–C2) chiqadi.

## 🛠 Stack
- aiogram 3 (polling)
- SQLAlchemy (async) + aiosqlite
- Google Gemini 2.5 Flash

## 🚀 O'rnatish

```bash
# 1. Virtual muhit (allaqachon .venv bor)
python -m venv .venv
.venv/Scripts/activate          # Windows
# source .venv/bin/activate     # Linux/Mac

# 2. Kutubxonalar
pip install -r requirements.txt

# 3. Konfiguratsiya
cp .env.example .env
# .env ni tahrirlang: BOT_TOKEN, GEMINI_API_KEY, SUPERADMIN_ID
```

### `.env`
| O'zgaruvchi | Tavsif |
|---|---|
| `BOT_TOKEN` | BotFather dan olingan token |
| `GEMINI_API_KEY` | aistudio.google.com dan |
| `SUPERADMIN_ID` | Sizning Telegram ID (adminlarni boshqaradi, `/overall`) |
| `ADMIN_IDS` | (ixtiyoriy) boshlang'ich adminlar, vergul bilan |

## ▶️ Ishga tushirish

PlacementBot papkasidan turib:

```bash
python -m bot.main
```

### (Ixtiyoriy) Namuna ma'lumot bilan to'ldirish
Botni darrov sinab ko'rish uchun:

```bash
python -m scripts.seed
```

## 📋 Foydalanish

**Foydalanuvchi:** `/start` → ism/familya → 5 seksiya → natija.

**Admin:** `/admin` → menyu orqali savol/passage/audio/topic boshqarish.
- Grammar/Reading/Listening savollari **Telegram Quiz so'rovnoma** ko'rinishida yuboriladi
  (4 variant + to'g'ri javob belgilangan) — bot avtomatik o'qib oladi.

**Superadmin:** `/overall` → umumiy statistika, `/admin` → adminlar boshqaruvi.

## 📂 Struktura
```
bot/
├── main.py              # kirish nuqtasi (polling)
├── config.py            # .env
├── states.py            # FSM holatlari
├── database/            # models, engine, crud
├── handlers/            # start, grammar, reading, listening, writing, speaking, result, quiz_engine
├── admin/               # handlers, keyboards
├── services/            # gemini_service
├── keyboards/           # inline
└── utils/               # scoring
scripts/seed.py          # namuna ma'lumot
```

## 📊 Ball taqsimoti
| Seksiya | Max | Daraja chegaralari |
|---|---|---|
| Grammar | 20 | 0–19% A1, 20–39% A2, 40–59% B1, |
| Reading | 6 | 60–74% B2, 75–89% C1, 90–100% C2 |
| Listening | 6 | |
| Writing | 10 | **Total = seksiya foizlarining o'rtachasi** |
| Speaking | 10 | |
