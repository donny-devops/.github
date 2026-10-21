import asyncio

from pipefish_mesh.dag import DAG


def test_dag_runs_dependencies_in_order() -> None:
    seen: list[str] = []

    async def first(_ctx: dict) -> int:
        seen.append("first")
        return 2

    async def second(ctx: dict) -> int:
        seen.append("second")
        return ctx["deps"]["first"] * 3

    dag = DAG().add_node("first", first).add_node("second", second, deps=("first",))
    result = asyncio.run(dag.run())
    assert result.status == "ok"
    assert result.outputs == {"first": 2, "second": 6}
    assert seen == ["first", "second"]


def test_dag_skips_after_failure() -> None:
    async def boom(_ctx: dict) -> None:
        raise RuntimeError("nope")

    async def later(_ctx: dict) -> str:
        return "should-not-run"

    dag = DAG().add_node("boom", boom).add_node("later", later, deps=("boom",))
    result = asyncio.run(dag.run())
    assert result.status == "failed"
    assert result.nodes["boom"].status == "error"
    assert result.nodes["later"].status == "skipped"


def test_cycle_is_rejected() -> None:
    dag = DAG().add_node("a", lambda ctx: 1, deps=("b",)).add_node("b", lambda ctx: 1, deps=("a",))
    try:
        asyncio.run(dag.run())
        raise AssertionError("expected cycle error")
    except ValueError as exc:
        assert "cycle" in str(exc)
