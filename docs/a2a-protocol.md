# A2A protocol

```json
{
  "source": "intake",
  "target": "decision",
  "intent": "qualify",
  "payload": { "request": "Need an OpenClaw review" },
  "tokens": ["commerce:read", "mesh:route"],
  "trace_id": "…"
}
```

## Rules

- `tokens` are capability scopes, never bearer secrets.
- `trace_id` is copied onto child envelopes.
- Unknown targets are not errors; they become a no-op on the in-process bus.
- The Go gateway accepts the same JSON on `POST /v1/envelopes`.
- RECON and five-agent-os should keep their own runtimes and speak this envelope
  at the boundary.
