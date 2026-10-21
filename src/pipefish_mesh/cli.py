"""CLI for catalog, ledger, DAG intake, and MCP."""

from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

from .commerce import Ledger, load_catalog
from .mcp_server import main as mcp_main
from .vectors import TokenMemory
from .workflows import run_revenue_intake


def main() -> None:
    parser = argparse.ArgumentParser(prog="pipefish-mesh")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("catalog", help="Print the service catalog as JSON")
    sub.add_parser("mcp", help="Start the stdio MCP server")

    intake = sub.add_parser("intake", help="Run the revenue-intake DAG")
    intake.add_argument("request")
    intake.add_argument("--sku", default="mesh.lane.ping")
    intake.add_argument("--ledger", default=":memory:")

    args = parser.parse_args()
    if args.command == "catalog":
        print(json.dumps(load_catalog().to_dicts(), indent=2))
        return
    if args.command == "mcp":
        mcp_main()
        return
    if args.command == "intake":
        catalog = load_catalog()
        ledger = Ledger(Path(args.ledger) if args.ledger != ":memory:" else ":memory:")
        memory = TokenMemory()
        result = asyncio.run(run_revenue_intake(args.request, args.sku, catalog, ledger, memory))
        print(
            json.dumps(
                {
                    "status": result.status,
                    "outputs": result.outputs,
                    "recognized_cents": ledger.recognized_cents(),
                },
                indent=2,
            )
        )
