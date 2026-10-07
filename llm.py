from __future__ import annotations

import json
import re
from typing import TypeVar, Type

from litellm import completion
from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)


def _clean_json(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)
    return text.strip()


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
        response = completion(
            model=model,
            messages=[
                {"role": "system", "content": base_system + repair_note},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0,
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
