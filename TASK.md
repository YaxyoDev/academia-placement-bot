# 📋 Academia IELTS — Placement Test Bot

## 🎯 Loyiha haqida
Academia IELTS o'quv markazi uchun Telegram bot orqali placement test.
**Kiosk mode** — bir qurilmada ko'p odamlar ketma-ket test topshiradi.
**Til:** Faqat O'zbek tili.
Har test boshida ism-familya so'raladi. Foydalanuvchi 5 seksiyadan o'tadi, AI Writing va Speaking ni baholaydi, oxirida daraja (A1–C2) chiqadi.

Natija namunasi: `Yaxyo Raxmatullayev — B1 (75%)`

---

## 🛠️ Stack
- **Bot:** Aiogram 3 (Polling)
- **DB:** SQLite3 + aiosqlite + SQLAlchemy (async)
- **AI:** Gemini 2.5 Flash (Writing baholash + Speaking audio to'g'ridan-to'g'ri)
- **Admin:** Aiogram 3 (same bot, admin role bilan)

---

## 🗄️ PHASE 1 — Database Schema

### Jadvallar:

- [ ] `grammar_questions`
  - id, question_text, option_a, option_b, option_c, option_d, correct_option, created_at

- [ ] `reading_passages`
  - id, title, passage_text, created_at

- [ ] `reading_questions`
  - id, passage_id (FK), question_text, option_a, option_b, option_c, option_d, correct_option

- [ ] `listening_audios`
  - id, title, file_id (Telegram file_id), created_at

- [ ] `listening_questions`
  - id, audio_id (FK), question_text, option_a, option_b, option_c, option_d, correct_option

- [ ] `writing_topics`
  - id, topic_text, created_at

- [ ] `speaking_topics`
  - id, topic_text, created_at

- [ ] `test_results`
  - id
  - first_name, last_name (test boshida kiritiladi)
  - grammar_score, reading_score, listening_score
  - writing_score, writing_feedback
  - speaking_score, speaking_feedback
  - total_score, percentage, level (A1/A2/B1/B2/C1/C2)
  - created_at

---

## 🤖 PHASE 2 — Bot Structure (Aiogram 3)

### Fayl strukturasi:
```
bot/
├── main.py
├── config.py
├── database/
│   ├── models.py
│   ├── engine.py
│   └── crud.py
├── handlers/
│   ├── start.py
│   ├── grammar.py
│   ├── reading.py
│   ├── listening.py
│   ├── writing.py
│   ├── speaking.py
│   └── result.py
├── admin/
│   ├── handlers.py
│   └── keyboards.py
├── services/
│   └── openai_service.py
├── keyboards/
│   └── inline.py
└── utils/
    └── scoring.py
```

---

## 📝 PHASE 3 — Foydalanuvchi Bot Flow

