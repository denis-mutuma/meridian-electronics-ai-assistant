"""
services/mcp_client.py — Streamable HTTP client for the MCP tool server.

Protocol: JSON-RPC 2.0 over HTTPS (MCP Streamable HTTP transport).

Sequence:
  1. initialize()  — handshake; server returns a session ID via the
                     Mcp-Session-Id response header (or JSON body).
  2. list_tools()  — discover the server's available tools.
  3. call_tool()   — invoke a named tool with typed arguments.

The Accept header must include "text/event-stream" because MCP servers
using SSE return 406 Not Acceptable without it.
"""

from __future__ import annotations

import asyncio
import json
import logging
import uuid
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class MCPClient:
    """
    Stateful HTTP client for a single MCP server endpoint.

    Each HTTP call creates a fresh httpx.AsyncClient, so concurrent
    calls from different requests are safe. The session ID is set only
    during initialize() which runs once at startup.
    """

    def __init__(self, server_url: str, timeout_seconds: float = 30.0) -> None:
        self.server_url = server_url
        self.timeout_seconds = timeout_seconds
        # Session ID obtained after initialize(); attached to subsequent requests.
        self._session_id: str | None = None

    async def initialize(self) -> None:
        """
        Perform the MCP initialize handshake.

        Must be called before list_tools() or call_tool().
        Stores the session ID for use in all later requests.
        """
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
        # Some servers embed the session ID in the JSON body instead of headers.
        self._session_id = response.get("sessionId")
        logger.debug("MCP initialized, session_id=%s", self._session_id)

    async def list_tools(self) -> list[dict[str, Any]]:
        """
        Retrieve the list of tools exposed by the MCP server.

        Returns tool descriptor dicts with "name", "description", and
        "inputSchema" keys at minimum.
        """
        payload = {
            "jsonrpc": "2.0",
            "id": self._new_request_id(),
            "method": "tools/list",
            "params": {},
        }
        response = await self._post(payload)
        tools = response.get("tools", [])
        # Defensive: filter out non-dict entries from malformed responses.
        if not isinstance(tools, list):
            return []
        return [tool for tool in tools if isinstance(tool, dict)]

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """
        Invoke a named MCP tool with the provided arguments.

        Args:
            name:      Tool name exactly as returned by list_tools().
            arguments: Keyword arguments matching the tool's inputSchema.

        Returns:
            The tool result dict (shape varies per tool).

        Raises:
            RuntimeError: if the server returns a JSON-RPC application error.
        """
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

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _new_request_id(self) -> str:
        """Generate a unique JSON-RPC request ID."""
        return str(uuid.uuid4())

    @staticmethod
    def _parse_sse_body(text: str) -> dict[str, Any]:
        """
        Extract the first JSON-RPC message from an SSE-formatted response body.

        SSE lines look like:  data: {"jsonrpc":"2.0","id":"...","result":{...}}
        Raises RuntimeError if no valid JSON-RPC data line is found.
        """
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
        """
        Send a JSON-RPC POST and return the unwrapped result dict.

        Raises:
            httpx.HTTPStatusError: for non-2xx HTTP responses.
            RuntimeError: for JSON-RPC errors or unexpected response shapes.
        """
        headers = {
            "Content-Type": "application/json",
            # Must include text/event-stream to satisfy MCP servers using SSE.
            "Accept": "application/json, text/event-stream",
        }
        # Attach session ID to all requests after initialize() succeeds.
        if self._session_id:
            headers["Mcp-Session-Id"] = self._session_id

        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            response = await client.post(self.server_url, json=payload, headers=headers)

        response.raise_for_status()

        # MCP servers may reply with either application/json or text/event-stream.
        # Parse SSE bodies by extracting the first `data:` line that contains a
        # valid JSON-RPC response; fall back to regular JSON otherwise.
        content_type = response.headers.get("content-type", "")
        if "text/event-stream" in content_type:
            body = self._parse_sse_body(response.text)
        else:
            body = response.json()

        # Surface JSON-RPC application-level errors as Python exceptions.
        if "error" in body:
            message = body["error"].get("message", "MCP error")
            raise RuntimeError(f"MCP error: {message}")

        result = body.get("result", {})
        if not isinstance(result, dict):
            raise RuntimeError(f"Unexpected MCP result type: {type(result)}")

        # Some servers return the session ID in a response header instead of the body.
        session_header = response.headers.get("Mcp-Session-Id")
        if session_header:
            self._session_id = session_header

        return result


class ToolCache:
    """
    Thread-safe in-memory cache for MCP tool descriptors.

    Tools are discovered once at startup and stored here. All chat
    requests read from this cache, avoiding repeated network round trips.
    """

    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._tools: list[dict[str, Any]] = []

    async def set_tools(self, tools: list[dict[str, Any]]) -> None:
        """Replace the cached tool list (called once during app startup)."""
        async with self._lock:
            self._tools = tools

    async def get_tools(self) -> list[dict[str, Any]]:
        """Return a snapshot copy of the cached tools."""
        async with self._lock:
            return list(self._tools)
