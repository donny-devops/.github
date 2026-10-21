"""Agent-to-agent envelopes and an in-process mesh bus."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

Handler = Callable[["Envelope"], Any]


def _utcnow() -> datetime:
    return datetime.now(UTC)


@dataclass(slots=True)
class Envelope:
    """Signed-in-spirit A2A message. Capability tokens are scopes, not secrets."""

    source: str
    target: str
    intent: str
    payload: dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: str(uuid4()))
    trace_id: str = field(default_factory=lambda: str(uuid4()))
    tokens: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: _utcnow().isoformat())

    def child(self, *, source: str, target: str, intent: str, payload: dict[str, Any]) -> Envelope:
        return Envelope(
            source=source,
            target=target,
            intent=intent,
            payload=payload,
            trace_id=self.trace_id,
            tokens=list(self.tokens),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Envelope:
        allowed = {f.name for f in cls.__dataclass_fields__.values()}  # type: ignore[attr-defined]
        return cls(**{k: v for k, v in data.items() if k in allowed})


class MeshBus:
    """In-process fan-out bus used by the DAG engine and MCP tools."""

    def __init__(self) -> None:
        self._handlers: dict[str, list[Handler]] = {}
        self.audit: list[Envelope] = []

    def subscribe(self, target: str, handler: Handler) -> None:
        self._handlers.setdefault(target, []).append(handler)

    async def publish(self, envelope: Envelope) -> list[Envelope]:
        self.audit.append(envelope)
        replies: list[Envelope] = []
        for handler in self._handlers.get(envelope.target, []):
            result = handler(envelope)
            if hasattr(result, "__await__"):
                result = await result  # type: ignore[assignment]
            if result is not None:
                replies.append(result)
                self.audit.append(result)
        return replies
