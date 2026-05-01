from __future__ import annotations

import asyncio
import json
import logging
import uuid
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class MCPClient:
    """JSON-RPC 2.0 client for the MCP server.

    The MCP server may respond with plain JSON or Server-Sent Events (SSE).
    Both formats are handled transparently by _post().
    """

    def __init__(self, server_url: str, timeout_seconds: float = 30.0) -> None:
        self.server_url = server_url
        self.timeout_seconds = timeout_seconds
        # Session ID returned by the server after initialize(); included in
        # subsequent requests as the Mcp-Session-Id header.
        self._session_id: str | None = None

    async def initialize(self) -> None:
        payload = {
            "jsonrpc": "2.0",
            "id": self._new_request_id(),
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "meridian-assistant", "version": "0.1.0"},
            },
        }
        response = await self._post(payload)
        self._session_id = response.get("sessionId")
        logger.debug("MCP initialized, session_id=%s", self._session_id)

    async def list_tools(self) -> list[dict[str, Any]]:
        payload = {
            "jsonrpc": "2.0",
            "id": self._new_request_id(),
            "method": "tools/list",
            "params": {},
        }
        response = await self._post(payload)
        tools = response.get("tools", [])
        if not isinstance(tools, list):
            return []
        return [tool for tool in tools if isinstance(tool, dict)]

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        payload = {
            "jsonrpc": "2.0",
            "id": self._new_request_id(),
            "method": "tools/call",
            "params": {
                "name": name,
                "arguments": arguments,
            },
        }
        logger.debug("Calling MCP tool: %s(%s)", name, arguments)
        return await self._post(payload)

    def _new_request_id(self) -> str:
        return str(uuid.uuid4())

    @staticmethod
    def _parse_sse_body(text: str) -> dict[str, Any]:
        # The MCP server wraps JSON-RPC responses in SSE "data:" lines.
        # Scan each line and return the first parseable JSON object.
        # Lines with "[DONE]" are SSE stream terminators and are skipped.
        for line in text.splitlines():
            line = line.strip()
            if line.startswith("data:"):
                data = line[len("data:"):].strip()
                if data and data != "[DONE]":
                    try:
                        return json.loads(data)
                    except json.JSONDecodeError:
                        continue
        raise RuntimeError("No valid JSON-RPC data found in SSE response")

    async def _post(self, payload: dict[str, Any]) -> dict[str, Any]:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }
        if self._session_id:
            headers["Mcp-Session-Id"] = self._session_id

        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            response = await client.post(self.server_url, json=payload, headers=headers)

        response.raise_for_status()

        content_type = response.headers.get("content-type", "")
        if "text/event-stream" in content_type:
            body = self._parse_sse_body(response.text)
        else:
            body = response.json()

        if "error" in body:
            message = body["error"].get("message", "MCP error")
            raise RuntimeError(f"MCP error: {message}")

        result = body.get("result", {})
        if not isinstance(result, dict):
            raise RuntimeError(f"Unexpected MCP result type: {type(result)}")

        session_header = response.headers.get("Mcp-Session-Id")
        if session_header:
            self._session_id = session_header

        return result


class ToolCache:
    """Thread-safe in-memory cache for MCP tool definitions.

    Tools are discovered once at startup and reused for every request,
    avoiding a round-trip to the MCP server on each chat turn.
    """

    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._tools: list[dict[str, Any]] = []

    async def set_tools(self, tools: list[dict[str, Any]]) -> None:
        async with self._lock:
            self._tools = tools

    async def get_tools(self) -> list[dict[str, Any]]:
        async with self._lock:
            return list(self._tools)
