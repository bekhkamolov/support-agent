"""Project paths and environment settings."""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
POLICY_DIR = DATA_DIR / "policies"
EVAL_DIR = DATA_DIR / "eval"
RESULTS_DIR = ROOT / "results"
CACHE_DIR = ROOT / ".cache"

load_dotenv(ROOT / ".env")


def get_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(
            f"{name} is not set. Copy .env.example to .env and add your key."
        )
    return value
