"""
services/chat_engine.py -- Agentic tool-calling loop.

Flow for each user turn:
  1. Build a conversation seeded with customer context + user message.
  2. Ask the LLM for a response (may include tool-call requests).
  3. If the model requested tools, execute each via the MCP client and
     append the results as tool messages.
  4. Repeat up to MAX_TOOL_ITERATIONS times until the model produces a
     plain-text reply (no more tool calls).
  5. Return the final assistant message to the caller.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from app.services.llm_service import LLMService
from app.services.mcp_client import MCPClient, ToolCache

logger = logging.getLogger(__name__)

# Maximum tool-call round trips per user message.
MAX_TOOL_ITERATIONS = 5


class ChatEngine:
    """Orchestrates the LLM <-> MCP tool loop for a single conversation turn."""

    def __init__(
        self,
        mcp_client: MCPClient,
        tool_cache: ToolCache,
        llm_service: LLMService,
    ) -> None:
        self.mcp_client = mcp_client
        self.tool_cache = tool_cache
        self.llm_service = llm_service

    async def respond(self, user_email: str, user_message: str) -> str:
        """
        Generate an assistant reply for the given customer message.

        The authenticated customer email is injected into the conversation
        context so the model can pass it to customer-specific MCP tools.
        """
        # Fetch the cached MCP tool list and convert to OpenAI format.
        tools = await self.tool_cache.get_tools()
        openai_tools = [self._to_openai_tool(t) for t in tools]

        # Seed the conversation: customer context first, then their message.
        messages: list[dict[str, Any]] = [
            {
                "role": "user",
                "content": (
                    "[Customer context: authenticated email = " + user_email + "]\n"
                    + user_message
                ),
            }
        ]

        for iteration in range(MAX_TOOL_ITERATIONS):
            model_response = await self.llm_service.create_completion(messages, openai_tools)
            tool_calls = model_response.get("tool_calls", [])

            # No tool calls means the model produced a final answer.
            if not tool_calls:
                content = model_response.get("content", "")
                return content if content else "I could not generate a response."

            logger.debug(
                "Iteration %d: executing %d tool call(s): %s",
                iteration + 1,
                len(tool_calls),
                [c["name"] for c in tool_calls],
            )

            # Append the assistant turn containing the tool-call requests.
            messages.append(
                {
                    "role": "assistant",
                    "content": model_response.get("content", ""),
                    "tool_calls": [
                        {
                            "id": call["id"],
                            "type": "function",
                            "function": {
                                "name": call["name"],
                                # OpenAI requires arguments as a JSON string, not a dict.
                                "arguments": json.dumps(call["arguments"]),
                            },
                        }
                        for call in tool_calls
                    ],
                }
            )

            # Execute each requested tool via MCP and append results.
            for call in tool_calls:
                try:
                    result = await self.mcp_client.call_tool(call["name"], call["arguments"])
                except Exception as exc:
                    logger.warning("Tool %s failed: %s", call["name"], exc)
                    result = {"error": str(exc)}

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": call["id"],
                        "content": json.dumps(result),
                    }
                )

        # Reached the iteration cap without a final answer.
        logger.warning("Tool loop hit MAX_TOOL_ITERATIONS (%d).", MAX_TOOL_ITERATIONS)
        return (
            "I wasn't able to complete your request in the allowed steps. "
            "Please try rephrasing or break it into smaller questions."
        )

    def _to_openai_tool(self, mcp_tool: dict[str, Any]) -> dict[str, Any]:
        """Convert an MCP tool descriptor to the OpenAI function-calling format."""
        input_schema = mcp_tool.get("inputSchema", {})
        if not isinstance(input_schema, dict):
            input_schema = {"type": "object", "properties": {}}

        return {
            "type": "function",
            "function": {
                "name": mcp_tool.get("name", "unknown_tool"),
                "description": mcp_tool.get("description", "MCP tool"),
                "parameters": input_schema,
            },
        }