### 3.1 Start
- [ ] `/start` — Xush kelibsiz xabari (o'zbek tilida):
  ```
  🎓 Academia IELTS ga xush kelibsiz!
  
  Placement test orqali siz ingliz tili darajangizni aniqlaymiz.
  Test 5 bo'limdan iborat: Grammar, Reading, Listening, Writing va Speaking.
  
  Boshlash uchun ismingizni kiriting:
  ```
- [ ] **Ism so'rash** → foydalanuvchi yozadi
- [ ] **Familya so'rash** → foydalanuvchi yozadi
- [ ] Tasdiqlash xabari:
  ```
  Salom, Yaxyo Raxmatullayev! 👋
  Testni boshlashga tayyormisiz?
  ```
- [ ] "✅ Testni boshlash" tugmasi

### 3.2 Grammar Seksiyasi (20 ball)
- [ ] DB dan 20 ta savol olish
- [ ] Har bir savol inline keyboard bilan (A, B, C, D) + **⏭ Skip** tugmasi
- [ ] Javob olgach keyingi savolga o'tish
- [ ] Progress ko'rsatish: `Savol 5/20`
- [ ] Skip qilingan savollar `skipped_grammar` listga saqlanadi (FSM context da)
- [ ] Barcha savollar tugagach — skip qilinganlar qaytib chiqadi:
  ```
  ⏭ Siz 3 ta savolni o'tkazib yubordingiz. Endi ularga javob bering!
  ```
- [ ] Skip qilinganlar ham tugagach Reading ga o'tish
- [ ] Skip qilingan savollarga ham javob berilmasa — 0 ball hisoblanadi

### 3.3 Reading Seksiyasi (6 ball)
- [ ] DB dan 1 ta passage olish
- [ ] Passage matnini yuborish
- [ ] "Savollarni boshlash" tugmasi
- [ ] 5-6 ta MCQ savol (A, B, C, D) + **⏭ Skip** tugmasi
- [ ] Skip qilinganlar `skipped_reading` listga saqlanadi
- [ ] Barcha savollar tugagach — skip qilinganlar qaytib chiqadi
- [ ] Tamom bo'lgach Listening ga o'tish

### 3.4 Listening Seksiyasi (6 ball)
- [ ] DB dan 1 ta audio olish
- [ ] "🎧 Audioni tinglash va boshlash" tugmasi bosilganda:
  - Audio yuboriladi
  - Savollar boshlanadi
- [ ] 5-6 ta MCQ savol (A, B, C, D) + **⏭ Skip** tugmasi
- [ ] Skip qilinganlar `skipped_listening` listga saqlanadi
- [ ] Barcha savollar tugagach — skip qilinganlar qaytib chiqadi
- [ ] Tamom bo'lgach Writing ga o'tish

### 3.5 Writing Seksiyasi (10 ball)
- [ ] DB dan 1 ta writing topic olish
- [ ] Topicni yuborish, foydalanuvchi matn yozadi
- [ ] Matn qabul qilinadi → Gemini 2.5 Flash ga yuboriladi
- [ ] AI baholaydi: ball (0-10) + qisqa feedback
- [ ] Speaking ga o'tish

### 3.6 Speaking Seksiyasi (10 ball)
- [ ] DB dan 5-6 ta speaking topic olish
- [ ] Har bir topic uchun:
  - Topicni ko'rsatish
  - Foydalanuvchi voice message yuboradi
  - Audio → to'g'ridan-to'g'ri Gemini 2.5 Flash ga yuboriladi
  - Gemini → baholaydi
- [ ] Barcha speaking ballarini o'rtalashtirish

### 3.7 Natija
- [ ] Barcha ballarni hisoblash
- [ ] Foizni hisoblash: `(jami ball / 52) * 100`
- [ ] Darajani aniqlash (scoring logic)
- [ ] Chiroyli natija xabari yuborish:
  ```
  👤 Yaxyo Raxmatullayev

  📝 Grammar:   80% — B1
  📖 Reading:   60% — A2
  🎧 Listening: 70% — B1
  ✍️  Writing:   50% — A2
  🎤 Speaking:  85% — B2

  ━━━━━━━━━━━━━━━━━━━━
  🏆 Total: 75% — B1
  ```
- [ ] Writing va Speaking feedback alohida yuborish
- [ ] DB ga saqlash
- [ ] `/start` ga qaytish (keyingi odam uchun)

---

## 🔄 PHASE 3.8 — State Management (FSMContext)

### Asosiy prinsip:
- Har bir test `FSMContext` da saqlanadi
- Test davomida `/start` yoki istalgan buyruq kelsa — **interrupt handler** ishlaydi

### Interrupt Handler:
Agar foydalanuvchi test davomida `/start` yoki boshqa amal qilsa:
```
⚠️ Siz hozir test topshiryapsiz!

Nima qilmoqchisiz?
[✅ Davom etish]   [🔄 Yangi test boshlash]
```
- **Davom etish** — hech narsa o'zgarmaydi, test davom etadi
- **Yangi test boshlash** — FSMContext tozalanadi, `/start` dan qayta boshlanadi

### FSM States:
```
WaitingFirstName
WaitingLastName
Grammar          (joriy savol raqami context da saqlanadi)
Reading          (joriy savol raqami context da saqlanadi)
Listening        (joriy savol raqami context da saqlanadi)
Writing          (matn kutilmoqda)
Speaking         (joriy topic raqami context da saqlanadi)
```

### Context da saqlanadigan ma'lumotlar:
- `first_name`, `last_name`
- `grammar_answers` — list (har savol javobi)
- `skipped_grammar` — skip qilingan savol IDlar
- `reading_answers` — list
- `skipped_reading` — skip qilingan savol IDlar
- `listening_answers` — list
- `skipped_listening` — skip qilingan savol IDlar
- `writing_text` — user yozgan matn
- `speaking_transcripts` — list (har topic uchun Gemini javobi)
- `current_question_index` — joriy savol/topic raqami
- `is_retrying_skipped` — hozir skip qaytayotganmi (True/False)

### Scoring (har seksiya uchun alohida daraja):
| Foiz | Daraja |
|---|---|
| 0–19% | A1 |
| 20–39% | A2 |
| 40–59% | B1 |
| 60–74% | B2 |
| 75–89% | C1 |
| 90–100% | C2 |

Total foiz = barcha seksiya foizlarining o'rtachasi

## 🔑 PHASE 4 — Admin Panel

### Rollar:
- **Superadmin** — `.env` da `SUPERADMIN_ID` saqlanadi (bitta odam)
- **Admin** — DB da `admins` jadvalida saqlanadi (ko'p bo'lishi mumkin)

### Kirish:
- `/admin` — faqat adminlar va superadmin uchun menyu ochiladi
- `/overall` — faqat superadmin uchun umumiy statistika

---

### 4.0 `/admin` — Admin Menyu
Admin `/admin` yozsa quyidagi inline menyu chiqadi:
```
⚙️ Admin Panel — Academia IELTS

👤 Adminlar boshqaruvi
📝 Grammar
📖 Reading
🎧 Listening
✍️ Writing
🎤 Speaking
```

---

### 4.1 Adminlar boshqaruvi (faqat Superadmin)
- [ ] Admin qo'shish → Telegram ID so'raladi → DB ga saqlanadi
- [ ] Admin o'chirish → Telegram ID bo'yicha o'chiriladi
- [ ] Adminlar ro'yxatini ko'rish → ID va ism ko'rinadi

---

### 4.2 Grammar boshqaruvi
- [ ] ➕ Savol qo'shish:
  - Admin **Telegram Quiz Poll** yaratib botga yuboradi
  - Bot `poll` objectidan `question`, `options`, `correct_option_id` ni o'zi ajratib oladi
  - DB ga avtomatik saqlanadi
  - ✅ Admin hech qanday format yozmaydi
- [ ] 🗑 Savol o'chirish → ID bo'yicha o'chiriladi
- [ ] 📋 Savollar ro'yxati → ID va qisqa matn ko'rinadi
- [ ] ⚠️ Savollar o'chirilmasa ham qayta-qayta ishlatiladi

---

### 4.3 Reading boshqaruvi
- [ ] ➕ Passage qo'shish:
  - Passage sarlavhasi so'raladi
  - Passage matni so'raladi
  - DB ga saqlanadi
- [ ] ➕ Passagega savol qo'shish:
  - Admin Passage ID ni yozadi
  - Keyin **Telegram Quiz Poll** yuboradi → bot o'zi ajratadi → DB ga saqlanadi
- [ ] 🗑 Passage o'chirish → bog'liq savollar ham o'chiriladi
- [ ] 📋 Passagelar ro'yxati

---

### 4.4 Listening boshqaruvi
- [ ] ➕ Audio qo'shish:
  - Admin audio fayl yuboradi → Telegram file_id saqlanadi
  - Audio sarlavhasi so'raladi
- [ ] ➕ Audioga savol qo'shish:
  - Admin Audio ID ni yozadi
  - Keyin **Telegram Quiz Poll** yuboradi → bot o'zi ajratadi → DB ga saqlanadi
- [ ] 🗑 Audio o'chirish → bog'liq savollar ham o'chiriladi
- [ ] 📋 Audiolar ro'yxati

---

### 4.5 Writing topiclar
- [ ] ➕ Topic qo'shish → matn so'raladi → DB ga saqlanadi
- [ ] 🗑 Topic o'chirish → ID bo'yicha
- [ ] 📋 Topiclar ro'yxati

---

### 4.6 Speaking topiclar
- [ ] ➕ Topic qo'shish → matn so'raladi → DB ga saqlanadi
- [ ] 🗑 Topic o'chirish → ID bo'yicha
- [ ] 📋 Topiclar ro'yxati

---

### 4.7 `/overall` — Superadmin statistikasi
Faqat Superadmin ko'radi:
```
📊 Academia IELTS — Umumiy statistika

👥 Jami testlar: 124
📅 Bugun: 8
📅 Bu hafta: 43

🏆 Daraja taqsimoti:
A1 — 12 ta
A2 — 28 ta
B1 — 41 ta
B2 — 30 ta
C1 — 10 ta
C2 — 3 ta

📈 O'rtacha ball: 61%
```

---

## 🤖 PHASE 5 — Gemini 2.5 Flash Integration

### Model: `gemini-2.5-flash`
- API: Google AI Studio (`google-generativeai` Python paketi)
- Audio: to'g'ridan-to'g'ri qabul qiladi (Whisper kerak emas)
- Narx: $0.30/1M input, $2.50/1M output

### Writing baholash:
- [ ] Prompt: topic + user matni → ball (0-10) + feedback
- [ ] Structured output (JSON): `{"score": 7, "feedback": "..."}`

### Speaking baholash:
- [ ] Voice message → Telegram dan yuklab olinadi
- [ ] Audio fayl to'g'ridan-to'g'ri Gemini ga yuboriladi
- [ ] Prompt: topic + audio → ball (0-10) + feedback
- [ ] Structured output (JSON): `{"score": 7, "feedback": "..."}`
- [ ] ⚠️ Whisper kerak emas — Gemini audio ni o'zi eshitadi va baholaydi

---

## 📊 PHASE 6 — Scoring & Level Logic

### Ball taqsimoti:
| Seksiya | Max ball |
|---|---|
| Grammar | 20 |
| Reading | 6 |
| Listening | 6 |
| Writing | 10 |
| Speaking | 10 |
| **Jami** | **52** |

### Daraja aniqlash (foiz bo'yicha):
| Foiz | Daraja |
|---|---|
| 0–19% | A1 |
| 20–39% | A2 |
| 40–59% | B1 |
| 60–74% | B2 |
| 75–89% | C1 |
| 90–100% | C2 |

> ⚠️ Bu chegaralar education center bilan kelishib aniqlanadi

---

## ⚙️ PHASE 7 — Config & Deploy

- [ ] `.env` fayl:
  - `BOT_TOKEN` — BotFather dan
  - `GEMINI_API_KEY` — Google AI Studio dan (aistudio.google.com)
  - `ADMIN_IDS` — admin telegram ID lar (vergul bilan: `123456,789012`)
- [ ] `requirements.txt`:
  - `aiogram==3.x`
  - `google-generativeai`
  - `sqlalchemy[asyncio]`
  - `aiosqlite`
  - `python-dotenv`
- [ ] SQLite migration (Alembic yoki oddiy `create_all`)
- [ ] Deploy: lokal yoki VPS (polling bo'lgani uchun server shart emas dastlab)

---

## 🚀 Boshlash tartibi

1. ✅ DB schema + models
2. ✅ Bot skeleton (main.py, config, engine)
3. ✅ Foydalanuvchi flow (grammar → reading → listening → writing → speaking → result)
4. ✅ Gemini 2.5 Flash integration
5. ✅ Admin handlers
6. ✅ Scoring logic
7. ✅ Test va deploy