import asyncio
import json
from pathlib import Path

from pipefish_mesh.commerce import Ledger, load_catalog
from pipefish_mesh.mcp_server import MeshRuntime, handle
from pipefish_mesh.protocol import Envelope, MeshBus
from pipefish_mesh.secrets import SecretBroker
from pipefish_mesh.slack_ops import deal_blocks
from pipefish_mesh.vectors import TokenMemory, cosine, embed
from pipefish_mesh.workflows import run_revenue_intake


def test_bus_publishes_and_records_audit() -> None:
    bus = MeshBus()

    async def echo(envelope: Envelope) -> Envelope:
        return envelope.child(
            source="echo",
            target=envelope.source,
            intent="ack",
            payload={"ok": True},
        )

    bus.subscribe("alpha", echo)
    replies = asyncio.run(
        bus.publish(Envelope(source="cli", target="alpha", intent="ping", payload={"n": 1}))
    )
    assert len(replies) == 1
    assert replies[0].intent == "ack"
    assert len(bus.audit) == 2


def test_catalog_and_ledger(tmp_path: Path) -> None:
    catalog = load_catalog()
    sku = catalog.get("mesh.lane.ping")
    ledger = Ledger(tmp_path / "ledger.sqlite")
    entry_id = ledger.recognize(sku, source="test")
    assert entry_id == 1
    assert ledger.recognized_cents() == 2500
    assert ledger.entries()[0]["sku"] == "mesh.lane.ping"


def test_token_memory_ranks_similar_text() -> None:
    memory = TokenMemory()
    memory.upsert("a", "post-quantum cryptography migration lattice kem")
    memory.upsert("b", "pomodoro focus timer local persistence")
    hits = memory.search("post-quantum cryptography migration lattice")
    assert hits[0]["id"] == "a"
    assert cosine(embed("alpha beta"), embed("alpha beta")) > 0.99


def test_secret_broker_reads_env_and_file(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("PIPEFISH_DEMO_TOKEN", "from-env")
    secret_file = tmp_path / "secrets.env"
    secret_file.write_text("FILE_ONLY=from-file\n", encoding="utf-8")
    broker = SecretBroker(file_path=secret_file, ssm_prefix="")
    assert broker.get("PIPEFISH_DEMO_TOKEN") == "from-env"
    assert broker.source_of("PIPEFISH_DEMO_TOKEN").backend == "env"
    assert broker.get("FILE_ONLY") == "from-file"
    try:
        broker.get("MISSING")
        raise AssertionError("expected missing secret")
    except KeyError:
        pass


def test_revenue_intake_books_valid_request() -> None:
    catalog = load_catalog()
    ledger = Ledger()
    memory = TokenMemory()
    result = asyncio.run(
        run_revenue_intake(
            "Need a security review of our OpenClaw gateway",
            "mesh.audit.security",
            catalog,
            ledger,
            memory,
        )
    )
    assert result.status == "ok"
    assert result.outputs["book"]["booked"] is True
    assert ledger.recognized_cents() == 450000


def test_mcp_tools_list_and_catalog() -> None:
    runtime = MeshRuntime()
    listed = asyncio.run(handle(runtime, {"jsonrpc": "2.0", "id": 1, "method": "tools/list"}))
    names = {tool["name"] for tool in listed["result"]["tools"]}
    assert "catalog.list" in names
    called = asyncio.run(
        handle(
            runtime,
            {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {"name": "catalog.list", "arguments": {}},
            },
        )
    )
    payload = json.loads(called["result"]["content"][0]["text"])
    assert payload[0]["id"].startswith("mesh.")


def test_slack_blocks_include_sku() -> None:
    sku = load_catalog().get("mesh.retain.ops")
    payload = deal_blocks(sku, source="test", status="recognized")
    assert sku.id in payload["blocks"][1]["fields"][0]["text"]
    assert "8,000" in payload["text"]
    assert payload["blocks"][0]["type"] == "header"
