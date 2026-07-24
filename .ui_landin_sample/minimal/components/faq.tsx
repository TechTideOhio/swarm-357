"use client";

import { ChevronDown, ChevronRightIcon } from "lucide-react";
import { AnimatePresence, motion, useInView } from "motion/react";
import { useRef, useState, type ReactNode } from "react";

const easeOut = [0.16, 1, 0.3, 1] as const;

const faqs = [
  {
    question: "Do I need all 357 agents running at once?",
    answer:
      "No. The 357 roles are a template catalog. You boot only the layers and agents your task needs. A typical swarm run uses 3-8 agents across 2-3 layers. Budget caps prevent runaway costs.",
  },
  {
    question: "What happens if the Memvid bridge is not installed?",
    answer:
      "MemoryManager gracefully falls back to flat .swarm/topics/ JSON files. The bridge is optional — install it when you want portable, searchable .mv2 memory with integrity verification.",
  },
  {
    question: "Does this work without an Anthropic API key?",
    answer:
      "Yes. The CLI runs in simulation mode without a key — swarm demo shows the full architecture and pipeline with stub outputs. Set ANTHROPIC_API_KEY for live Claude execution.",
  },
  {
    question: "How does the security gate work?",
    answer:
      "BashSecurityGate validates every shell command against 13 pattern rules before execution. It blocks destructive operations, secret exfiltration, elevated commands, and remote code injection. Every rule has a corresponding test.",
  },
  {
    question: "Can I use models other than Claude?",
    answer:
      "Currently the Agent class targets Claude (opus, sonnet, haiku) via the Anthropic API. The architecture is model-agnostic at the config level — AgentConfig.model is a string — but the runtime adapter only implements Anthropic today.",
  },
];

function FAQItem({
  faq,
  index,
  isOpen,
  onToggle,
}: {
  faq: (typeof faqs)[0];
  index: number;
  isOpen: boolean;
  onToggle: () => void;
}): ReactNode {
  return (
    <motion.div
      className="border-foreground/10 border-b last:border-b-0"
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, amount: 0.5 }}
      transition={{ duration: 0.5, delay: index * 0.05, ease: easeOut }}
    >
      <button
        onClick={onToggle}
        className="group flex w-full items-center justify-between py-6 text-left"
      >
        <span className="text-foreground text-lg font-medium pr-8 md:text-xl">
          {faq.question}
        </span>
        <motion.div
          className="text-foreground/50 shrink-0"
          animate={{ rotate: isOpen ? 180 : 0 }}
          transition={{ duration: 0.3, ease: easeOut }}
        >
          <ChevronDown className="h-5 w-5" />
        </motion.div>
      </button>
      <AnimatePresence initial={false}>
        {isOpen && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3, ease: easeOut }}
            className="overflow-hidden"
          >
            <p className="text-muted-foreground pb-6 text-base leading-relaxed">
              {faq.answer}
            </p>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

export function FAQ(): ReactNode {
  const [openIndex, setOpenIndex] = useState<number | null>(null);
  const headerRef = useRef<HTMLDivElement>(null);
  const isHeaderInView = useInView(headerRef, { once: true, amount: 0.5 });

  const handleToggle = (index: number) => {
    setOpenIndex(openIndex === index ? null : index);
  };

  return (
    <section className="bg-foreground px-6 py-16 md:py-32 rounded-4xl">
      <div className="mx-auto max-w-3xl">
        <motion.div
          ref={headerRef}
          className="mb-12 text-center md:mb-16"
          initial={{ opacity: 0, y: 20 }}
          animate={isHeaderInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
          transition={{ duration: 0.6, ease: easeOut }}
        >
          <h2 className="text-background text-3xl font-medium tracking-tight md:text-4xl lg:text-5xl">
            Common Questions
          </h2>
        </motion.div>

        <motion.div
          className="bg-background rounded-2xl px-6 md:px-10 py-2"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.3 }}
          transition={{ duration: 0.6, ease: easeOut }}
        >
          {faqs.map((faq, index) => (
            <FAQItem
              key={faq.question}
              faq={faq}
              index={index}
              isOpen={openIndex === index}
              onToggle={() => handleToggle(index)}
            />
          ))}
        </motion.div>

        <motion.div
          className="mt-12 text-center"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.5 }}
          transition={{ duration: 0.6, delay: 0.2, ease: easeOut }}
        >
          <p className="text-background/60 mb-6 text-base">
            Still have questions? Open an issue on GitHub.
          </p>
          <a
            href="https://github.com/TechTideOhio/swarm-357/issues"
            className="group inline-flex items-center gap-3 rounded-md bg-background py-3 pl-5 pr-3 font-medium text-foreground shadow-lg transition-all duration-500 ease-out hover:rounded-[50px]"
          >
            <span>Open an issue</span>
            <span className="flex h-10 w-10 items-center justify-center rounded-full bg-foreground text-background transition-all duration-300 group-hover:scale-110">
              <ChevronRightIcon className="h-4 w-4 relative left-px" />
            </span>
          </a>
        </motion.div>
      </div>
    </section>
  );
}
