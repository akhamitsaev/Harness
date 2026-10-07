from __future__ import annotations

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parent
ARTIFACTS_DIR = ROOT / "artifacts"
SKILLS_DIR = ROOT / "skills"
ARTIFACTS_DIR.mkdir(exist_ok=True)


def _normalize_model(name: str | None, provider: str) -> str | None:
    if not name:
        return None
    name = name.strip()
    if not name:
        return None
    return name if "/" in name else f"{provider}/{name}"


PRIMARY_MODEL = (
    os.getenv("PRIMARY_MODEL")
    or _normalize_model(os.getenv("MISTRAL"), "mistral")
    or _normalize_model(os.getenv("MISTRAL_MODEL"), "mistral")
    or "mistral/mistral-small-latest"
)

BENCHMARK_MODEL = (
    os.getenv("BENCHMARK_MODEL")
    or _normalize_model(os.getenv("DEEPSEEK_MODEL"), "deepseek")
)

NCBI_EMAIL = os.getenv("NCBI_EMAIL", "")
NCBI_TOOL = os.getenv("NCBI_TOOL", "mito-harness")
