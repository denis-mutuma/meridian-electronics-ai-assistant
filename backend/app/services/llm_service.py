from __future__ import annotations

import json
from typing import Any

from openai import AsyncOpenAI

from app.config import settings

SYSTEM_PROMPT = (
    "You are Meridian Electronics customer support assistant. "
    "Use tools for factual operations like checking product availability, placing orders, "
    "looking up order history, and authenticating customers. "
    "If required details are missing, ask concise follow-up questions."
)


class LLMService:
    def __init__(self) -> None:
        self.client = AsyncOpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None

    def is_enabled(self) -> bool:
        return self.client is not None

    async def create_completion(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
    ) -> dict[str, Any]:
        if not self.client:
            return {
                "content": "The assistant model is not configured. Set OPENAI_API_KEY to enable live responses.",
                "tool_calls": [],
            }

        response = await self.client.chat.completions.create(
            model=settings.openai_model,
            temperature=0.2,
            messages=[{"role": "system", "content": SYSTEM_PROMPT}, *messages],
            tools=tools,
            tool_choice="auto",
        )

        choice = response.choices[0].message
        tool_calls: list[dict[str, Any]] = []

        if choice.tool_calls:
            for call in choice.tool_calls:
                parsed_args: dict[str, Any] = {}
                if call.function.arguments:
                    try:
                        loaded = json.loads(call.function.arguments)
                        if isinstance(loaded, dict):
                            parsed_args = loaded
                    except json.JSONDecodeError:
                        parsed_args = {}

                tool_calls.append(
                    {
                        "id": call.id,
                        "name": call.function.name,
                        "arguments": parsed_args,
                    }
                )

        return {
            "content": choice.content or "",
            "tool_calls": tool_calls,
        }
