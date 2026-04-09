# Live Dashboard u2014 Real SSE Streaming Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the fake-stagger demo in `try-it-live.tsx` with genuine SSE streaming from a new FastAPI endpoint, plus a polish pass removing dead code and fixing env var config.

**Architecture:** Add `POST /api/swarm/run/stream` to `server.py` using FastAPI's `StreamingResponse` with an async generator that instantiates and runs agents one-by-one, yielding SSE frames after each. The frontend replaces `postRun()` with a `fetch` + `ReadableStream` reader that dispatches frames to React state as they arrive. Falls back to the existing `postRun()` call if the stream endpoint is unreachable.

**Tech Stack:** Python 3.10+ / FastAPI / `StreamingResponse` / `asyncio`; Next.js 16 / TypeScript / `fetch` ReadableStream / `TextDecoder`

---

## File Map

| File | Action | Responsibility |
|------|--------|----------------|
| `packages/techtide-swarm/src/techtide_swarm/server.py` | Modify | Add SSE route `POST /api/swarm/run/stream` |
| `packages/techtide-swarm/tests/test_server.py` | Modify | Add SSE endpoint test |
| `.ui_landin_sample/minimal/components/try-it-live.tsx` | Modify | Replace fake stagger with SSE `fetch` reader |
| `.ui_landin_sample/minimal/components/live-stats.tsx` | Modify | Remove `console.error` |
| `.ui_landin_sample/minimal/next.config.ts` | Modify | Add `env: { NEXT_PUBLIC_API_URL }` |
| `.ui_landin_sample/minimal/components/stats.tsx` | Delete | Dead code |
| `.ui_landin_sample/minimal/.env.example` | Create | Document `NEXT_PUBLIC_API_URL` |
| `.ui_landin_sample/minimal/lib/config.ts` | Modify | Add comment on `apiConfig` |

---

## Task 1: SSE Endpoint in FastAPI

**Files:**

- Modify: `packages/techtide-swarm/src/techtide_swarm/server.py`

### What we're building

Add `POST /api/swarm/run/stream` inside `create_app()` (alongside the existing routes). It returns a `StreamingResponse` whose async generator iterates the roster, builds+runs each `Agent`, and yields SSE frames.

SSE frame format (two trailing newlines end each frame):

```text
event: <name>\ndata: <json>\n\n
```

- [ ] **Step 1.1: Add the imports at the top of `server.py`**

Open `packages/techtide-swarm/src/techtide_swarm/server.py`. The file already imports `from fastapi import FastAPI, HTTPException`. Add `StreamingResponse` and `json` to the import block:

```python
# Change this line (around line 9):
from fastapi import FastAPI, HTTPException
# To:
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
import json
```

- [ ] **Step 1.2: Add the SSE helper function**

After the `_stub_swarm_result` helper at the bottom of `server.py` (after line ~300), add:

```python
def _sse_frame(event: str, data: dict) -> str:
    """Format a single SSE frame: 'event: name\ndata: json\n\n'."""
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"
```

- [ ] **Step 1.3: Add the SSE route inside `create_app()`**

Inside `create_app()`, after the existing `@app.post("/api/swarm/run")` route (around line 230) and before `@app.post("/api/agent/run")`, add:

