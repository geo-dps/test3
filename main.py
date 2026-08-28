
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Config:
    bot_token: str
    db_path: str
    timezone: str
    reminder_hour: int
    reminder_minute: int

def load_config() -> Config:
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("BOT_TOKEN is required")
    return Config(
        bot_token=token,
        db_path=os.getenv("DB_PATH", "/data/streak.db"),
        timezone=os.getenv("TIMEZONE", "Europe/Berlin"),
        reminder_hour=int(os.getenv("REMINDER_HOUR", "20")),
        reminder_minute=int(os.getenv("REMINDER_MINUTE", "0")),
    )
