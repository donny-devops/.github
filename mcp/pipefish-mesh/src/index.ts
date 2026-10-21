#!/usr/bin/env node
/**
 * TypeScript MCP server for PipeFish Mesh.
 * Speaks newline-delimited JSON-RPC 2.0 over stdio.
 */

export const SERVER_INFO = { name: "pipefish-mesh-ts", version: "0.1.0" } as const;

export const TOOLS = [
  {
    name: "mesh.ping",
    description: "Health check for the TypeScript PipeFish MCP server.",
    inputSchema: { type: "object", properties: {}, additionalProperties: false },
  },
  {
    name: "catalog.list",
    description: "Return the built-in revenue catalog (mirrors catalog/services.json).",
    inputSchema: { type: "object", properties: {}, additionalProperties: false },
  },
  {
    name: "a2a.envelope",
    description: "Build a validated agent-to-agent envelope.",
    inputSchema: {
      type: "object",
      properties: {
        source: { type: "string" },
        target: { type: "string" },
        intent: { type: "string" },
        payload: { type: "object" },
      },
      required: ["source", "target", "intent"],
    },
  },
] as const;

const CATALOG = [
  {
    id: "mesh.lane.ping",
    name: "Paid agent ping",
    price_usd: 25,
    repo: "https://github.com/donny-devops/openclaw-revenue-engine",
  },
  {
    id: "mesh.consult.discovery",
    name: "Agentic mesh discovery",
    price_usd: 2500,
    repo: "https://github.com/donny-devops/pipefish-labs",
  },
  {
    id: "mesh.audit.security",
    name: "Agent / OpenClaw security review",
    price_usd: 4500,
    repo: "https://github.com/donny-devops/pipefish-recon",
  },
];

export function callTool(name: string, args: Record<string, unknown> = {}) {
  if (name === "mesh.ping") {
    return { ok: true, server: SERVER_INFO };
  }
  if (name === "catalog.list") {
    return CATALOG;
  }
  if (name === "a2a.envelope") {
    const source = String(args.source ?? "");
    const target = String(args.target ?? "");
    const intent = String(args.intent ?? "");
    if (!source || !target || !intent) {
      throw new Error("source, target, and intent are required");
    }
    return {
      source,
      target,
      intent,
      payload: args.payload ?? {},
      created_at: new Date().toISOString(),
    };
  }
  throw new Error(`unknown tool: ${name}`);
}

export function handleMessage(message: {
  jsonrpc?: string;
  id?: number | string | null;
  method?: string;
  params?: { name?: string; arguments?: Record<string, unknown> };
}) {
  const { id, method, params } = message;
  if (method === "initialize") {
    return {
      jsonrpc: "2.0",
      id,
      result: {
        protocolVersion: "2024-11-05",
        capabilities: { tools: {} },
        serverInfo: SERVER_INFO,
      },
    };
  }
  if (method === "tools/list") {
    return { jsonrpc: "2.0", id, result: { tools: TOOLS } };
  }
  if (method === "tools/call") {
    try {
      const payload = callTool(params?.name ?? "", params?.arguments ?? {});
      return {
        jsonrpc: "2.0",
        id,
        result: { content: [{ type: "text", text: JSON.stringify(payload, null, 2) }] },
      };
    } catch (error) {
      const text = error instanceof Error ? error.message : String(error);
      return {
        jsonrpc: "2.0",
        id,
        result: { isError: true, content: [{ type: "text", text }] },
      };
    }
  }
  if (method === "notifications/initialized") {
    return null;
  }
  return { jsonrpc: "2.0", id, error: { code: -32601, message: `unknown method: ${method}` } };
}

async function serveStdio() {
  const { createInterface } = await import("node:readline");
  const rl = createInterface({ input: process.stdin, crlfDelay: Infinity });
  for await (const line of rl) {
    if (!line.trim()) continue;
    const reply = handleMessage(JSON.parse(line));
    if (reply) {
      process.stdout.write(`${JSON.stringify(reply)}\n`);
    }
  }
}

if (import.meta.url === `file://${process.argv[1]}`) {
  serveStdio().catch((error) => {
    console.error(error);
    process.exit(1);
  });
}
