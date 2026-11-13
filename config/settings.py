"""Configurações centrais do Assistente Operacional Universal."""

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent

load_dotenv(PROJECT_ROOT / ".env")


def get_env(name: str, default: str = "") -> str:
    """Obtém uma variável de ambiente."""
    return os.getenv(name, default).strip()


APP_NAME = get_env("APP_NAME", "Assistente Operacional Universal")
APP_ENV = get_env("APP_ENV", "development")
DEBUG = get_env("DEBUG", "false").lower() == "true"
LOG_LEVEL = get_env("LOG_LEVEL", "INFO").upper()

OLLAMA_BASE_URL = get_env(
    "OLLAMA_BASE_URL",
    "http://localhost:11434",
).rstrip("/")

OLLAMA_MODEL = get_env("OLLAMA_MODEL", "llama3.2:1b")
OLLAMA_EMBEDDING_MODEL = get_env(
    "OLLAMA_EMBEDDING_MODEL",
    "nomic-embed-text",
)

TELEGRAM_BOT_TOKEN = get_env("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = get_env("OPENAI_API_KEY")

DATA_DIR = PROJECT_ROOT / "data"
STORAGE_DIR = PROJECT_ROOT / "storage"

DATA_DIR.mkdir(parents=True, exist_ok=True)
STORAGE_DIR.mkdir(parents=True, exist_ok=True)
