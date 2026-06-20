"""Konfiguratsiya — .env dan o'qiladi."""
import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

load_dotenv()


def _parse_ids(raw: str) -> list[int]:
    ids: list[int] = []
    for part in (raw or "").replace(";", ",").split(","):
        part = part.strip()
        if part.lstrip("-").isdigit():
            ids.append(int(part))
    return ids


@dataclass
class Config:
    bot_token: str
    gemini_api_key: str
    superadmin_id: int
    admin_ids: list[int] = field(default_factory=list)
    gemini_model: str = "gemini-2.5-flash"
    db_path: str = "academia.db"
    disable_ssl_verify: bool = False


def load_config() -> Config:
    bot_token = os.getenv("BOT_TOKEN", "").strip()
    gemini_api_key = os.getenv("GEMINI_API_KEY", "").strip()
    superadmin_raw = os.getenv("SUPERADMIN_ID", "").strip()
    superadmin_id = int(superadmin_raw) if superadmin_raw.lstrip("-").isdigit() else 0
    admin_ids = _parse_ids(os.getenv("ADMIN_IDS", ""))
    gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip() or "gemini-2.5-flash"
    db_path = os.getenv("DB_PATH", "academia.db").strip() or "academia.db"
    disable_ssl_verify = os.getenv("DISABLE_SSL_VERIFY", "").strip().lower() in ("1", "true", "yes")

    if not bot_token:
        raise RuntimeError("BOT_TOKEN .env faylida topilmadi. .env.example dan nusxa oling.")
    if not gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY .env faylida topilmadi.")

    return Config(
        bot_token=bot_token,
        gemini_api_key=gemini_api_key,
        superadmin_id=superadmin_id,
        admin_ids=admin_ids,
        gemini_model=gemini_model,
        db_path=db_path,
        disable_ssl_verify=disable_ssl_verify,
    )


config = load_config()
