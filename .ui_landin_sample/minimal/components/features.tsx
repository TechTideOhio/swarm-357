"use client";

import { ChevronRightIcon } from "lucide-react";
import { motion } from "motion/react";
import type { ReactNode } from "react";

const easeOut = [0.16, 1, 0.3, 1] as const;

interface Feature {
  number: string;
  title: string;
  description: string;
}

const features: Feature[] = [
  {
    number: "01",
    title: "Layered orchestration",
    description:
      "Six business layers -- Sales, Support, Marketing, SEO, Research, Operations -- plus Management meta-agents. Pre-defined roles, not blank-slate prompts.",
  },
  {
    number: "02",
    title: "Durable .mv2 memory",
    description:
      "Replace flat-file context with portable Memvid capsules. WAL-based crash safety, full-text and vector search, integrity verification -- no database server required.",
  },
  {
    number: "03",
    title: "Honest cost surfaces",
    description:
      "Per-agent budget caps enforced at runtime, per-layer cost controllers, and a swarm cost CLI. Know what you spend before production reviewers ask.",
  },
];

function FeatureCard({
  feature,
  index,
}: {
  feature: Feature;
  index: number;
}): ReactNode {
  return (
    <motion.div
      className="bg-muted grid grid-cols-1 gap-2 overflow-hidden rounded-2xl p-2 md:grid-cols-2 transition-colors duration-300 hover:bg-muted/80"
      initial={{ opacity: 0, y: 30 }}
      whileInView={{ opacity: 1, y: 0 }}
      whileHover={{ scale: 1.01 }}
      viewport={{ once: true, amount: 0.3 }}
      transition={{
        duration: 0.6,
        delay: index * 0.1,
        ease: easeOut,
      }}
    >
      <div className="px-4 py-28">
        <span className="text-muted-foreground bg-foreground/5 mb-4 block w-fit rounded-md px-2 py-1 text-sm font-medium transition-colors duration-300 group-hover:bg-foreground/10">
          {feature.number}
        </span>
        <h3 className="mb-4 text-2xl font-medium tracking-tight md:text-3xl">
          {feature.title}
        </h3>
        <p className="text-muted-foreground max-w-md text-sm leading-relaxed">
          {feature.description}
        </p>
      </div>
    </motion.div>
  );
}

export function Features(): ReactNode {
  return (
    <section className="bg-background px-6 py-16 md:py-32">
      <div className="mx-auto flex max-w-6xl flex-col gap-12 lg:flex-row lg:items-start lg:gap-16">
        {/* Sticky left column */}
        <motion.div
          className="lg:sticky lg:top-60 lg:w-96 lg:shrink-0"
          initial={{ opacity: 0, x: -30 }}
          whileInView={{ opacity: 1, x: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, ease: easeOut }}
        >
          <h2 className="mb-4 text-2xl font-medium tracking-tight md:mb-6 md:text-3xl lg:text-4xl">
            Built for Claude Code
          </h2>
          <p className="text-muted-foreground mb-6 max-w-sm text-base md:mb-8 md:text-lg">
            One repo ties a Next.js surface, a Python agent package, and the
            Memvid Rust core — so contributors improve memory, hooks, or UI
            without three separate releases.
          </p>
          <a
            href="#"
            className="bg-foreground group inline-flex w-full items-center justify-center gap-3 rounded-md py-3 pr-3 pl-5 font-medium text-background transition-all duration-500 ease-out hover:rounded-[50px] sm:w-auto"
          >
            <span>View on GitHub</span>
            <span className="bg-background text-foreground flex h-10 w-10 items-center justify-center rounded-full transition-all duration-300 group-hover:scale-110">
              <ChevronRightIcon className="relative left-px h-4 w-4" />
            </span>
          </a>
        </motion.div>

        {/* Scrolling right column */}
        <div className="flex min-w-0 flex-1 flex-col gap-6 md:gap-32">
          {features.map((feature, index) => (
            <FeatureCard key={feature.number} feature={feature} index={index} />
          ))}
        </div>
      </div>
    </section>
  );
}
