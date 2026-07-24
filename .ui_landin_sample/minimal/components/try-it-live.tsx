"use client";

import { motion } from "motion/react";
import { useState, type ReactNode } from "react";
import { postRun, type AgentResult, type SwarmRunResult } from "@/lib/api";

const easeOut = [0.16, 1, 0.3, 1] as const;

type DemoState = "idle" | "running" | "done" | "error";

interface RunStep {
  agentName: string;
  status: AgentResult["status"];
  output: string;
  costUsd: number;
  latencyMs: number;
}

function StatusDot({ status }: { status: AgentResult["status"] }): ReactNode {
  const colors: Record<AgentResult["status"], string> = {
    success: "bg-green-500",
    error: "bg-red-500",
    skipped: "bg-yellow-500",
  };
  return (
    <span
      className={`inline-block h-2 w-2 rounded-full ${colors[status]}`}
    />
  );
}

function AgentStepRow({ step }: { step: RunStep }): ReactNode {
  const [expanded, setExpanded] = useState(false);
  return (
    <motion.div
      className="border-border/40 border-b py-3 last:border-0"
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.3, ease: "easeOut" }}
    >
      <button
        className="flex w-full items-center justify-between gap-3 text-left"
        onClick={() => setExpanded((p) => !p)}
      >
        <div className="flex items-center gap-3">
          <StatusDot status={step.status} />
          <span className="text-sm font-medium">{step.agentName}</span>
          <span className="text-muted-foreground text-xs">
            {step.latencyMs}ms \u00b7 ${step.costUsd.toFixed(4)}
          </span>
        </div>
        <span className="text-muted-foreground text-xs">
          {expanded ? "\u25b2" : "\u25bc"}
        </span>
      </button>
      {expanded && step.output && (
        <p className="text-muted-foreground mt-2 pl-5 text-xs leading-relaxed">
          {step.output.slice(0, 400)}
          {step.output.length > 400 ? "\u2026" : ""}
        </p>
      )}
    </motion.div>
  );
}

export function TryItLive(): ReactNode {
  const [task, setTask] = useState("");
  const [state, setState] = useState<DemoState>("idle");
  const [steps, setSteps] = useState<RunStep[]>([]);
  const [finalOutput, setFinalOutput] = useState("");
  const [totalCost, setTotalCost] = useState(0);
  const [errorMsg, setErrorMsg] = useState("");

  async function handleSubmit(e: React.FormEvent): Promise<void> {
    e.preventDefault();
    if (!task.trim() || state === "running") return;

    setState("running");
    setSteps([]);
    setFinalOutput("");
    setTotalCost(0);
    setErrorMsg("");

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

  return (
    <motion.div
      className="relative z-10 mx-auto w-full max-w-2xl px-6 pb-24"
      initial={{ opacity: 0, y: 40 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, amount: 0.3 }}
      transition={{ duration: 0.8, ease: easeOut }}
    >
      <h2 className="mb-4 text-center text-3xl font-medium tracking-tight md:text-4xl">
        Try it live
      </h2>
      <p className="text-muted-foreground mb-6 text-center text-base">
        Type a business task and watch agents route and execute it. If the API has{" "}
        <code className="text-foreground/90">SWARM_API_KEY</code> set, add{" "}
        <code className="text-foreground/90">NEXT_PUBLIC_SWARM_WRITE_KEY</code> in the
        Next.js env (same value) so the browser can send{" "}
        <code className="text-foreground/90">X-SWARM-API-KEY</code>.
      </p>

      <form onSubmit={handleSubmit} className="mb-6 flex gap-3">
        <input
          type="text"
          value={task}
          onChange={(e) => setTask(e.target.value)}
          placeholder="e.g. Research the AI market"
          disabled={state === "running"}
          className="bg-muted text-foreground placeholder:text-muted-foreground flex-1 rounded-md px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-accent disabled:opacity-50"
        />
        <button
          type="submit"
          disabled={!task.trim() || state === "running"}
          className="bg-accent rounded-md px-5 py-3 text-sm font-medium text-black transition-opacity disabled:opacity-40"
        >
          {state === "running" ? "Running\u2026" : "Submit"}
        </button>
      </form>

      {steps.length > 0 && (
        <motion.div
          className="bg-muted rounded-xl p-4"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <p className="text-muted-foreground mb-3 text-xs font-medium uppercase tracking-wider">
            Agent pipeline
          </p>
          {steps.map((s, i) => (
            <AgentStepRow key={`${s.agentName}-${i}`} step={s} />
          ))}
          {state === "running" && (
            <p className="text-muted-foreground mt-3 animate-pulse text-xs">
              Running\u2026
            </p>
          )}
        </motion.div>
      )}

      {state === "done" && finalOutput && (
        <motion.div
          className="bg-muted mt-4 rounded-xl p-4"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          <p className="text-muted-foreground mb-2 text-xs font-medium uppercase tracking-wider">
            Final output \u00b7 ${totalCost.toFixed(4)} total
          </p>
          <p className="text-foreground text-sm leading-relaxed">
            {finalOutput.slice(0, 1000)}
            {finalOutput.length > 1000 ? "\u2026" : ""}
          </p>
        </motion.div>
      )}

      {state === "error" && (
        <motion.div
          className="mt-4 rounded-xl bg-red-950/40 p-4"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          <p className="text-sm text-red-400">{errorMsg}</p>
        </motion.div>
      )}
    </motion.div>
  );
}
