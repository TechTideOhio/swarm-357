"use client";

import { Check, ChevronRightIcon } from "lucide-react";
import { motion } from "motion/react";
import type { ReactNode } from "react";

const easeOut = [0.16, 1, 0.3, 1] as const;

interface Plan {
  name: string;
  tagline: string;
  price: string;
  period: string;
  features: string[];
  highlighted?: boolean;
}

const plans: Plan[] = [
  {
    name: "Open Source",
    tagline: "Full swarm package, bring your own keys",
    price: "$0",
    period: "forever",
    features: [
      "357 agent templates",
      "swarm CLI (init, demo, status, cost, run)",
      ".swarm/ flat-file memory",
      "BashSecurityGate (13 rules)",
      "CostController and budget caps",
      "Opik trace hooks",
      "Apache-2.0 license",
    ],
  },
  {
    name: "Enterprise Controls",
    tagline: "Durable memory + verification + support",
    price: "Custom",
    period: "year",
    highlighted: true,
    features: [
      "Everything in Open Source",
      "Memvid .mv2 durable memory",
      "Integrity verification (memvid verify --deep)",
      "Encrypted capsules (.mv2e) path",
      "Migration tooling (swarm migrate)",
      "Priority issue triage",
      "Architecture review session",
    ],
  },
];

function PlanCard({ plan }: { plan: Plan }): ReactNode {
  return (
    <motion.div
      className={`rounded-2xl p-6 md:p-8 ${
        plan.highlighted
          ? "border-accent bg-background border-2 transition-[border-color,box-shadow] duration-300 hover:border-accent/80 hover:shadow-lg hover:shadow-accent/10"
          : "bg-background transition-[background-color] duration-300 hover:bg-background/80"
      }`}
      initial={{ opacity: 0, y: 30 }}
      whileInView={{ opacity: 1, y: 0 }}
      whileHover={{ y: -4 }}
      viewport={{ once: true, amount: 0.3 }}
      transition={{
        opacity: { duration: 0.6, ease: easeOut },
        y: { duration: 0.3, ease: easeOut },
      }}
    >
      <div className="mb-6">
        <h3 className="text-lg font-medium">{plan.name}</h3>
        <p className="text-muted-foreground text-sm">{plan.tagline}</p>
      </div>

      <div className="mb-8 flex items-baseline gap-1">
        <span className="text-4xl font-medium tracking-tight md:text-5xl">
          {plan.price}
        </span>
        <span className="text-muted-foreground text-sm">/ {plan.period}</span>
      </div>

      <ul className="space-y-3">
        {plan.features.map((feature) => (
          <li key={feature} className="flex items-start gap-3 text-sm">
            <Check className="text-foreground mt-0.5 h-4 w-4 shrink-0" />
            <span>{feature}</span>
          </li>
        ))}
      </ul>
    </motion.div>
  );
}

export function Pricing(): ReactNode {
  const freePlan = plans[0];
  const proPlan = plans[1];
  
  if (!freePlan || !proPlan) {
    return null;
  }

  return (
    <section className="bg-muted px-6 py-16 md:py-32">
      <div className="mx-auto max-w-6xl">
        <motion.div
          className="mb-12 text-center md:mb-16"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, ease: easeOut }}
        >
          <h2 className="mb-4 text-3xl font-medium tracking-tight md:text-4xl lg:text-5xl">
            Open-Core Pricing
          </h2>
          <p className="text-muted-foreground text-lg">
            Open-source agent harness and memory bridge — bring your own Anthropic keys and hosting.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 items-start gap-6 md:grid-cols-2 md:gap-8">
          <div className="md:mt-16">
            <PlanCard plan={freePlan} />
          </div>

          <div>
            <PlanCard plan={proPlan} />
          </div>
        </div>

        <motion.div
          className="mt-12 flex flex-col items-center gap-4 md:mt-16"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.2, ease: easeOut }}
        >
          <a
            href="#"
            className="group inline-flex w-full items-center justify-center gap-3 rounded-md bg-accent py-3 pl-5 pr-3 font-medium text-black transition-all duration-500 ease-out hover:rounded-[50px] hover:shadow-lg hover:shadow-accent/20 sm:w-auto"
          >
            <span>View on GitHub</span>
            <span className="flex h-10 w-10 items-center justify-center rounded-full bg-white text-black transition-all duration-300 group-hover:scale-110">
              <ChevronRightIcon className="h-4 w-4 relative left-px" />
            </span>
          </a>
          <a
            href="#"
            className="text-muted-foreground text-sm transition-colors hover:text-foreground"
          >
            Read the docs
          </a>
        </motion.div>
      </div>
    </section>
  );
}
