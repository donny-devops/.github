# SQL, Supabase, and DBeaver

The control-plane ledger and token memory default to **SQLite** so they run
without a hosted database. Point them at Postgres when you are ready.

## Local SQLite

```bash
export PIPEFISH_LEDGER_PATH=./data/ledger.sqlite
export PIPEFISH_MEMORY_PATH=./data/memory.sqlite
python -m pipefish_mesh intake "Need a discovery workshop" --sku mesh.consult.discovery --ledger "$PIPEFISH_LEDGER_PATH"
```

Open the file in DBeaver (`SQLite` driver).

## Postgres / Supabase

Store the URL in the secret broker, never in git:

```
DATABASE_URL=postgresql://postgres:…@db.<project>.supabase.co:5432/postgres
```

SQLAlchemy 2.x sketch (install the `db` extra):

```python
from sqlalchemy import create_engine, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class LedgerRow(Base):
    __tablename__ = "ledger"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sku: Mapped[str] = mapped_column(String(64))
    amount_cents: Mapped[int]
    source: Mapped[str] = mapped_column(Text)
```

Production card events still belong in `openclaw-revenue-engine`, not this table.
