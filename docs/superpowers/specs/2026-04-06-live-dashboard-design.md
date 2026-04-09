# Swarm 357 Live Dashboard — Design Spec

**Date:** 2026-04-06  
**Status:** Draft — awaiting user review  
**Scope:** `.ui_landin_sample/minimal/` landing page + FastAPI server SSE endpoint

---

## Context

The landing page at `.ui_landin_sample/minimal/` shipped with all the right component shells
(`try-it-live.tsx`, `agent-roster.tsx`, `live-stats.tsx`, `recent-runs.tsx`) already wired to the
FastAPI backend from Prompt 3. The problem: the "Try it live" demo uses a single blocking POST +
artificial 120ms stagger delays to simulate streaming. This reads as fake in a README GIF. The goal
is Option C: real SSE streaming from the backend + a polish pass to fix small gaps.

**Outcome:** Visit the deployed landing page, type "Research the AI market", and watch agent steps
appear one by one as each agent actually completes — real streaming, real cost, real latency numbers.
That sequence is the README GIF.

---

## 1. FastAPI SSE Endpoint

**File:** `packages/techtide-swarm/src/techtide_swarm/server.py`

Add a new route: `POST /api/swarm/run/stream`

Request body: identical to `/api/swarm/run` — `{task: str, budget_usd: float = 5.0, layer?: str}`

Response: `Content-Type: text/event-stream` using FastAPI's `StreamingResponse` + a generator that:

1. Emits `event: start` with `{pipeline_id, task}` immediately
2. Iterates through each agent the swarm would run
3. For each agent: runs it, then emits `event: agent` with `{agent_name, layer, status, output, cost_usd, latency_ms}`
4. Emits `event: done` with `{pipeline_id, total_cost_usd, final_output}` at the end
5. On error: emits `event: error` with `{message}` and closes the stream

Each SSE frame follows standard format:

```text
event: agent
data: {"agent_name": "...", "status": "success", ...}

```

Implementation pattern — identical to the existing `/api/agent/run` endpoint:

1. Call `_get_roster()` to get all agent configs (same closure the other routes use)
2. Filter to `req.layer` agents if provided; otherwise use all agents in roster order
3. For each agent config, build `AgentConfig` + `Agent(config)`, call `await agent.run(task)`, then `yield` the SSE frame
4. After all agents, yield the `done` frame

This avoids modifying `Swarm.execute()` — it directly composes the same primitives the `/api/agent/run` route already uses.

**CORS note:** `StreamingResponse` inherits the existing CORS middleware — no extra config needed.

---

## 2. TryItLive Component — Real SSE Client

**File:** `.ui_landin_sample/minimal/components/try-it-live.tsx`

Replace the `postRun()` call with a native `fetch` + streaming `ReadableStream` reader
(not `EventSource`, because `EventSource` only supports GET):

```text
fetch(POST /api/swarm/run/stream, body)
  → response.body.getReader()
  → read chunks, split on double-newline SSE frames
  → parse event type + JSON data
  → dispatch to state
```

State machine stays identical (`idle → running → done | error`). The only difference: agent steps
now appear one by one as the server yields them, not after the full response arrives.

The `AgentStepRow` component, expand/collapse output, status dots, cost/latency display — all
unchanged. The final output block and total cost — all unchanged.

**Fallback:** if the SSE fetch fails (network error, 404 — e.g. backend not running locally),
fall back to `postRun()` on the existing `/api/swarm/run` endpoint with the stagger. Show a dim
`(live streaming unavailable)` label.

---

## 3. Polish Pass

### 3a. Remove `console.error` from `live-stats.tsx`

**File:** `.ui_landin_sample/minimal/components/live-stats.tsx:116`

Line: `console.error("[LiveStats] API fetch failed, using fallback", err);`

Fix: Remove the log. The component already silently uses `FALLBACK_STATS` — the error is
recoverable and the user sees no broken UI.

### 3b. Declare `NEXT_PUBLIC_API_URL` in `next.config.ts`

**File:** `.ui_landin_sample/minimal/next.config.ts`

Add `env: { NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL ?? '' }` to the config object.
This ensures Next.js bundles the env var into the client-side build at deploy time on platforms
(Railway, Vercel) that set it at build time.

### 3c. Remove dead `stats.tsx`

**File:** `.ui_landin_sample/minimal/components/stats.tsx`

`page.tsx` imports `LiveStats` not `Stats`. The file is dead code. Delete it.

### 3d. Add `.env.example` for the landing page

**File:** `.ui_landin_sample/minimal/.env.example` (new file)

Content:

```env
# URL of the deployed FastAPI backend (Railway or local)
NEXT_PUBLIC_API_URL=https://your-api.up.railway.app
```

This is the deploy instruction for the README GIF — whoever deploys must set this.

### 3e. Update `apiConfig` Railway URL comment in `config.ts`

**File:** `.ui_landin_sample/minimal/lib/config.ts`

Add a comment on `apiConfig` explaining the env var:
`// Set NEXT_PUBLIC_API_URL at build time to the Railway backend URL`

---

## 4. What Is NOT Changing

- Design system (Tailwind, CSS variables, motion, dark mode) — untouched
- `hero.tsx` structure — untouched (TryItLive is already embedded)
- `agent-roster.tsx` — already live and correct
- `recent-runs.tsx` — already live and correct
- `lib/api.ts` — all existing functions remain; `postRun()` kept as SSE fallback
- `lib/config.ts` — only adding a comment, not restructuring
- All navigation links — already point to real GitHub URLs
- `siteConfig`, pricing, FAQ, footer content — untouched

---

## 5. Files Changed

| File | Change |
|------|--------|
| `packages/techtide-swarm/src/techtide_swarm/server.py` | Add `POST /api/swarm/run/stream` SSE route |
| `.ui_landin_sample/minimal/components/try-it-live.tsx` | Replace fake stagger with real SSE fetch reader |
| `.ui_landin_sample/minimal/components/live-stats.tsx` | Remove `console.error` |
| `.ui_landin_sample/minimal/next.config.ts` | Add `env: { NEXT_PUBLIC_API_URL }` |
| `.ui_landin_sample/minimal/components/stats.tsx` | Delete (dead code) |
| `.ui_landin_sample/minimal/.env.example` | Create with `NEXT_PUBLIC_API_URL` |
| `.ui_landin_sample/minimal/lib/config.ts` | Add comment on `apiConfig` |

---

## 6. Verification

**Local test:**

1. `cd packages/techtide-swarm && pip install -e ".[dev]"` then `swarm serve` (starts FastAPI on :8000)
2. `cd .ui_landin_sample/minimal && NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev`
3. Visit `http://localhost:3000`, type "Research the AI market", hit Submit
4. Agent steps should appear one by one as the server streams them (not all at once after a pause)
5. Verify `recent-runs.tsx` shows the run after it completes
6. Verify `live-stats.tsx` updates total cost
7. `npm run typecheck` — no TypeScript errors
8. `npm run lint` — no ESLint errors

**SSE verification (curl):**

```bash
curl -N -X POST http://localhost:8000/api/swarm/run/stream \
  -H 'Content-Type: application/json' \
  -d '{"task": "Research the AI market", "budget_usd": 5.0}'
```

Expect: `event: start`, then `event: agent` lines appearing with gaps, then `event: done`.
