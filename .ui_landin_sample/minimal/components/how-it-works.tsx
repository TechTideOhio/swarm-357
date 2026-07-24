"use client";

import { howItWorksConfig } from "@/lib/config";
import { Download, Layers, Terminal } from "lucide-react";
import { motion, useInView } from "motion/react";
import Link from "next/link";
import type { ReactNode } from "react";
import { useRef } from "react";

const easeOut = [0.16, 1, 0.3, 1] as const;

const steps = [
  {
    icon: Download,
    title: "Install the package",
    description:
      "pip install techtide-swarm. The wheel ships the compact 357-agent roster and soul templates so swarm boot works out of the box.",
  },
  {
    icon: Layers,
    title: "Boot the roster",
    description:
      "swarm boot expands six business layers plus management meta-agents, with per-layer budgets and model preferences.",
  },
  {
    icon: Terminal,
    title: "Run a real task",
    description:
      "swarm run routes through the Conductor, executes role agents with tools, and reports cost and latency you can show FinOps.",
  },
];

function StepCard({
  step,
  index,
}: {
  step: (typeof steps)[0];
  index: number;
}): ReactNode {
  const ref = useRef<HTMLDivElement>(null);
  const isInView = useInView(ref, { once: true, amount: 0.5 });
  const Icon = step.icon;

  return (
    <motion.div
      ref={ref}
      className="bg-muted min-h-70 rounded-2xl p-6 md:p-8 flex flex-col"
      initial={{ opacity: 0, y: 30 }}
      animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 30 }}
      transition={{ duration: 0.6, delay: index * 0.1, ease: easeOut }}
    >
      <div className="text-foreground mb-6">
        <Icon className="h-12 w-12" strokeWidth={1} />
      </div>
      <h3 className="mb-3 text-xl font-medium tracking-tight md:text-2xl mt-auto">
        {step.title}
      </h3>
      <p className="text-muted-foreground text-base leading-relaxed">
        {step.description}
      </p>
    </motion.div>
  );
}

export function HowItWorks(): ReactNode {
  const headerRef = useRef<HTMLDivElement>(null);
  const isHeaderInView = useInView(headerRef, { once: true, amount: 0.5 });

  return (
    <section id="how-it-works" className="bg-background px-6 py-16 md:py-32">
      <div className="mx-auto max-w-6xl">
        <motion.div
          ref={headerRef}
          className="mb-8 text-center md:mb-16"
          initial={{ opacity: 0, y: 20 }}
          animate={isHeaderInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
          transition={{ duration: 0.6, ease: easeOut }}
        >
          <h2 className="text-3xl font-medium tracking-tight md:text-4xl lg:text-5xl">
            {howItWorksConfig.title}
          </h2>
          <p className="text-muted-foreground mx-auto mt-4 max-w-2xl text-base md:text-lg">
            {howItWorksConfig.description}
          </p>
          <Link
            href={howItWorksConfig.cta.href}
            className="text-foreground mt-6 inline-block text-sm font-medium underline underline-offset-4"
          >
            {howItWorksConfig.cta.text}
          </Link>
        </motion.div>

        <div className="grid grid-cols-1 gap-4 md:grid-cols-3 md:gap-6">
          {steps.map((step, index) => (
            <StepCard key={step.title} step={step} index={index} />
          ))}
        </div>
      </div>
    </section>
  );
}
