import { FAQ } from "@/components/faq";
import { AgentRoster } from "@/components/agent-roster";
import { FinalCTA } from "@/components/final-cta";
import { Hero } from "@/components/hero";
import { HowItWorks } from "@/components/how-it-works";
import { Pricing } from "@/components/pricing";
import { LiveStats } from "@/components/live-stats";
import { Testimonials } from "@/components/testimonials";
import { RecentRuns } from "@/components/recent-runs";
import { features } from "@/lib/config";
import type { Metadata } from "next";
import { createMetadata, siteConfig } from "@/lib/metadata";
import type { ReactNode } from "react";

export const metadata: Metadata = createMetadata({
  title: `${siteConfig.name} - ${siteConfig.tagline}`,
  description: siteConfig.description,
  path: "/",
});

export default function HomePage(): ReactNode {
  return (
    <main id="main-content" className="flex-1">
      <Hero />
      <HowItWorks />
      <AgentRoster />
      <LiveStats />
      <RecentRuns />
      {features.testimonialsSection ? <Testimonials /> : null}
      <Pricing />
      <FAQ />
      <FinalCTA />
    </main>
  );
}
