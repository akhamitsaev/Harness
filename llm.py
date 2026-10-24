from __future__ import annotations

import json
import re
from typing import TypeVar, Type

import os
import random
import time

from litellm import completion
from pydantic import BaseModel, ValidationError

from config import (
    LLM_TEMPERATURE,
    LLM_MAX_TOKENS,
    LLM_TIMEOUT,
    LLM_KEY_MAX_ROUNDS,
    LLM_KEY_MAX_SECONDS,
    LLM_KEY_PAUSE_MIN,
    LLM_KEY_PAUSE_MAX,
)

T = TypeVar("T", bound=BaseModel)


def _clean_json(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)
    return text.strip()

def _completion_with_key_rotation(*, model, messages):
    provider = model.split("/", 1)[0].upper()
    prefix = f"{provider}_"

    keys = [
        value
        for name, value in sorted(os.environ.items())
        if name.startswith(prefix) and "API_KEY" in name and value
    ]

    if not keys:
        raise RuntimeError(f"No API keys found for {provider}")

    started = time.monotonic()
    last_error = None

    for attempt in range(len(keys) * LLM_KEY_MAX_ROUNDS):
        if time.monotonic() - started >= LLM_KEY_MAX_SECONDS:
            break

        try:
            return completion(
                model=model,
                messages=messages,
                api_key=keys[attempt % len(keys)],
                temperature=LLM_TEMPERATURE,
                max_tokens=LLM_MAX_TOKENS,
                timeout=LLM_TIMEOUT,
            )
        except Exception as e:
            last_error = e

            time.sleep(
                random.uniform(
                    LLM_KEY_PAUSE_MIN,
                    LLM_KEY_PAUSE_MAX,
                )
            )

    raise last_error

def call_structured_llm(
    *,
    model: str,
    system_prompt: str,
    user_prompt: str,
    response_model: Type[T],
    max_attempts: int = 2,
) -> T:
    schema_text = json.dumps(response_model.model_json_schema(), ensure_ascii=False, indent=2)
    base_system = f"""{system_prompt}

Return ONLY one valid JSON object matching this JSON Schema:
{schema_text}

Rules:
- No Markdown fences.
- Do not add keys outside the schema.
- Use null when information is unavailable and null is allowed.
- Never invent identifiers, numbers, phases, significance, citations, or study results.
"""

    last_error: Exception | None = None
    repair_note = ""
    for _ in range(max_attempts):
        response = _completion_with_key_rotation(
            model=model,
            messages=[
                {"role": "system", "content": base_system + repair_note},
                {"role": "user", "content": user_prompt},
            ],
        )
        raw = response.choices[0].message.content or ""
        try:
            data = json.loads(_clean_json(raw))
            return response_model.model_validate(data)
        except (json.JSONDecodeError, ValidationError) as e:
            last_error = e
            repair_note = (
                "\nPrevious JSON was invalid. Return corrected JSON only. "
                f"Validation error: {e}\n"
            )

    raise RuntimeError(f"Structured LLM output failed after {max_attempts} attempts: {last_error}")