```python
    @app.post("/api/swarm/run/stream")
    async def swarm_run_stream(req: SwarmRunRequest) -> StreamingResponse:
        from techtide_swarm.agent import Agent, AgentConfig
        from techtide_swarm.core.types import LayerType
        import uuid

        async def _generate():
            pipeline_id = str(uuid.uuid4())[:8]
            yield _sse_frame("start", {"pipeline_id": pipeline_id, "task": req.task})

            roster = _get_roster()
            if req.layer:
                roster = [a for a in roster if a.get("layer") == req.layer]

            total_cost = 0.0
            last_output = ""

            for agent_cfg in roster:
                try:
                    layer_str = agent_cfg.get("layer", "operations")
                    try:
                        layer = LayerType(layer_str)
                    except ValueError:
                        layer = LayerType.OPERATIONS

                    config = AgentConfig(
                        name=agent_cfg.get("name", ""),
                        layer=layer,
                        role=agent_cfg.get("role", ""),
                        soul=agent_cfg.get("soul", ""),
                        tools=agent_cfg.get("tools", []),
                        model=agent_cfg.get("model", "sonnet"),
                        budget_limit_usd=float(
                            agent_cfg.get("budget_usd", agent_cfg.get("budget_limit_usd", 1.0))
                        ),
                    )
                    agent = Agent(config)
                    result = await agent.run(req.task)

                    total_cost += result.cost_usd
                    last_output = result.output

                    yield _sse_frame("agent", {
                        "agent_name": result.agent_name,
                        "layer": layer_str,
                        "status": result.status,
                        "output": result.output,
                        "cost_usd": round(result.cost_usd, 6),
                        "latency_ms": result.latency_ms,
                    })
                except Exception as exc:  # noqa: BLE001
                    yield _sse_frame("error", {"message": str(exc), "agent_name": agent_cfg.get("name", "")})
                    return

            yield _sse_frame("done", {
                "pipeline_id": pipeline_id,
                "total_cost_usd": round(total_cost, 6),
                "final_output": last_output,
            })

        return StreamingResponse(_generate(), media_type="text/event-stream")
```

- [ ] **Step 1.4: Verify the server still starts cleanly**

```bash
cd packages/techtide-swarm
python -c "from techtide_swarm.server import create_app; app = create_app(); print('OK')"
```

Expected output: `OK` (no import errors)

---

## Task 2: Test the SSE Endpoint

**Files:**

- Modify: `packages/techtide-swarm/tests/test_server.py`

### What we're building

Two new tests using `httpx` ASGI transport: one verifying the SSE endpoint returns `200` and `text/event-stream`, one verifying the stub/no-config path returns a `start` frame and a `done` frame.

- [ ] **Step 2.1: Write the failing tests**

Open `packages/techtide-swarm/tests/test_server.py`. Add after the last test (`test_swarm_runs_list`):

```python
@pytest.mark.asyncio
async def test_swarm_run_stream_returns_event_stream(app):
    """POST /api/swarm/run/stream must return text/event-stream content type."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test", timeout=30.0
    ) as client:
        resp = await client.post(
            "/api/swarm/run/stream",
            json={"task": "ping", "budget_usd": 0.01},
        )
    assert resp.status_code == 200
    assert "text/event-stream" in resp.headers.get("content-type", "")


@pytest.mark.asyncio
async def test_swarm_run_stream_emits_start_and_done(app):
    """SSE stream must emit at least a 'start' event and a 'done' event."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test", timeout=30.0
    ) as client:
        resp = await client.post(
            "/api/swarm/run/stream",
            json={"task": "ping", "budget_usd": 0.01},
        )
    body = resp.text
    assert "event: start" in body, f"Missing 'start' frame. Body: {body[:500]}"
    assert "event: done" in body, f"Missing 'done' frame. Body: {body[:500]}"
```

- [ ] **Step 2.2: Run to verify they fail**

```bash
cd packages/techtide-swarm
pytest tests/test_server.py::test_swarm_run_stream_returns_event_stream tests/test_server.py::test_swarm_run_stream_emits_start_and_done -v
```

