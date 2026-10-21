# `@donny-devops/pipefish-mesh-mcp`

TypeScript MCP server for the PipeFish control plane. Pair it with the Python
`pipefish-mcp` binary when you need ledger, DAG, and token-memory tools.

## Cursor / Claude config

```json
{
  "mcpServers": {
    "pipefish-mesh": {
      "command": "node",
      "args": ["--experimental-strip-types", "mcp/pipefish-mesh/src/index.ts"]
    }
  }
}
```

## Tools

| Tool | Purpose |
| --- | --- |
| `mesh.ping` | Liveness |
| `catalog.list` | Revenue SKUs |
| `a2a.envelope` | Build a validated A2A message |

Python extras (`catalog` write path, DAG intake, memory search) live in
`src/pipefish_mesh/mcp_server.py`.
