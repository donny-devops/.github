"""Embedded token memory: hashed bag-of-tokens similarity over SQLite."""

from __future__ import annotations

import hashlib
import json
import math
import re
import sqlite3
from collections.abc import Iterable
from pathlib import Path
from typing import Any

_TOKEN = re.compile(r"[a-z0-9]{2,}")
DIM = 64


def tokenize(text: str) -> list[str]:
    return _TOKEN.findall(text.lower())


def embed(text: str, dim: int = DIM) -> list[float]:
    """Deterministic hashed bag-of-tokens vector. No external model required."""
    vector = [0.0] * dim
    tokens = tokenize(text)
    if not tokens:
        return vector
    for token in tokens:
        digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
        index = int.from_bytes(digest, "big") % dim
        vector[index] += 1.0
    norm = math.sqrt(sum(value * value for value in vector)) or 1.0
    return [value / norm for value in vector]


def cosine(left: Iterable[float], right: Iterable[float]) -> float:
    return float(sum(a * b for a, b in zip(left, right, strict=True)))


class TokenMemory:
    def __init__(self, path: str | Path = ":memory:") -> None:
        self.path = str(path)
        if self.path not in {":memory:", ""}:
            Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self.path)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS memory (
                id TEXT PRIMARY KEY,
                text TEXT NOT NULL,
                metadata TEXT NOT NULL,
                vector TEXT NOT NULL
            )
            """
        )
        self._conn.commit()

    def upsert(self, item_id: str, text: str, metadata: dict[str, Any] | None = None) -> None:
        payload = json.dumps(metadata or {}, sort_keys=True)
        vector = json.dumps(embed(text))
        self._conn.execute(
            """
            INSERT INTO memory (id, text, metadata, vector)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                text = excluded.text,
                metadata = excluded.metadata,
                vector = excluded.vector
            """,
            (item_id, text, payload, vector),
        )
        self._conn.commit()

    def search(self, query: str, k: int = 5) -> list[dict[str, Any]]:
        query_vec = embed(query)
        rows = self._conn.execute("SELECT id, text, metadata, vector FROM memory").fetchall()
        ranked: list[dict[str, Any]] = []
        for row in rows:
            score = cosine(query_vec, json.loads(row["vector"]))
            ranked.append(
                {
                    "id": row["id"],
                    "text": row["text"],
                    "metadata": json.loads(row["metadata"]),
                    "score": round(score, 6),
                }
            )
        ranked.sort(key=lambda item: item["score"], reverse=True)
        return ranked[:k]
