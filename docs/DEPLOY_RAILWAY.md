# Deploy Swarm 357 on Railway

## Monorepo (TechTide root on GitHub)

1. **New service** → connect repo → **Root Directory**: `Apps/swarm357`.
2. **Builder**: Dockerfile (see [railway.toml](../railway.toml)).
3. **Variables** (minimum):
   - `ANTHROPIC_API_KEY` — for live agents (omit only if you want stub responses).
   - `SWARM_API_KEY` — long random string; required for securing POST routes in production.
   - `PORT` — Railway sets automatically; [railway.toml](../railway.toml) uses `$PORT` in `startCommand`.

Optional:

- `ALLOWED_ORIGINS` — comma-separated origins for the Next.js marketing site.
- `SUPABASE_URL` / `SUPABASE_SERVICE_KEY` — persistence; run [database/migrations/001_initial.sql](../database/migrations/001_initial.sql) in Supabase SQL first.
- `SWARM_MAX_RUN_BUDGET_USD` — hard cap for JSON `budget_usd` (default `500`).
- `SWARM_RATE_LIMIT_PER_MINUTE` — per-IP limit (default `120`; set `0` to disable).

## Custom domain

1. Railway → service → **Settings** → **Networking** → generate domain or attach custom domain.
2. Add the same origin to `ALLOWED_ORIGINS`.
3. Redeploy so CORS includes the new host.

## Smoke checks

Public production URLs (Railway project `swarm-357`):

| Surface | Service | Public URL |
|--------|---------|------------|
| Frontend | `frontend` | https://swarm357fe.up.railway.app |
| Backend | `backend` | https://swarm357be.up.railway.app |

```bash
curl -sSf "https://swarm357be.up.railway.app/api/health"
# Expect: "status":"ok","agents":357,...
```

See [VERIFY.md](VERIFY.md) for the full scorecard.

## Landing (Next.js) on Railway (optional second service)

- Deploy from `TechTideOhio/swarm-357-site` (Railway root = repo root).
- Build: `bun install && bun run build` (or `npm ci && npm run build`).
- Env: `NEXT_PUBLIC_API_URL=https://swarm357be.up.railway.app`
- Backend CORS: `ALLOWED_ORIGINS=https://swarm357fe.up.railway.app` (plus any custom domains).
- If the API uses `SWARM_API_KEY`, set `NEXT_PUBLIC_SWARM_WRITE_KEY` to the **same** value only if you want the “Try it live” hero form to call POST `/api/swarm/run` from the browser (prefer restricting demo POSTs or using a server-side proxy in production).

## Go-live checklist

1. **Root directory** is `Apps/swarm357` when the GitHub repo is the TechTide monorepo (not `.` at monorepo root unless the service only contains swarm357).
2. **Builder** = Dockerfile; confirm [railway.toml](../railway.toml) `startCommand` uses `$PORT` (Railway injects it).
3. Set **`ANTHROPIC_API_KEY`**, **`SWARM_API_KEY`**, and optional **`ALLOWED_ORIGINS`** for your marketing origin.
4. Run **`database/migrations/001_initial.sql`** in Supabase before setting `SUPABASE_*` env vars (see [DATA_PLANE.md](DATA_PLANE.md)).
5. Deploy, then **`curl /api/health`** — expect `"agents":357` and `"status":"ok"`.

## Troubleshooting

| Symptom | Likely cause | Fix |
|--------|----------------|-----|
| Build: `package.json` not found / Railpack errors | Wrong **Root Directory** | Set Root Directory to `Apps/swarm357` and builder to Dockerfile. |
| Service starts then 502 / connection refused | `PORT` not bound | Keep `uvicorn ... --port $PORT` in Railway start command; do not hardcode `8000` in production. |
| `/api/health` shows `agents: 0` | Config path missing in image | Ensure [Dockerfile](../Dockerfile) copies `config/` and `templates/`; or set `SWARM_CONFIG_PATH`. |
| POST returns 401 | `SWARM_API_KEY` set | Send header `X-SWARM-API-KEY` with the same secret. |
| POST returns 429 | Rate limit | Raise `SWARM_RATE_LIMIT_PER_MINUTE` or set to `0` for internal testing only. |
| CORS blocked from browser | Origin not allowed | Add site URL to `ALLOWED_ORIGINS` and redeploy. |
