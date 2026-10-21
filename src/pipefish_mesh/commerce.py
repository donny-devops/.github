"""Service catalog and SQLite ledger for RevOps / agent commerce."""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

CATALOG_PATH = Path(__file__).resolve().parents[2] / "catalog" / "services.json"


@dataclass(frozen=True, slots=True)
class Sku:
    id: str
    name: str
    price_usd: float
    cadence: str
    lane: str
    description: str
    repo: str | None = None

    @property
    def amount_cents(self) -> int:
        return int(round(self.price_usd * 100))


class ServiceCatalog:
    def __init__(self, skus: Iterable[Sku]) -> None:
        self._skus = {sku.id: sku for sku in skus}

    def get(self, sku_id: str) -> Sku:
        try:
            return self._skus[sku_id]
        except KeyError as exc:
            raise KeyError(f"unknown sku: {sku_id}") from exc

    def list(self) -> list[Sku]:
        return list(self._skus.values())

    def to_dicts(self) -> list[dict[str, Any]]:
        return [
            {
                "id": sku.id,
                "name": sku.name,
                "price_usd": sku.price_usd,
                "cadence": sku.cadence,
                "lane": sku.lane,
                "description": sku.description,
                "repo": sku.repo,
            }
            for sku in self.list()
        ]


def load_catalog(path: str | Path | None = None) -> ServiceCatalog:
    catalog_file = Path(path) if path else CATALOG_PATH
    data = json.loads(catalog_file.read_text(encoding="utf-8"))
    return ServiceCatalog(Sku(**row) for row in data["skus"])


class Ledger:
    """Append-only commercial event store. Amounts are integer cents."""

    def __init__(self, path: str | Path = ":memory:") -> None:
        self.path = str(path)
        if self.path not in {":memory:", ""}:
            Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self.path)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS ledger (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sku TEXT NOT NULL,
                amount_cents INTEGER NOT NULL,
                currency TEXT NOT NULL,
                source TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        self._conn.commit()

    def record(
        self,
        sku: str,
        amount_cents: int,
        *,
        currency: str = "USD",
        source: str = "manual",
        status: str = "recognized",
    ) -> int:
        now = datetime.now(UTC).isoformat()
        cursor = self._conn.execute(
            """
            INSERT INTO ledger (sku, amount_cents, currency, source, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (sku, amount_cents, currency, source, status, now),
        )
        self._conn.commit()
        return int(cursor.lastrowid)

    def recognize(self, sku: Sku, *, source: str, status: str = "recognized") -> int:
        return self.record(
            sku.id,
            sku.amount_cents,
            source=source,
            status=status,
        )

    def entries(self) -> list[dict[str, Any]]:
        rows = self._conn.execute("SELECT * FROM ledger ORDER BY id ASC").fetchall()
        return [dict(row) for row in rows]

    def recognized_cents(self) -> int:
        row = self._conn.execute(
            "SELECT COALESCE(SUM(amount_cents), 0) AS total FROM ledger WHERE status = 'recognized'"
        ).fetchone()
        return int(row["total"])
