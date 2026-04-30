"""
services/llm_service.py — OpenAI GPT-4o-mini wrapper.

Responsibilities:
  - Hold the AsyncOpenAI client (created once on startup).
  - Inject the system prompt and conversation history into every request.
  - Parse the model's tool-call requests into a normalised dict structure
    that the ChatEngine can forward to the MCP client.

If OPENAI_API_KEY is not set, create_completion returns a static fallback
message so the rest of the stack can be exercised without API access.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from openai import AsyncOpenAI

from app.config import settings

logger = logging.getLogger(__name__)

# ── System prompt ─────────────────────────────────────────────────────────────
# Instructs the model on its role, available tools, and expected behaviour.
# The customer's email is injected per-conversation by the ChatEngine (see
# chat_engine.py) so the model can personalise responses.
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
    """Thin wrapper around the OpenAI async client."""

    def __init__(self) -> None:
        # Only create the client when an API key is available.
        if settings.openai_api_key:
            self.client: AsyncOpenAI | None = AsyncOpenAI(api_key=settings.openai_api_key)
            logger.info("LLMService: OpenAI client initialised (model=%s).", settings.openai_model)
        else:
            self.client = None
            logger.warning(
                "LLMService: OPENAI_API_KEY not set — responses will be placeholder text."
            )

    def is_enabled(self) -> bool:
        """Return True if the OpenAI client is configured and ready."""
        return self.client is not None

    async def create_completion(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """
        Call the chat completions API and normalise the response.

        Args:
            messages: Conversation history in OpenAI message format.
                      The system prompt is prepended automatically.
            tools:    OpenAI-format tool definitions built from MCP tool schemas.

        Returns:
            A dict with:
              "content"    — assistant text (may be empty when tool_calls are present)
              "tool_calls" — list of { id, name, arguments } dicts (may be empty)
        """
        if not self.client:
            # Return a helpful placeholder when the API key is missing.
            return {
                "content": (
                    "The AI assistant is not configured. "
                    "Please set OPENAI_API_KEY in your .env file to enable live responses."
                ),
                "tool_calls": [],
            }

        # Build the full message list: system prompt first, then conversation.
        full_messages: list[dict[str, Any]] = [
            {"role": "system", "content": SYSTEM_PROMPT},
            *messages,
        ]

        response = await self.client.chat.completions.create(
            model=settings.openai_model,
            temperature=0.2,       # Low temperature for consistent, factual responses.
            messages=full_messages,
            # Only pass tool-related parameters when tools are actually available.
            # Sending tool_choice="auto" with tools=None causes an API error.
            **({"tools": tools, "tool_choice": "auto"} if tools else {}),
        )

        choice = response.choices[0].message
        tool_calls: list[dict[str, Any]] = []

        if choice.tool_calls:
            for call in choice.tool_calls:
                # Parse JSON arguments defensively; default to empty dict on failure.
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
