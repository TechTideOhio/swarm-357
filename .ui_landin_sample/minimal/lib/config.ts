/**
 * Site Configuration
 *
 * Central configuration file for easy customization.
 * Update these values to personalize your template.
 */

export const siteConfig = {
  name: "Swarm 357",
  tagline: "Layered agents. Durable memory. Observable runs.",
  description:
    "357 Claude agents across six business layers—sales, support, marketing, SEO, research, and operations—backed by portable Memvid memory and a Claude Code–native workflow.",
  url: "https://swarm357.techtide.ai",
  social: {
    twitter: "@techtide",
    github: "https://github.com/TechTideOhio/swarm-357",
  },
  nav: {
    cta: {
      text: "Get the repo",
      href: "https://github.com/TechTideOhio/swarm-357",
    },
    signIn: {
      text: "Docs",
      href: "https://github.com/TechTideOhio/swarm-357/blob/main/CLAUDE.md",
    },
  },
} as const;

export const heroConfig = {
  headline: {
    prefix: "Run the",
    accent: "Swarm",
    suffix: "enterprise agents actually ship",
  },
  description:
    "Orchestrate domain specialists with a single CLI, replace flat-file memory with searchable .mv2 capsules when you are ready, and keep costs and traces honest—without pretending three hundred agents are a substitute for governance.",
  cta: {
    primary: {
      text: "Install the Python package",
      href: "https://github.com/TechTideOhio/swarm-357/tree/main/packages/techtide-swarm",
    },
    secondary: {
      text: "See architecture",
      href: "#how-it-works",
    },
  },
  carousel: [
    "Sales plays",
    "Support macros",
    "Campaign briefs",
    "SEO clusters",
    "Research packs",
    "Ops runbooks",
    "Memvid recall",
    "Opik traces",
    "Budget caps",
    "Bash policy gate",
    "Layer health",
    "UltraPlan",
  ],
} as const;

export const howItWorksConfig = {
  title: "Acquire, orchestrate, remember, observe",
  description:
    "Marketing site and docs bring people in; the swarm CLI and YAML layers coordinate work; Memvid stores portable memory; Opik (optional) and cost reports keep production honest.",
  cta: {
    text: "Read CLAUDE.md",
    href: "https://github.com/TechTideOhio/swarm-357/blob/main/CLAUDE.md",
  },
} as const;

export const featuresConfig = {
  title: "Built for Claude Code",
  description:
    "One repository ties a Next.js surface, a Python agent package, and the Memvid Rust core—so contributors can improve memory, hooks, or UI without three separate releases.",
} as const;

export const statsConfig = {
  title: "Designed for scale",
  description: "Six business layers plus management meta-agents—templates and tests matter more than raw headcount.",
} as const;

export const testimonialsConfig = {
  title: "What teams ask for",
} as const;

export const pricingConfig = {
  title: "Pricing",
  description: "Open-core agent harness and memory bridge—bring your own Anthropic keys and hosting.",
  cta: {
    primary: {
      text: "View on GitHub",
      href: "https://github.com/TechTideOhio/swarm-357",
    },
    secondary: {
      text: "Enterprise controls",
      href: "https://github.com/TechTideOhio/swarm-357/blob/main/docs/ENTERPRISE_CONTROLS.md",
    },
  },
} as const;

export const faqConfig = {
  title: "Common Questions",
  contact: {
    text: "Still have questions? Open an issue on GitHub.",
    cta: {
      text: "Get in Touch",
      href: "https://github.com/TechTideOhio/swarm-357/issues",
    },
  },
} as const;

export const finalCtaConfig = {
  headline: "Ready to wire durable memory into your agent mesh?",
  description:
    "Clone the repo, pip install the techtide-swarm package, optional-build the Memvid bridge, and point your Claude Code session at CLAUDE.md.",
  cta: {
    text: "Start with swarm init",
    href: "https://github.com/TechTideOhio/swarm-357",
  },
} as const;

export const footerConfig = {
  description:
    "Swarm 357 pairs layered business agents with Memvid single-file memory and honest cost surfaces—so your GitHub story matches what security and FinOps reviewers can verify.",
  cta: {
    text: "Documentation",
    href: "https://github.com/TechTideOhio/swarm-357/blob/main/CLAUDE.md",
  },
  links: {
    product: [
      { label: "Python package", href: "https://github.com/TechTideOhio/swarm-357/tree/main/packages/techtide-swarm" },
      { label: "Memvid bridge", href: "https://github.com/TechTideOhio/swarm-357/tree/main/packages/memvid-swarm-bridge" },
      { label: "CLI reference", href: "https://github.com/TechTideOhio/swarm-357/blob/main/CLAUDE.md" },
      { label: "Enterprise controls", href: "https://github.com/TechTideOhio/swarm-357/blob/main/docs/ENTERPRISE_CONTROLS.md" },
    ],
    company: [
      { label: "About", href: "/about" },
      { label: "Architecture", href: "https://github.com/TechTideOhio/swarm-357/blob/main/CLAUDE.md" },
      { label: "Evals", href: "https://github.com/TechTideOhio/swarm-357/blob/main/docs/EVALS.md" },
      { label: "Contributing", href: "https://github.com/TechTideOhio/swarm-357/blob/main/CONTRIBUTING.md" },
    ],
  },
  contact: {
    location: "Remote",
    address: "",
    hours: "",
    email: "https://github.com/TechTideOhio/swarm-357/issues",
  },
  copyright: `© ${new Date().getFullYear()} TechTide Swarm 357`,
} as const;

/**
 * Feature Flags
 *
 * Toggle features on/off for easy customization.
 */
export const features = {
  smoothScroll: true,
  darkMode: true,
  ditherCursor: true,
  statsSection: true,
  testimonialsSection: false,
} as const;

export const apiConfig = {
  url: process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000",
} as const;
