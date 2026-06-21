"""Gemini 2.5 Flash integratsiyasi — Writing va Speaking baholash (PHASE 5)."""
import asyncio
import json
import logging
import re

import google.generativeai as genai

from bot.config import config

logger = logging.getLogger(__name__)

# Korporativ proksi/sertifikat muammosi bo'lsa: REST transport + SSL tekshiruvni o'chirish.
_transport = None
if config.disable_ssl_verify:
    import warnings

    import requests
    import urllib3

    warnings.filterwarnings("ignore")
    urllib3.disable_warnings()

    _orig_merge = requests.Session.merge_environment_settings

    def _no_verify_merge(self, url, proxies, stream, verify, cert):
        settings = _orig_merge(self, url, proxies, stream, verify, cert)
        settings["verify"] = False
        return settings

    requests.Session.merge_environment_settings = _no_verify_merge
    _transport = "rest"

genai.configure(api_key=config.gemini_api_key, transport=_transport)
_model = genai.GenerativeModel(config.gemini_model)

# Tarmoq osilib qolmasligi uchun timeout
_REQUEST_OPTIONS = {"timeout": 120}

_GEN_CONFIG = {
    "temperature": 0.3,
    "response_mime_type": "application/json",
}

WRITING_PROMPT = """Sen IELTS placement test imtihonchisisan. Foydalanuvchi quyidagi mavzuda \
ingliz tilida insho yozdi. Uning ingliz tili darajasini grammatika, lug'at, \
strukturasi va mavzuga mosligi bo'yicha baholang.

MAVZU: {topic}

FOYDALANUVCHI MATNI:
{text}

MUHIM: Inshoning uzunligi (so'z soni: {word_count} ta) shu MAVZU talabiga mosligini ham \
hisobga ol. Sobit so'z chegarasi yo'q — mavzuning kengligi/murakkabligidan kelib chiqib, \
javob mavzuni yetarlicha ochib berganini o'zing bahola. Mavzu uchun juda qisqa yoki yuzaki \
yozilgan bo'lsa, ballni pasaytir.

Faqat JSON qaytar: {{"score": <0 dan 10 gacha butun son>, "feedback": "<o'zbek tilida 2-3 gaplik qisqa izoh>"}}
Agar matn bo'sh yoki mavzuga umuman aloqasiz bo'lsa, 0 ball ber."""

SPEAKING_PROMPT = """Sen IELTS placement test imtihonchisisan. Foydalanuvchi quyidagi mavzuda \
ingliz tilida gapirib, ovozli javob yubordi (audio biriktirilgan). Uning ingliz tilida \
gapirish darajasini talaffuz, ravonlik, grammatika va lug'at bo'yicha baholang.

MAVZU: {topic}

AUDIO UZUNLIGI: {duration} soniya.
MUHIM: Javob uzunligi shu MAVZU talabiga mosligini ham hisobga ol. Sobit soniya chegarasi \
YO'Q — mavzuning kengligi/murakkabligidan kelib chiqib, javob mavzuni yetarlicha ochib \
berganini o'zing bahola. Oddiy/qisqa mavzuga qisqa javob normal bo'lishi mumkin, keng/murakkab \
mavzu esa to'liqroq javob talab qiladi. Mavzuga nisbatan javob yuzaki yoki chala bo'lsa, ballni pasaytir.

Faqat JSON qaytar: {{"score": <0 dan 10 gacha butun son>, "feedback": "<o'zbek tilida 2-3 gaplik qisqa izoh>"}}
Agar audioda nutq bo'lmasa yoki ingliz tilida bo'lmasa, 0 ball ber."""


def _parse_response(raw_text: str) -> tuple[int, str]:
    """Gemini javobidan score (0-10) va feedback ni ajratish."""
    if not raw_text:
        return 0, "Baholab bo'lmadi."
    try:
        data = json.loads(raw_text)
    except (json.JSONDecodeError, TypeError):
        # JSON ichidan qidirish (matn orasidan)
        match = re.search(r"\{.*\}", raw_text, re.DOTALL)
        if not match:
            logger.warning("Gemini javobini parse qilib bo'lmadi: %s", raw_text[:200])
            return 0, "Baholab bo'lmadi."
        try:
            data = json.loads(match.group(0))
        except json.JSONDecodeError:
            return 0, "Baholab bo'lmadi."

    try:
        score = int(round(float(data.get("score", 0))))
    except (TypeError, ValueError):
        score = 0
    score = max(0, min(10, score))
    feedback = str(data.get("feedback", "")).strip() or "Izoh berilmadi."
    return score, feedback


async def evaluate_writing(topic: str, text: str) -> tuple[int, str]:
    """Writing matnini baholash → (ball 0-10, feedback)."""
    word_count = len((text or "").split())
    prompt = WRITING_PROMPT.format(topic=topic, text=text, word_count=word_count)
    try:
        resp = await asyncio.to_thread(
            _model.generate_content, prompt,
            generation_config=_GEN_CONFIG, request_options=_REQUEST_OPTIONS,
        )
        return _parse_response(resp.text)
    except Exception as e:  # noqa: BLE001
        logger.exception("Writing baholashda xatolik: %s", e)
        return 0, "Texnik sabablarga ko'ra baholab bo'lmadi."


async def evaluate_speaking(
    topic: str, audio_bytes: bytes, mime_type: str = "audio/ogg", duration: int = 0
) -> tuple[int, str]:
    """Speaking audiosini baholash → (ball 0-10, feedback)."""
    prompt = SPEAKING_PROMPT.format(topic=topic, duration=duration)
    audio_part = {"mime_type": mime_type, "data": audio_bytes}
    try:
        resp = await asyncio.to_thread(
            _model.generate_content, [prompt, audio_part],
            generation_config=_GEN_CONFIG, request_options=_REQUEST_OPTIONS,
        )
        return _parse_response(resp.text)
    except Exception as e:  # noqa: BLE001
        logger.exception("Speaking baholashda xatolik: %s", e)
        return 0, "Texnik sabablarga ko'ra baholab bo'lmadi."
