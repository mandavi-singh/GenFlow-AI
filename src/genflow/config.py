import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    model: str = os.getenv("GENFLOW_MODEL", "qwen3:4b-instruct")
    base_url: str = os.getenv("GENFLOW_BASE_URL", "http://localhost:11434")
    temperature: float = float(os.getenv("GENFLOW_TEMPERATURE", "0.2"))
    max_revisions: int = int(os.getenv("GENFLOW_MAX_REVISIONS", "2"))
    password: str = os.getenv("GENFLOW_PASSWORD", "")


settings = Settings()
