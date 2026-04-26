"""
Groq chat completions with Structured Outputs (JSON Schema).

Docs: https://console.groq.com/docs/structured-outputs
Uses strict json_schema when the configured model supports it (e.g. openai/gpt-oss-20b).
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any

from django.conf import settings

logger = logging.getLogger(__name__)

try:
    from groq import Groq
except ImportError:  # pragma: no cover
    Groq = None  # type: ignore[misc, assignment]

DEFAULT_MODEL = "openai/gpt-oss-20b"
DEFAULT_TIMEOUT = 60.0

SYSTEM_PROMPT = (
    "You are a workload planning assistant. Base answers only on the JSON the user "
    "provides. Use anonymized labels like Emp_1, Emp_2 when names are redacted. "
    "Do not fabricate data. Fill every field in the response schema; use empty "
    "arrays only when there are genuinely no risks."
)

# Strict mode: constrained decoding on supported models (see Groq structured-outputs docs).
WORKLOAD_SUGGESTION_JSON_SCHEMA: dict[str, Any] = {
    "name": "workload_suggestion",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "overview": {
                "type": "string",
                "description": "2–4 sentences summarizing rebalance advice for the period.",
            },
            "risks": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Concrete risks or bottlenecks; empty if none.",
            },
            "next_steps": {
                "type": "array",
                "items": {"type": "string"},
                "description": "3–5 actionable next steps for admins.",
            },
            "reasoning_notes": {
                "type": "string",
                "description": "Brief rationale tying recommendations to the input data.",
            },
        },
        "required": ["overview", "risks", "next_steps", "reasoning_notes"],
        "additionalProperties": False,
    },
}


def _api_key() -> str:
    key = getattr(settings, "GROQ_API_KEY", None) or os.environ.get("GROQ_API_KEY", "")
    return (key or "").strip()


def _model() -> str:
    return (
        getattr(settings, "GROQ_MODEL", None)
        or os.environ.get("GROQ_MODEL")
        or DEFAULT_MODEL
    )


def _strict_schema() -> bool:
    raw = os.environ.get("GROQ_STRUCTURED_STRICT", "1")
    return raw not in ("0", "false", "False")


def _client() -> Groq:
    if Groq is None:
        raise RuntimeError("The 'groq' package is not installed. pip install groq")
    if not _api_key():
        raise ValueError("GROQ_API_KEY is not set.")
    return Groq(api_key=_api_key(), timeout=DEFAULT_TIMEOUT)


def _format_suggestion_text(parsed: dict[str, Any]) -> str:
    overview = (parsed.get("overview") or "").strip()
    risks = parsed.get("risks") or []
    steps = parsed.get("next_steps") or []
    lines = [overview, "", "## Risks"]
    if risks:
        lines.extend(f"- {r}" for r in risks)
    else:
        lines.append("- _(none identified)_")
    lines.extend(("", "## Next steps"))
    if steps:
        lines.extend(f"- {s}" for s in steps)
    else:
        lines.append("- _(none)_")
    return "\n".join(lines)


def fetch_workload_suggestion(payload: dict[str, Any], period: str) -> dict[str, Any]:
    """
    Ask Groq for workload-balancing suggestions. Response is validated JSON (structured output).

    Returns a dict compatible with the AISuggestion view::

        {
          "content": "<markdown-friendly text for display>",
          "reasoning": "<reasoning_notes from schema>",
          "reasoning_details": [<parsed structured object>],
          "model": "<model id from API>",
        }
    """
    model = _model()
    user_content = (
        f"Period: {period}.\n"
        "Analyze workload balance, flag risks, and propose concrete next steps.\n"
        f"Workload JSON:\n{json.dumps(payload, default=str)[:8000]}"
    )
    messages: list[dict[str, str]] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]

    json_schema = dict(WORKLOAD_SUGGESTION_JSON_SCHEMA)
    json_schema["strict"] = _strict_schema()

    client = _client()
    completion = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.3,
        max_completion_tokens=2048,
        response_format={
            "type": "json_schema",
            "json_schema": json_schema,
        },
    )

    used_model = getattr(completion, "model", None) or model
    choice = completion.choices[0] if completion.choices else None
    raw = (choice.message.content if choice and choice.message else None) or ""
    raw = raw.strip()
    if not raw:
        logger.error("Groq empty content: %s", completion)
        raise ValueError("Empty content in Groq response.")

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        logger.error("Groq JSON decode error: %s", raw[:500])
        raise ValueError("Groq returned invalid JSON.") from exc

    return {
        "content": _format_suggestion_text(parsed),
        "reasoning": (parsed.get("reasoning_notes") or "").strip(),
        "reasoning_details": [parsed],
        "model": used_model,
    }
