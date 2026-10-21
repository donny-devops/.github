---
name: dag-orchestrator
description: Design and run async DAGs on the PipeFish mesh. Use when a workflow has dependencies, needs fan-out, or must stop on upstream failure.
---

# DAG Orchestrator

```python
from pipefish_mesh import DAG

dag = DAG("example")
dag.add_node("intake", intake_fn)
dag.add_node("decide", decide_fn, deps=("intake",))
dag.add_node("book", book_fn, deps=("decide",))
result = await dag.run({"request": "..."})
```

## Rules

- Node names are unique.
- Cycles raise `ValueError`.
- Failed parents mark children `skipped`.
- Keep node functions isolated — no shared mutable globals.
- Persist commercial side effects only in the `book` (or equivalent) node.

Reference pipeline: `pipefish_mesh.workflows.revenue_intake_dag`.
