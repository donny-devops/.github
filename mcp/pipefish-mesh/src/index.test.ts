import assert from "node:assert/strict";
import test from "node:test";
import { callTool, handleMessage, SERVER_INFO } from "./index.ts";

test("mesh.ping returns server info", () => {
  const result = callTool("mesh.ping");
  assert.equal((result as { ok: boolean }).ok, true);
  assert.equal(SERVER_INFO.name, "pipefish-mesh-ts");
});

test("tools/list exposes catalog", () => {
  const reply = handleMessage({ jsonrpc: "2.0", id: 1, method: "tools/list" });
  assert.ok(reply);
  const names = (reply as { result: { tools: { name: string }[] } }).result.tools.map(
    (tool) => tool.name,
  );
  assert.ok(names.includes("catalog.list"));
});

test("a2a.envelope validates required fields", () => {
  assert.throws(() => callTool("a2a.envelope", { source: "a" }), /required/);
  const envelope = callTool("a2a.envelope", {
    source: "intake",
    target: "decision",
    intent: "qualify",
  }) as { intent: string };
  assert.equal(envelope.intent, "qualify");
});
