from __future__ import annotations
import os
from dataclasses import dataclass


@dataclass
class Settings:
    db_url: str = os.getenv("ASH_DB_URL", "sqlite:///data/ai_signal_hub.db")
    host: str = os.getenv("ASH_HOST", "127.0.0.1")
    port: int = int(os.getenv("ASH_PORT", "8000"))
    timezone: str = os.getenv("ASH_TZ", "America/Los_Angeles")


settings = Settings()
