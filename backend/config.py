"""Shared settings for the Campus Customs backend.

Loads the first .env found in this folder or a parent folder (e.g. the shared
course-root .env) and locates the course data folder (campus_customs.db and
products/). Real keys are never stored in the project; see ../.env.example.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

HERE = Path(__file__).resolve().parent
PROJECT_DIR = HERE.parent  # hw4/


def _load_env() -> None:
    for folder in (HERE, *HERE.parents):
        if (folder / ".env").is_file():
            load_dotenv(folder / ".env")
            return


_load_env()

# ---- Shared settings (override in .env) ------------------------------------
MODEL = os.getenv("CAMPUS_CUSTOMS_MODEL", "gpt-5.6-sol")
PORTKEY_BASE_URL = os.getenv("PORTKEY_BASE_URL", "https://api.portkey.ai/v1").rstrip("/")
FRONTEND_ORIGIN = os.getenv("CAMPUS_CUSTOMS_FRONTEND_ORIGIN", "http://localhost:5173")


def _legacy_iterations() -> int | None:
    """Iteration count for the 3 seeded users' legacy pbkdf2_sha256 hashes.
    Not stored in the hash itself, so it must come from the course staff. Until
    it is set, legacy logins report 'pending' instead of guessing (see auth.py)."""
    raw = os.getenv("CAMPUS_CUSTOMS_LEGACY_PBKDF2_ITERATIONS")
    return int(raw) if raw and raw.strip().isdigit() else None


LEGACY_PBKDF2_ITERATIONS = _legacy_iterations()


def _data_dir() -> Path:
    """Course data folder (campus_customs.db, products/). It is not part of the
    submission: by default it is looked for inside hw4/, then one level up."""
    configured = os.getenv("CAMPUS_CUSTOMS_DATA_DIR")
    if configured:
        path = Path(configured).expanduser()
        return path if path.is_absolute() else (PROJECT_DIR / path).resolve()
    for candidate in (PROJECT_DIR / "data", PROJECT_DIR.parent / "data"):
        if candidate.is_dir():
            return candidate
    return PROJECT_DIR / "data"


DATA_DIR = _data_dir()
DB_PATH = DATA_DIR / "campus_customs.db"
PRODUCTS_DIR = DATA_DIR / "products"
PROMPTS_DIR = HERE / "prompts"
OUTPUT_DIR = PROJECT_DIR / "output"


def make_model():
    """OpenAI model (MODEL) through the Portkey gateway, for the PydanticAI agent.
    Imported lazily so the product/auth routes don't need pydantic_ai installed."""
    from openai import AsyncOpenAI
    from pydantic_ai.models.openai import OpenAIResponsesModel
    from pydantic_ai.providers.openai import OpenAIProvider

    portkey_api_key = os.environ["PORTKEY_API_KEY"]
    client = AsyncOpenAI(
        api_key=portkey_api_key,
        base_url=PORTKEY_BASE_URL,
        default_headers={"x-portkey-api-key": portkey_api_key},
    )
    return OpenAIResponsesModel(MODEL, provider=OpenAIProvider(openai_client=client))
