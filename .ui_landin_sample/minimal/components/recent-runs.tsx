"use client";

import { motion, useInView } from "motion/react";
import { useEffect, useRef, useState, type ReactNode } from "react";
import { getRuns, type RunEvent } from "@/lib/api";

const easeOut = [0.16, 1, 0.3, 1] as const;

function RunRow({ run, index }: { run: RunEvent; index: number }): ReactNode {
  const ref = useRef<HTMLDivElement>(null);
  const isInView = useInView(ref, { once: true, amount: 0.3 });
  const statusColor =
    run.status === "ok" || run.status === "success"
      ? "text-green-400"
      : run.status === "error"
        ? "text-red-400"
        : "text-yellow-400";

  return (
    <motion.div
      ref={ref}
      className="border-border/40 grid grid-cols-[1fr_auto_auto_auto] items-center gap-4 border-b py-4 last:border-0"
      initial={{ opacity: 0, y: 10 }}
      animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 10 }}
      transition={{ duration: 0.4, delay: index * 0.05, ease: easeOut }}
    >
      <div className="min-w-0">
        <p className="text-foreground truncate text-sm font-medium">
          {run.task ?? run.pipeline_id ?? "\—"}
        </p>
        <p className="text-muted-foreground text-xs">
          {Array.isArray(run.agents_used) && run.agents_used.length > 0
            ? `${run.agents_used.length} agents`
            : run.agent_name ?? "\—"}
        </p>
      </div>
      <span className={`text-xs font-medium ${statusColor}`}>
        {run.status ?? "\—"}
      </span>
      <span className="text-muted-foreground text-xs">
        {run.latency_ms != null ? `${run.latency_ms}ms` : "\—"}
      </span>
      <span className="text-muted-foreground text-xs">
        {run.total_cost_usd != null || run.cost_usd != null
          ? `$${((run.total_cost_usd ?? run.cost_usd) as number).toFixed(4)}`
          : "\—"}
      </span>
    </motion.div>
  );
}

export function RecentRuns(): ReactNode {
  const [runs, setRuns] = useState<RunEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [fetchError, setFetchError] = useState(false);

  useEffect(() => {
    getRuns(10)
      .then((res) => setRuns(res.runs))
      .catch(() => setFetchError(true))
      .finally(() => setLoading(false));
  }, []);

  const headerRef = useRef<HTMLDivElement>(null);
  const isHeaderInView = useInView(headerRef, { once: true, amount: 0.5 });

  return (
    <section className="bg-background px-6 py-16 md:py-32">
      <div className="mx-auto max-w-4xl">
        <motion.div
          ref={headerRef}
          className="mb-10 text-center"
          initial={{ opacity: 0, y: 20 }}
          animate={isHeaderInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
          transition={{ duration: 0.6, ease: easeOut }}
        >
          <h2 className="text-3xl font-medium tracking-tight md:text-4xl lg:text-5xl">
            Recent Runs
          </h2>
          <p className="text-muted-foreground mt-3 text-base">
            Last 10 swarm executions logged in real time.
          </p>
        </motion.div>

        {loading && (
          <div className="space-y-3">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="bg-muted h-14 animate-pulse rounded-xl" />
            ))}
          </div>
        )}

        {!loading && fetchError && (
          <p className="text-muted-foreground text-center text-sm py-12">
            Could not load run history. Check that the backend is reachable.
          </p>
        )}

        {!loading && !fetchError && runs.length === 0 && (
          <p className="text-muted-foreground text-center text-sm py-12">
            No runs yet. Use the demo above to create your first run.
          </p>
        )}

        {!loading && !fetchError && runs.length > 0 && (
          <div className="bg-muted rounded-2xl px-4">
            <div className="border-border/40 grid grid-cols-[1fr_auto_auto_auto] gap-4 border-b py-3 text-xs font-medium uppercase tracking-wider text-muted-foreground">
              <span>Task</span>
              <span>Status</span>
              <span>Latency</span>
              <span>Cost</span>
            </div>
            {runs.map((run, index) => (
              <RunRow
                key={run.pipeline_id ?? index}
                run={run}
                index={index}
              />
            ))}
          </div>
        )}
      </div>
    </section>
  );
}
