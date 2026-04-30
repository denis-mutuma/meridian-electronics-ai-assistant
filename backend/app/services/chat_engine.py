from __future__ import annotations

import json
from typing import Any

from app.services.llm_service import LLMService
from app.services.mcp_client import MCPClient, ToolCache


class ChatEngine:
    def __init__(self, mcp_client: MCPClient, tool_cache: ToolCache, llm_service: LLMService) -> None:
        self.mcp_client = mcp_client
        self.tool_cache = tool_cache
        self.llm_service = llm_service

    async def respond(self, user_email: str, user_message: str) -> str:
        tools = await self.tool_cache.get_tools()
        openai_tools = [self._to_openai_tool(tool) for tool in tools]

        messages: list[dict[str, Any]] = [
            {
                "role": "user",
                "content": (
                    f"Authenticated customer email: {user_email}. "
                    f"Customer message: {user_message}"
                ),
            }
        ]

        for _ in range(5):
            model_response = await self.llm_service.create_completion(messages, openai_tools)
            tool_calls = model_response.get("tool_calls", [])

            if not tool_calls:
                content = model_response.get("content", "")
                return content if content else "I could not generate a response."

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

            for call in tool_calls:
                result = await self.mcp_client.call_tool(call["name"], call["arguments"])
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": call["id"],
                        "content": json.dumps(result),
                    }
                )

        return "I hit a tool-processing limit. Please try again with a narrower request."

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
