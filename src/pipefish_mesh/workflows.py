"""Reference DAGs that wire intake → decision → revenue → memory."""

from __future__ import annotations

from typing import Any

from .commerce import Ledger, ServiceCatalog
from .dag import DAG, DAGResult
from .protocol import Envelope, MeshBus
from .vectors import TokenMemory


def revenue_intake_dag(
    catalog: ServiceCatalog,
    ledger: Ledger,
    memory: TokenMemory,
    bus: MeshBus | None = None,
) -> DAG:
    mesh = bus or MeshBus()

    async def qualify(ctx: dict[str, Any]) -> dict[str, Any]:
        request = str(ctx.get("request", ""))
        sku_id = str(ctx.get("sku_id", "mesh.lane.ping"))
        sku = catalog.get(sku_id)
        envelope = Envelope(
            source="intake",
            target="decision",
            intent="qualify",
            payload={"request": request, "sku_id": sku.id},
            tokens=["commerce:read", "mesh:route"],
        )
        await mesh.publish(envelope)
        return {"sku_id": sku.id, "request": request}

    async def decide(ctx: dict[str, Any]) -> dict[str, Any]:
        qualified = ctx["deps"]["qualify"]
        sku = catalog.get(qualified["sku_id"])
        approved = len(qualified["request"]) >= 12
        envelope = Envelope(
            source="decision",
            target="ledger",
            intent="price",
            payload={"sku_id": sku.id, "approved": approved},
            tokens=["commerce:write"],
        )
        await mesh.publish(envelope)
        return {"approved": approved, "sku_id": sku.id}

    async def book(ctx: dict[str, Any]) -> dict[str, Any]:
        decision = ctx["deps"]["decide"]
        sku = catalog.get(decision["sku_id"])
        if not decision["approved"]:
            return {"booked": False, "reason": "request too thin to price"}
        entry_id = ledger.recognize(sku, source="mesh-dag")
        memory.upsert(
            f"ledger-{entry_id}",
            f"{sku.name} {ctx.get('request', '')}",
            {"sku": sku.id, "entry_id": entry_id},
        )
        return {"booked": True, "entry_id": entry_id, "amount_cents": sku.amount_cents}

    return (
        DAG("revenue-intake")
        .add_node("qualify", qualify)
        .add_node("decide", decide, deps=("qualify",))
        .add_node("book", book, deps=("decide",))
    )


async def run_revenue_intake(
    request: str,
    sku_id: str,
    catalog: ServiceCatalog,
    ledger: Ledger,
    memory: TokenMemory,
) -> DAGResult:
    dag = revenue_intake_dag(catalog, ledger, memory)
    return await dag.run({"request": request, "sku_id": sku_id})
