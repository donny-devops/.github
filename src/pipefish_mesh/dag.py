"""Async DAG engine with dependency-aware scheduling."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable, Iterable
from dataclasses import dataclass, field
from typing import Any

NodeFn = Callable[[dict[str, Any]], Awaitable[Any] | Any]


@dataclass(slots=True)
class NodeResult:
    name: str
    status: str
    output: Any = None
    error: str | None = None


@dataclass(slots=True)
class DAGResult:
    status: str
    nodes: dict[str, NodeResult] = field(default_factory=dict)

    @property
    def outputs(self) -> dict[str, Any]:
        return {name: node.output for name, node in self.nodes.items() if node.status == "ok"}


@dataclass(slots=True)
class _Node:
    name: str
    fn: NodeFn
    deps: tuple[str, ...]


class DAG:
    """Run named async/sync tasks once their dependencies succeed."""

    def __init__(self, name: str = "pipeline") -> None:
        self.name = name
        self._nodes: dict[str, _Node] = {}

    def add_node(self, name: str, fn: NodeFn, deps: Iterable[str] = ()) -> DAG:
        if name in self._nodes:
            raise ValueError(f"duplicate node: {name}")
        self._nodes[name] = _Node(name=name, fn=fn, deps=tuple(deps))
        return self

    def _validate(self) -> None:
        for node in self._nodes.values():
            for dep in node.deps:
                if dep not in self._nodes:
                    raise ValueError(f"{node.name} depends on missing node {dep}")
        visiting: set[str] = set()
        seen: set[str] = set()

        def walk(name: str) -> None:
            if name in seen:
                return
            if name in visiting:
                raise ValueError(f"cycle detected at {name}")
            visiting.add(name)
            for dep in self._nodes[name].deps:
                walk(dep)
            visiting.remove(name)
            seen.add(name)

        for name in self._nodes:
            walk(name)

    async def run(self, context: dict[str, Any] | None = None) -> DAGResult:
        self._validate()
        ctx: dict[str, Any] = dict(context or {})
        results: dict[str, NodeResult] = {}
        in_degree = {name: len(node.deps) for name, node in self._nodes.items()}
        ready = [name for name, degree in in_degree.items() if degree == 0]
        dependents: dict[str, list[str]] = {name: [] for name in self._nodes}
        for node in self._nodes.values():
            for dep in node.deps:
                dependents[dep].append(node.name)

        async def execute(name: str) -> NodeResult:
            node = self._nodes[name]
            if any(results[dep].status != "ok" for dep in node.deps):
                return NodeResult(name=name, status="skipped", error="upstream failed")
            local = {**ctx, "deps": {dep: results[dep].output for dep in node.deps}}
            try:
                value = node.fn(local)
                if hasattr(value, "__await__"):
                    value = await value
                return NodeResult(name=name, status="ok", output=value)
            except Exception as exc:  # noqa: BLE001 — node isolation
                return NodeResult(name=name, status="error", error=str(exc))

        while ready:
            batch = list(ready)
            ready.clear()
            completed = await asyncio.gather(*(execute(name) for name in batch))
            for result in completed:
                results[result.name] = result
                ctx[result.name] = result.output
                for child in dependents[result.name]:
                    in_degree[child] -= 1
                    if in_degree[child] == 0:
                        ready.append(child)

        status = "ok" if all(node.status == "ok" for node in results.values()) else "failed"
        return DAGResult(status=status, nodes=results)
