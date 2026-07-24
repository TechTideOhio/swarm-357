"use client";

import { motion } from "motion/react";
import { useEffect, useState, type ReactNode } from "react";
import { getAgents, type Agent } from "@/lib/api";

const easeOut = [0.16, 1, 0.3, 1] as const;

const LAYER_ORDER = [
  "management",
  "sales",
  "support",
  "marketing",
  "seo",
  "research",
  "operations",
];

const LAYER_COLORS: Record<string, string> = {
  management: "bg-purple-500/15 text-purple-300",
  sales: "bg-blue-500/15 text-blue-300",
  support: "bg-green-500/15 text-green-300",
  marketing: "bg-pink-500/15 text-pink-300",
  seo: "bg-orange-500/15 text-orange-300",
  research: "bg-cyan-500/15 text-cyan-300",
  operations: "bg-yellow-500/15 text-yellow-300",
};

function AgentCard({ agent }: { agent: Agent }): ReactNode {
  const colorClass =
    LAYER_COLORS[agent.layer] ?? "bg-foreground/10 text-foreground";
  return (
    <div className="bg-muted hover:bg-muted/80 flex flex-col gap-2 rounded-xl p-4 transition-colors duration-200">
      <div className="flex items-start justify-between gap-2">
        <span className="text-foreground truncate text-sm font-medium">
          {agent.name}
        </span>
        <span
          className={`shrink-0 rounded-full px-2 py-0.5 text-xs font-medium ${colorClass}`}
        >
          {agent.model}
        </span>
      </div>
      <p className="text-muted-foreground text-xs">{agent.role}</p>
      <p className="text-muted-foreground text-xs">
        Budget: ${agent.budget_usd.toFixed(2)}/run
      </p>
    </div>
  );
}

export function AgentRoster(): ReactNode {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [search, setSearch] = useState("");
  const [activeLayer, setActiveLayer] = useState<string>("all");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    getAgents()
      .then((res) => setAgents(res.agents))
      .catch((e: unknown) =>
        setError(e instanceof Error ? e.message : "Failed to load agents")
      )
      .finally(() => setLoading(false));
  }, []);

  const layers = [
    "all",
    ...LAYER_ORDER.filter((l) => agents.some((a) => a.layer === l)),
  ];

  const filtered = agents.filter((a) => {
    const matchLayer = activeLayer === "all" || a.layer === activeLayer;
    const matchSearch =
      !search ||
      a.name.toLowerCase().includes(search.toLowerCase()) ||
      a.role.toLowerCase().includes(search.toLowerCase());
    return matchLayer && matchSearch;
  });

  return (
    <section className="bg-background px-6 py-16 md:py-32">
      <div className="mx-auto max-w-6xl">
        <motion.div
          className="mb-10 text-center"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, ease: easeOut }}
        >
          <h2 className="mb-3 text-3xl font-medium tracking-tight md:text-4xl lg:text-5xl">
            {loading ? "Loading agents\u2026" : `${agents.length} Live Agents`}
          </h2>
          <p className="text-muted-foreground text-base">
            Six business layers — searchable, filterable, real.
          </p>
        </motion.div>

        {error && (
          <p className="text-center text-sm text-red-400 mb-6">{error}</p>
        )}

        {!loading && !error && (
          <>
            {/* Controls */}
            <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
              <label htmlFor="agent-search" className="sr-only">Search agents or roles</label>
              <input
                id="agent-search"
                type="text"
                placeholder="Search agents or roles…"
                aria-label="Search agents or roles"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="bg-muted text-foreground placeholder:text-muted-foreground w-full rounded-md px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-accent sm:w-72"
              />
              <div className="flex flex-wrap gap-2">
                {layers.map((l) => (
                  <button
                    key={l}
                    aria-pressed={activeLayer === l}
                    onClick={() => setActiveLayer(l)}
                    className={`rounded-full px-3 py-1 text-xs font-medium transition-colors duration-200 ${
                      activeLayer === l
                        ? "bg-accent text-black"
                        : "bg-muted text-muted-foreground hover:bg-muted/80"
                    }`}
                  >
                    {l === "all" ? `All (${agents.length})` : l}
                  </button>
                ))}
              </div>
            </div>

            {/* Grid */}
            <motion.div
              className="grid grid-cols-1 gap-3 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.4 }}
            >
              {filtered.map((agent) => (
                <AgentCard key={agent.name} agent={agent} />
              ))}
              {filtered.length === 0 && (
                <p className="text-muted-foreground col-span-full text-center text-sm py-8">
                  No agents match your search.
                </p>
              )}
            </motion.div>
          </>
        )}

        {loading && (
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
            {Array.from({ length: 12 }).map((_, i) => (
              <div
                key={i}
                className="bg-muted h-24 animate-pulse rounded-xl"
              />
            ))}
          </div>
        )}
      </div>
    </section>
  );
}
