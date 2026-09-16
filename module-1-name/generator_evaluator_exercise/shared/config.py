"""Load configuration in one place so the harness stays focused on its loop."""

import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


# ========================
# Locate .env beside requirements.txt, regardless of which script starts the
# exercise. Students do not need to repeat setup code in starter or solution.
# ========================
PROJECT_ROOT = Path(__file__).resolve().parents[1]


def load_settings() -> tuple[str, str]:
    # ========================
    # The evaluator model is optional. Prompt and context separation still
    # apply when both requests use the same underlying model name.
    # ========================
    load_dotenv(PROJECT_ROOT / ".env")
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError(f"Set OPENAI_API_KEY in {PROJECT_ROOT / '.env'} or your environment.")

    generator_model = os.getenv("OPENAI_MODEL", "").strip()
    if not generator_model:
        raise ValueError(f"Set OPENAI_MODEL in {PROJECT_ROOT / '.env'} or your environment.")

    evaluator_model = os.getenv("OPENAI_EVALUATOR_MODEL", "").strip() or generator_model
    return generator_model, evaluator_model


def get_client() -> OpenAI:
    # ========================
    # One SDK client can make two independent requests. Each component builds
    # its own input list, so sharing the client does not share model context.
    # ========================
    load_settings()
    return OpenAI()
