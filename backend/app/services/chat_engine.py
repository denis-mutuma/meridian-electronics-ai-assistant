from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

from app.services.llm_service import LLMService
from app.services.mcp_client import MCPClient, ToolCache

logger = logging.getLogger(__name__)

# Limit how many tool-call rounds the LLM can make per request to prevent
# runaway loops and keep latency bounded.
MAX_TOOL_ITERATIONS = 5


class ChatEngine:
    def __init__(
        self,
        mcp_client: MCPClient,
        tool_cache: ToolCache,
        llm_service: LLMService | None = None,
    ) -> None:
        self.mcp_client = mcp_client
        self.tool_cache = tool_cache
        self.llm_service = llm_service
        self._tools_loaded = False
        self._tool_load_lock = asyncio.Lock()

    async def respond(self, user_email: str, user_message: str) -> str:
        await self._ensure_tools_loaded()
        llm_service = self._get_llm_service()
        tools = await self.tool_cache.get_tools()
        openai_tools = [self._to_openai_tool(t) for t in tools]

        # Prepend the customer's email as context so the LLM can pass it to
        # MCP tools that require an email or customer identifier.
        messages: list[dict[str, Any]] = [
            {
                "role": "user",
                "content": (
                    "[Customer context: authenticated email = " + user_email + "]\n"
                    + user_message
                ),
            }
        ]

        # Agentic loop: keep calling the LLM until it returns a plain text reply
        # (no tool calls) or the iteration cap is reached.
        for iteration in range(MAX_TOOL_ITERATIONS):
            model_response = await llm_service.create_completion(messages, openai_tools)
            tool_calls = model_response.get("tool_calls", [])

            if not tool_calls:
                # No tool calls means the LLM has a final answer.
                content = model_response.get("content", "")
                return content if content else "I could not generate a response."

            logger.debug(
                "Iteration %d: executing %d tool call(s): %s",
                iteration + 1,
                len(tool_calls),
                [c["name"] for c in tool_calls],
            )

            # Append the assistant's tool-call turn so the LLM sees its own
            # prior decisions when we loop back.
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
                                "arguments": json.dumps(call["arguments"]),
                            },
                        }
                        for call in tool_calls
                    ],
                }
            )

            # Execute each tool call and append results so the LLM can
            # reason over them in the next iteration.
            for call in tool_calls:
                try:
                    result = await self.mcp_client.call_tool(call["name"], call["arguments"])
                except Exception as exc:
                    logger.warning("Tool %s failed: %s", call["name"], exc)
                    # Return the error as a tool result so the LLM can
                    # acknowledge it gracefully rather than crashing.
                    result = {"error": str(exc)}

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": call["id"],
                        "content": json.dumps(result),
                    }
                )

        logger.warning("Tool loop hit MAX_TOOL_ITERATIONS (%d).", MAX_TOOL_ITERATIONS)
        return (
            "I wasn't able to complete your request in the allowed steps. "
            "Please try rephrasing or break it into smaller questions."
        )

    def _get_llm_service(self) -> LLMService:
        if self.llm_service is None:
            self.llm_service = LLMService()
        return self.llm_service

    async def _ensure_tools_loaded(self) -> None:
        if self._tools_loaded:
            return

        async with self._tool_load_lock:
            if self._tools_loaded:
                return

            try:
                await self.mcp_client.initialize()
                discovered_tools = await self.mcp_client.list_tools()
                await self.tool_cache.set_tools(discovered_tools)
                logger.info("MCP tool discovery succeeded: %d tools loaded.", len(discovered_tools))
            except Exception as exc:
                logger.warning("MCP tool discovery failed: %s", exc)
                await self.tool_cache.set_tools([])
            finally:
                self._tools_loaded = True

    def _to_openai_tool(self, mcp_tool: dict[str, Any]) -> dict[str, Any]:
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
