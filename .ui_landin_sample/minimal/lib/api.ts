/**
 * Typed API client for the TechTide Swarm 357 FastAPI backend.
 * Reads NEXT_PUBLIC_API_URL; falls back to http://localhost:8000 for local dev.
 */

import { apiConfig } from "@/lib/config";

const BASE_URL = apiConfig.url;

// -- Types ------------------------------------------------------------------

export interface Agent {
  name: string;
  layer: string;
  role: string;
  model: string;
  budget_usd: number;
  tools: string[];
}

export interface AgentsResponse {
  agents: Agent[];
  total: number;
}

export interface LayerStats {
  calls: number;
  cost: number;
  latency: number;
}

export interface SwarmStatus {
  layers: Record<string, LayerStats>;
  total_cost_usd: number;
  roster_size: number;
}

export interface SwarmCost {
  total_cost_usd: number;
  per_layer_usd: Record<string, number>;
}

export interface AgentResult {
  output: string;
  cost_usd: number;
  latency_ms: number;
  status: "success" | "error" | "skipped";
  agent_name: string;
  error: string | null;
}

export interface SwarmRunResult {
  pipeline_id: string;
  status: "ok" | "error" | "stub";
  total_cost_usd: number;
  final_output: string;
  agent_results: AgentResult[];
  error?: string;
}

export interface RunEvent {
  type: string;
  pipeline_id?: string;
  task?: string;
  total_cost_usd?: number;
  agents_used?: string[];
  latency_ms?: number;
  status?: string;
  agent_name?: string;
  layer?: string;
  cost_usd?: number;
}

export interface RunsResponse {
  runs: RunEvent[];
  total: number;
}

// -- Fetch helpers ----------------------------------------------------------

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(init?.headers as Record<string, string> | undefined),
  };
  const res = await fetch(`${BASE_URL}${path}`, {
    ...init,
    headers,
  });
  if (!res.ok) {
    let detail = `${res.status}`;
    try {
      const body = (await res.json()) as { detail?: string };
      if (body.detail) detail = `${res.status}: ${body.detail}`;
    } catch {
      /* ignore */
    }
    throw new Error(`API ${path} returned ${detail}`);
  }
  return res.json() as Promise<T>;
}

// -- Public API -------------------------------------------------------------

export function getAgents(): Promise<AgentsResponse> {
  return apiFetch<AgentsResponse>("/api/swarm/agents");
}

export function getStatus(): Promise<SwarmStatus> {
  return apiFetch<SwarmStatus>("/api/swarm/status");
}

export function getCost(): Promise<SwarmCost> {
  return apiFetch<SwarmCost>("/api/swarm/cost");
}

export function getRuns(limit = 10): Promise<RunsResponse> {
  return apiFetch<RunsResponse>(`/api/swarm/runs?limit=${limit}`);
}

/** Public health JSON — safe to link from the landing page. */
export function getHealth(): Promise<{
  status: string;
  version: string;
  agents: number;
  api_key_set: boolean;
}> {
  return apiFetch("/api/health");
}

/**
 * Runs the swarm pipeline. When the API has SWARM_API_KEY set, pass the same
 * value from NEXT_PUBLIC_SWARM_WRITE_KEY so the browser can send X-SWARM-API-KEY.
 */
export function postRun(
  task: string,
  budgetUsd = 5.0
): Promise<SwarmRunResult> {
  const writeKey = process.env.NEXT_PUBLIC_SWARM_WRITE_KEY ?? "";
  const headers: Record<string, string> = {};
  if (writeKey) {
    headers["X-SWARM-API-KEY"] = writeKey;
  }
  return apiFetch<SwarmRunResult>("/api/swarm/run", {
    method: "POST",
    body: JSON.stringify({ task, budget_usd: budgetUsd }),
    headers,
  });
}
