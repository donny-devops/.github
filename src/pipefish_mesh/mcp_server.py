"""Minimal stdio MCP server exposing mesh tools."""

from __future__ import annotations

import asyncio
import json
import sys
from typing import Any

from .commerce import Ledger, load_catalog
from .protocol import Envelope, MeshBus
from .vectors import TokenMemory
from .workflows import run_revenue_intake

PROTOCOL_VERSION = "2024-11-05"
SERVER_INFO = {"name": "pipefish-mesh", "version": "0.1.0"}

TOOLS = [
    {
        "name": "mesh.ping",
        "description": "Health check for the PipeFish mesh control plane.",
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
    {
        "name": "catalog.list",
        "description": "List monetizable PipeFish / OpenClaw service SKUs.",
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
    {
        "name": "ledger.record",
        "description": "Recognize revenue for a catalog SKU.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "sku_id": {"type": "string"},
                "source": {"type": "string"},
            },
            "required": ["sku_id"],
        },
    },
    {
        "name": "dag.revenue_intake",
        "description": "Qualify a request, price it, and book it on the ledger.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "request": {"type": "string"},
                "sku_id": {"type": "string"},
            },
            "required": ["request"],
        },
    },
    {
        "name": "memory.search",
        "description": "Search embedded token memory for similar commercial or ops notes.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "k": {"type": "integer"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "a2a.send",
        "description": "Publish an agent-to-agent envelope on the in-process bus.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "source": {"type": "string"},
                "target": {"type": "string"},
                "intent": {"type": "string"},
                "payload": {"type": "object"},
            },
            "required": ["source", "target", "intent"],
        },
    },
]


class MeshRuntime:
    def __init__(self) -> None:
        self.catalog = load_catalog()
        self.ledger = Ledger()
        self.memory = TokenMemory()
        self.bus = MeshBus()
        for sku in self.catalog.list():
            self.memory.upsert(sku.id, f"{sku.name} {sku.description}", {"sku": sku.id})

    async def call(self, name: str, arguments: dict[str, Any]) -> Any:
        if name == "mesh.ping":
            return {"ok": True, "server": SERVER_INFO}
        if name == "catalog.list":
            return self.catalog.to_dicts()
        if name == "ledger.record":
            sku = self.catalog.get(arguments["sku_id"])
            entry_id = self.ledger.recognize(sku, source=str(arguments.get("source", "mcp")))
            return {"entry_id": entry_id, "recognized_cents": self.ledger.recognized_cents()}
        if name == "dag.revenue_intake":
            result = await run_revenue_intake(
                str(arguments["request"]),
                str(arguments.get("sku_id", "mesh.lane.ping")),
                self.catalog,
                self.ledger,
                self.memory,
            )
            return {
                "status": result.status,
                "outputs": result.outputs,
                "recognized_cents": self.ledger.recognized_cents(),
            }
        if name == "memory.search":
            return self.memory.search(str(arguments["query"]), int(arguments.get("k", 5)))
        if name == "a2a.send":
            envelope = Envelope(
                source=str(arguments["source"]),
                target=str(arguments["target"]),
                intent=str(arguments["intent"]),
                payload=dict(arguments.get("payload") or {}),
            )
            replies = await self.bus.publish(envelope)
            return {
                "published": envelope.to_dict(),
                "replies": [item.to_dict() for item in replies],
            }
        raise ValueError(f"unknown tool: {name}")


def _result(payload: Any) -> dict[str, Any]:
    return {"content": [{"type": "text", "text": json.dumps(payload, indent=2)}]}


def _rpc_result(req_id: Any, result: Any) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": req_id, "result": result}


def _rpc_error(req_id: Any, message: str, code: int = -32000) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}


async def handle(runtime: MeshRuntime, message: dict[str, Any]) -> dict[str, Any] | None:
    method = message.get("method")
    req_id = message.get("id")
    if method == "initialize":
        return _rpc_result(
            req_id,
            {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {"tools": {}},
                "serverInfo": SERVER_INFO,
            },
        )
    if method == "notifications/initialized":
        return None
    if method == "tools/list":
        return _rpc_result(req_id, {"tools": TOOLS})
    if method == "tools/call":
        params = message.get("params") or {}
        try:
            payload = await runtime.call(params.get("name"), params.get("arguments") or {})
        except Exception as exc:  # noqa: BLE001
            return _rpc_result(req_id, {"isError": True, **_result({"error": str(exc)})})
        return _rpc_result(req_id, _result(payload))
    if method == "ping":
        return _rpc_result(req_id, {})
    return _rpc_error(req_id, f"unknown method: {method}", code=-32601)


async def _stdio_loop() -> None:
    runtime = MeshRuntime()
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        message = json.loads(line)
        reply = await handle(runtime, message)
        if reply is not None:
            sys.stdout.write(json.dumps(reply) + "\n")
            sys.stdout.flush()


def main() -> None:
    asyncio.run(_stdio_loop())


if __name__ == "__main__":
    main()