Expected: `FAILED` with `404` (route doesn't exist yet)

- [ ] **Step 2.3: Confirm tests pass with the new route from Task 1**

```bash
pytest tests/test_server.py::test_swarm_run_stream_returns_event_stream tests/test_server.py::test_swarm_run_stream_emits_start_and_done -v
```

Expected: both `PASSED`

- [ ] **Step 2.4: Run the full test suite to confirm no regressions**

```bash
pytest tests/test_server.py -v
```

Expected: all existing tests still `PASSED`, plus 2 new `PASSED`

- [ ] **Step 2.5: Commit**

```bash
cd packages/techtide-swarm
git add src/techtide_swarm/server.py tests/test_server.py
git commit -m "feat(server): add POST /api/swarm/run/stream SSE endpoint"
```

---

## Task 3: SSE Client in `try-it-live.tsx`

**Files:**

- Modify: `.ui_landin_sample/minimal/components/try-it-live.tsx`

### What we're building

Replace the `postRun()` call inside `handleSubmit` with a `fetch` + `ReadableStream` reader that:
1. Sends `POST /api/swarm/run/stream`
2. Reads chunks with `response.body.getReader()`
3. Decodes with `TextDecoder` and buffers partial frames
4. Splits on `\n\n` to extract complete SSE frames
5. Parses `event:` and `data:` lines
6. Dispatches to the same React state (`setSteps`, `setFinalOutput`, `setTotalCost`, `setState`)
7. Falls back to `postRun()` if the stream request fails (e.g. 404 from local dev without new server)

The UI components (`AgentStepRow`, `StatusDot`, final output block) remain completely unchanged.

- [ ] **Step 3.1: Replace `handleSubmit` in `try-it-live.tsx`**

Open `.ui_landin_sample/minimal/components/try-it-live.tsx`.

Replace the entire `handleSubmit` function (lines ~74u2013114) with:

```typescript
async function handleSubmit(e: React.FormEvent): Promise<void> {
  e.preventDefault();
  if (!task.trim() || state === "running") return;

  setState("running");
  setSteps([]);
  setFinalOutput("");
  setTotalCost(0);
  setErrorMsg("");

  const streamUrl = `${apiConfig.url}/api/swarm/run/stream`;

  try {
    const res = await fetch(streamUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ task: task.trim(), budget_usd: 5.0 }),
    });

    // Fall back to non-streaming if SSE endpoint not available (local dev without new server)
    if (!res.ok || !res.body) {
      await _runWithFallback();
      return;
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const frames = buffer.split("\n\n");
      // Keep the last (possibly incomplete) chunk in the buffer
      buffer = frames.pop() ?? "";

      for (const frame of frames) {
        if (!frame.trim()) continue;
        const lines = frame.split("\n");
        const eventLine = lines.find((l) => l.startsWith("event:"));
        const dataLine = lines.find((l) => l.startsWith("data:"));
        if (!eventLine || !dataLine) continue;

        const eventType = eventLine.replace("event:", "").trim();
        let payload: Record<string, unknown>;
        try {
          payload = JSON.parse(dataLine.replace("data:", "").trim()) as Record<string, unknown>;
        } catch {
          continue;
        }

        if (eventType === "agent") {
          setSteps((prev) => [
            ...prev,
            {
              agentName: String(payload.agent_name ?? ""),
              status: (payload.status as AgentResult["status"]) ?? "success",
              output: String(payload.output ?? ""),
              costUsd: Number(payload.cost_usd ?? 0),
              latencyMs: Number(payload.latency_ms ?? 0),
            },
          ]);
        } else if (eventType === "done") {
          setFinalOutput(String(payload.final_output ?? ""));
          setTotalCost(Number(payload.total_cost_usd ?? 0));
          setState("done");
        } else if (eventType === "error") {
          setErrorMsg(String(payload.message ?? "Stream error"));
          setState("error");
          return;
        }
      }
    }

    // If stream ended without a done frame, mark complete
    setState((prev) => (prev === "running" ? "done" : prev));
  } catch {
    // Network failure or SSE not supported u2014 fall back to single-shot POST
    await _runWithFallback();
  }
}

async function _runWithFallback(): Promise<void> {
  try {
    const result: SwarmRunResult = await postRun(task.trim(), 5.0);

    if (result.status === "error") {
      setErrorMsg(result.error ?? "Unknown error");
      setState("error");
      return;
    }

    for (const r of result.agent_results) {
      setSteps((prev) => [
        ...prev,
        {
          agentName: r.agent_name,
          status: r.status,
          output: r.output,
          costUsd: r.cost_usd,
          latencyMs: r.latency_ms,
        },
      ]);
      await new Promise<void>((res) => setTimeout(res, 120));
    }

    setFinalOutput(result.final_output);
    setTotalCost(result.total_cost_usd);
    setState("done");
  } catch (err: unknown) {
    setErrorMsg(err instanceof Error ? err.message : "Request failed");
    setState("error");
  }
}
```

- [ ] **Step 3.2: Add `apiConfig` import**

At the top of `try-it-live.tsx`, the existing imports are:

```typescript
import { postRun, type AgentResult, type SwarmRunResult } from "@/lib/api";
```

Change to:

```typescript
import { postRun, type AgentResult, type SwarmRunResult } from "@/lib/api";
import { apiConfig } from "@/lib/config";
```

- [ ] **Step 3.3: Run TypeScript check**

```bash
cd .ui_landin_sample/minimal
npx tsc --noEmit
```

Expected: no errors

- [ ] **Step 3.4: Run lint**

```bash
npx next lint
```

Expected: no errors or warnings

- [ ] **Step 3.5: Commit**

```bash
git add .ui_landin_sample/minimal/components/try-it-live.tsx
git commit -m "feat(dashboard): real SSE streaming in TryItLive component"
```

---

## Task 4: Polish u2014 Remove `console.error` from `live-stats.tsx`

**Files:**

- Modify: `.ui_landin_sample/minimal/components/live-stats.tsx`

- [ ] **Step 4.1: Remove the `console.error` line**

Open `.ui_landin_sample/minimal/components/live-stats.tsx`.

Find the `.catch` block (around line 114u2013117):

```typescript
      .catch((err: unknown) => {
        console.error("[LiveStats] API fetch failed, using fallback", err);
      });
```

Replace with:

```typescript
      .catch(() => {
        // API unreachable u2014 FALLBACK_STATS already set as default state
      });
```

- [ ] **Step 4.2: TypeScript check**

```bash
cd .ui_landin_sample/minimal && npx tsc --noEmit
```

Expected: no errors

- [ ] **Step 4.3: Commit**

```bash
git add .ui_landin_sample/minimal/components/live-stats.tsx
git commit -m "fix(dashboard): remove console.error from LiveStats fallback"
```

---

## Task 5: Polish u2014 Fix `next.config.ts` env declaration

**Files:**

- Modify: `.ui_landin_sample/minimal/next.config.ts`

- [ ] **Step 5.1: Add env block**

Open `.ui_landin_sample/minimal/next.config.ts`. Replace the entire file with:

```typescript
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Disable source maps in production to prevent easy code inspection
  productionBrowserSourceMaps: false,
  // Remove console.log in production
  compiler: {
    removeConsole: process.env.NODE_ENV === "production",
  },
  // Expose API URL to the client bundle at build time
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL ?? "",
  },
};

export default nextConfig;
```

- [ ] **Step 5.2: TypeScript check**

```bash
cd .ui_landin_sample/minimal && npx tsc --noEmit
```

Expected: no errors

- [ ] **Step 5.3: Commit**

```bash
git add .ui_landin_sample/minimal/next.config.ts
git commit -m "chore(dashboard): declare NEXT_PUBLIC_API_URL in next.config.ts env block"
```

---

## Task 6: Polish u2014 Delete dead `stats.tsx` and add `.env.example`

**Files:**

- Delete: `.ui_landin_sample/minimal/components/stats.tsx`
- Create: `.ui_landin_sample/minimal/.env.example`
- Modify: `.ui_landin_sample/minimal/lib/config.ts`

- [ ] **Step 6.1: Delete `stats.tsx`**

```bash
rm .ui_landin_sample/minimal/components/stats.tsx
```

Verify `page.tsx` doesn't import it:

```bash
grep -r "from.*stats" .ui_landin_sample/minimal/app/page.tsx
```

Expected: no output (it imports `live-stats`, not `stats`)

- [ ] **Step 6.2: Create `.env.example`**

Create `.ui_landin_sample/minimal/.env.example` with content:

```env
# URL of the deployed FastAPI backend (Railway or local)
# Set this at build time when deploying to Railway / Vercel
NEXT_PUBLIC_API_URL=https://your-api.up.railway.app
```

- [ ] **Step 6.3: Add comment to `lib/config.ts`**

Open `.ui_landin_sample/minimal/lib/config.ts`. Find the `apiConfig` block (around line 167):

```typescript
export const apiConfig = {
  url: process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000",
} as const;
```

Replace with:

```typescript
// Set NEXT_PUBLIC_API_URL at build time to the Railway backend URL.
// Falls back to http://localhost:8000 for local dev.
export const apiConfig = {
  url: process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000",
} as const;
```

- [ ] **Step 6.4: TypeScript check**

```bash
cd .ui_landin_sample/minimal && npx tsc --noEmit
```

Expected: no errors

- [ ] **Step 6.5: Commit**

```bash
git add .ui_landin_sample/minimal/
git rm .ui_landin_sample/minimal/components/stats.tsx
git commit -m "chore(dashboard): remove dead stats.tsx, add .env.example, document apiConfig"
```

---

## Task 7: End-to-End Verification

This task has no code changes u2014 it validates the full flow works as described in the spec.

- [ ] **Step 7.1: Start the FastAPI server**

```bash
cd packages/techtide-swarm
pip install -e ".[dev]"
swarm serve
```

Expected: `Uvicorn running on http://0.0.0.0:8000`

- [ ] **Step 7.2: Verify the SSE endpoint with curl**

In a second terminal:

```bash
curl -N -X POST http://localhost:8000/api/swarm/run/stream \
  -H 'Content-Type: application/json' \
  -d '{"task": "Research the AI market", "budget_usd": 5.0}'
```

Expected output (lines appear with time gaps between them):

```text
event: start
data: {"pipeline_id": "...", "task": "Research the AI market"}

event: agent
data: {"agent_name": "...", "layer": "...", "status": "...", ...}

...

event: done
data: {"pipeline_id": "...", "total_cost_usd": ..., "final_output": "..."}

```

- [ ] **Step 7.3: Start the Next.js dev server**

In a third terminal:

```bash
cd .ui_landin_sample/minimal
NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev
```

Expected: `u25b2 Next.js 16 u2014 ready on http://localhost:3000`

- [ ] **Step 7.4: Browser test**

1. Open `http://localhost:3000`
2. Scroll to the "Try it live" section
3. Type `Research the AI market`
4. Click **Submit**
5. Agent rows must appear **one by one** with real gaps (not all at once)
6. After the last agent, the **Final output** block must appear
7. Scroll up u2014 **Live Numbers** section must show non-zero values
8. Scroll down u2014 **Recent Runs** table must show the run just submitted

- [ ] **Step 7.5: Run full frontend build**

```bash
cd .ui_landin_sample/minimal
npm run build
```

Expected: build completes with no TypeScript or ESLint errors

- [ ] **Step 7.6: Run full backend test suite**

```bash
cd packages/techtide-swarm
pytest tests/ -v
```

Expected: all tests `PASSED` (including the 2 new SSE tests from Task 2)

---

## Self-Review Notes

### Spec coverage check

| Spec requirement | Task |
|---|---|
| SSE endpoint `POST /api/swarm/run/stream` | Task 1 |
| SSE test for content-type + frame shape | Task 2 |
| `TryItLive` real SSE fetch reader | Task 3 |
| Fallback to `postRun()` if stream fails | Task 3 (`_runWithFallback`) |
| Remove `console.error` from `live-stats.tsx` | Task 4 |
| Add `env: { NEXT_PUBLIC_API_URL }` to `next.config.ts` | Task 5 |
| Delete dead `stats.tsx` | Task 6 |
| Create `.env.example` | Task 6 |
| Add comment to `apiConfig` in `config.ts` | Task 6 |
| End-to-end browser verification | Task 7 |

All spec requirements covered. No gaps.
