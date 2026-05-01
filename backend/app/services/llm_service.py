from __future__ import annotations

import json
import logging
from typing import Any

from openai import AsyncOpenAI

from app.config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """\
You are a helpful and professional customer support assistant for Meridian Electronics, \
an online electronics retailer.

The authenticated customer's email address will be provided at the start of each \
conversation — use it when tools require an email or customer identifier.

Guidelines:
- Always use the provided tools for factual lookups: product availability, pricing, \
  order history, order status, and customer verification.
- Never guess product SKUs, prices, stock levels, or order details — always call a tool.
- When a customer asks about their orders, use the verify_customer_pin tool first if \
  the tool requires PIN verification.
- Keep responses concise and focused. If a request needs more information, ask one \
  clear follow-up question.
- If a tool returns an error or empty result, acknowledge it honestly and offer \
  alternatives (e.g. suggest contacting support for unresolvable issues).
"""


class LLMService:
    def __init__(self) -> None:
        if settings.openai_api_key:
            self.client: AsyncOpenAI | None = AsyncOpenAI(api_key=settings.openai_api_key)
            logger.info("LLMService: OpenAI client initialised (model=%s).", settings.openai_model)
        else:
            self.client = None
            logger.warning(
                "LLMService: OPENAI_API_KEY not set — responses will be placeholder text."
            )

    def is_enabled(self) -> bool:
        return self.client is not None

    async def create_completion(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
    ) -> dict[str, Any]:
        if not self.client:
            return {
                "content": (
                    "The AI assistant is not configured. "
                    "Please set OPENAI_API_KEY in your .env file to enable live responses."
                ),
                "tool_calls": [],
            }

        full_messages: list[dict[str, Any]] = [
            {"role": "system", "content": SYSTEM_PROMPT},
            *messages,
        ]

        response = await self.client.chat.completions.create(
            model=settings.openai_model,
            temperature=0.2,
            messages=full_messages,
            **({"tools": tools, "tool_choice": "auto"} if tools else {}),
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
                        logger.warning(
                            "Could not parse arguments for tool %s: %s",
                            call.function.name,
                            call.function.arguments,
                        )

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
