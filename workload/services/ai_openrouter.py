"""
OpenRouter chat-completions integration with reasoning support.

Uses OpenRouter's `reasoning` field to ask the model to produce thinking
tokens, and preserves `reasoning_details` on assistant turns so multi-turn
calls can continue from where the model left off (per OpenRouter docs).
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "google/gemma-4-26b-a4b-it:free"
DEFAULT_TIMEOUT = 60

SYSTEM_PROMPT = (
    "You are a workload planning assistant. Respond with concise, actionable "
    "bullet points grounded only in the JSON the user provides. Use anonymized "
    "labels like Emp_1, Emp_2 when names are redacted. Do not fabricate data."
)


def _api_key() -> str:
    """Read the OpenRouter API key from settings or the environment."""
    key = getattr(settings, "OPENROUTER_API_KEY", None) or os.environ.get(
        "OPENROUTER_API_KEY", ""
    )
    return (key or "").strip()


def _model() -> str:
    return (
        getattr(settings, "OPENROUTER_MODEL", None)
        or os.environ.get("OPENROUTER_MODEL")
        or DEFAULT_MODEL
    )


def _headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {_api_key()}",
        "Content-Type": "application/json",
        "HTTP-Referer": os.environ.get("OPENROUTER_REFERER", "http://localhost:8000"),
        "X-Title": os.environ.get("OPENROUTER_TITLE", "Workload Tracker"),
    }


def _post(body: dict[str, Any]) -> dict[str, Any]:
    if not _api_key():
        raise ValueError("OPENROUTER_API_KEY is not set.")
    r = requests.post(
        OPENROUTER_URL, headers=_headers(), json=body, timeout=DEFAULT_TIMEOUT
    )
    if r.status_code >= 400:
        logger.error("OpenRouter HTTP %s: %s", r.status_code, r.text[:500])
        r.raise_for_status()
    return r.json()


def _extract_message(data: dict[str, Any]) -> dict[str, Any]:
    try:
        return data["choices"][0]["message"]
    except (KeyError, IndexError) as exc:
        logger.error("OpenRouter unexpected response shape: %s", data)
        raise ValueError("Unexpected OpenRouter response shape") from exc


def call_chat(
    messages: list[dict[str, Any]],
    *,
    reasoning: bool = True,
    model: str | None = None,
) -> dict[str, Any]:
    """
    Generic chat call. Returns the assistant message dict, which contains:
      - "role": "assistant"
      - "content": str | None
      - "reasoning_details": list (only if reasoning is enabled and supported)
      - "reasoning": str (text summary, on some providers)

    Pass the returned dict back unchanged inside the next `messages` list to
    let the model continue thinking from where it left off.
    """
    body: dict[str, Any] = {"model": model or _model(), "messages": messages}
    if reasoning:
        body["reasoning"] = {"enabled": True}
    data = _post(body)
    return _extract_message(data)


def fetch_workload_suggestion(payload: dict[str, Any], period: str) -> dict[str, Any]:
    """
    Ask the model for workload-balancing suggestions for the given period.

    Returns a dict::

        {
          "content": "<assistant text>",
          "reasoning": "<thinking text or empty>",
          "reasoning_details": [...],   # pass back unmodified to continue
          "model": "<model id used>",
          "messages": [...],            # full message log incl. assistant turn
        }
    """
    model = _model()
    user_content = (
        f"Period: {period}.\n"
        "Suggest how to rebalance workload, flag risks, and propose 3-5 "
        "concrete next steps.\n"
        f"Workload JSON:\n{json.dumps(payload, default=str)[:8000]}"
    )
    messages: list[dict[str, Any]] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]
    assistant = call_chat(messages, reasoning=True, model=model)

    content = (assistant.get("content") or "").strip()
    if not content:
        raise ValueError("Empty content in OpenRouter response.")

    full_log = messages + [
        {
            "role": "assistant",
            "content": content,
            "reasoning_details": assistant.get("reasoning_details"),
        }
    ]
    return {
        "content": content,
        "reasoning": (assistant.get("reasoning") or "").strip(),
        "reasoning_details": assistant.get("reasoning_details") or [],
        "model": model,
        "messages": full_log,
    }


def continue_chat(prior_messages: list[dict[str, Any]], follow_up: str) -> dict[str, Any]:
    """
    Continue a reasoning-enabled conversation. `prior_messages` must already
    include the previous assistant turn with its `reasoning_details` preserved
    unmodified (as returned by `fetch_workload_suggestion`).
    """
    if not follow_up.strip():
        raise ValueError("Follow-up content is empty.")
    messages = list(prior_messages) + [{"role": "user", "content": follow_up}]
    assistant = call_chat(messages, reasoning=True)
    content = (assistant.get("content") or "").strip()
    return {
        "content": content,
        "reasoning": (assistant.get("reasoning") or "").strip(),
        "reasoning_details": assistant.get("reasoning_details") or [],
        "messages": messages
        + [
            {
                "role": "assistant",
                "content": content,
                "reasoning_details": assistant.get("reasoning_details"),
            }
        ],
    }
