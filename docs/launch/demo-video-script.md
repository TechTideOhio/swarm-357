# Demo Video Script — 90 Seconds

**Title card:** TechTide Swarm 357 — 357 Claude AI Agents, One `pip install`

---

## Shot 1 — Install (0:00–0:12)

**Screen:** Clean terminal, dark background.

```bash
pip install techtide-swarm
```

**Voiceover:**
> "This installs 357 AI agents. Sales, Support, Marketing, SEO, Research, Operations — and a management layer that coordinates all of them."

**On screen:** Progress bar completes. `Successfully installed techtide-swarm-0.1.0`

---

## Shot 2 — Architecture View (0:12–0:28)

**Screen:** Run `swarm demo` — no API key needed for this view.

```bash
swarm demo
```

**Expected terminal output:**
```
TechTide Swarm 357 — Architecture

              Management (10)
                   |
  +------+------+------+------+------+------+
  Sales  Support Marketing  SEO  Research  Ops
  (62)    (55)    (68)      (47)    (58)   (57)

Model distribution:
  Opus   →  10 agents  (management)
  Sonnet → 195 agents  (senior roles)
  Haiku  → 152 agents  (high-frequency)

Budget ceiling: $2,500 / day across all layers
BashSecurityGate: 13 patterns, 50+ tests
```

**Voiceover:**
> "The architecture tab shows the full org chart. Ten Opus management agents. 195 Sonnet. 152 Haiku for the high-frequency tasks."

---

## Shot 3 — Live Multi-Agent Execution (0:28–1:08)

**Screen:** Run the GTM task with streaming output.

```bash
swarm run "Launch a GTM campaign for an AI training product"
```

**Expected streaming output (shown as it streams):**
```
[Conductor]  Routing to: research (2), marketing (3), sales (2), seo (1)
[Conductor]  Budget allocated: $0.18 ceiling

[research-market-001]  Analyzing AI training market...
[research-market-001]  → Target segments: enterprise L&D, dev bootcamps, university upskilling
[research-trend-001]   Trend data: 340% YoY growth in enterprise AI training spend

[marketing-strategy-001]  Building positioning...
[marketing-strategy-001]  → Angle: ROI-first ("train your team once, automate 40% of tasks")
[marketing-content-001]   Draft landing page headline: "Your team, AI-ready in 90 days"
[marketing-email-001]     Email sequence: 5-part nurture for cold outreach

[seo-keyword-001]  Keyword clusters: "AI training for teams" (8.2K/mo), "enterprise AI upskilling" (3.1K/mo)

[sales-outreach-001]   ICP definition: Director of L&D at companies 200-2000 employees
[sales-outreach-001]   → LinkedIn sequence: 4 touchpoints, 14-day cadence
[sales-sdr-001]        Cold email subject lines: 3 variants for A/B test

✓ Complete
```

**Voiceover:**
> "Watch the Conductor route the task. Research agents pull market data. Marketing agents build positioning. Sales agents write the outreach. SEO agents find the keywords. It's streaming live."

---

## Shot 4 — Cost Breakdown (1:08–1:22)

**Screen:** Run `swarm cost` or show the cost summary from the previous run.

```bash
swarm cost
```

**Expected output:**
```
Model Usage — Last Run
─────────────────────────────────────────────────
Model     Agents   Tokens In   Tokens Out   Cost
Opus         1       1,240        380       $0.047
Sonnet       6       8,100      2,890       $0.067
Haiku        1       2,200        610       $0.005
─────────────────────────────────────────────────
Total        8      11,540      3,880       $0.119
Duration: 67 seconds
─────────────────────────────────────────────────
```

**Final text overlay:**
```
357 agents available
$0.0773 for a full GTM campaign
67 seconds end-to-end
```

**Voiceover:**
> "One complete go-to-market plan. Twelve cents. Forty-three seconds."

---

## Shot 5 — Outro (1:22–1:30)

**Screen:** GitHub repo URL + install command side by side.

```
github.com/TechTideOhio/swarm357
pip install techtide-swarm
```

**Voiceover:**
> "Open source. Apache 2. Try it now."

---

## Recording Notes

### Setup
- Terminal: use a dark theme (VS Code Dark+, Dracula, or Tokyo Night)
- Font: JetBrains Mono or Fira Code at 16–18pt for readability
- Resolution: record at 1920×1080 minimum
- Run `swarm init` in a fresh temp directory before recording
- Have `ANTHROPIC_API_KEY` set in env for shots 3 and 4

### Pre-flight checks
```bash
# Verify the package installs clean
pip install techtide-swarm
swarm --version

# Verify demo works
swarm demo

# Do a dry run of the GTM task to confirm output shape
swarm run "Launch a GTM campaign for an AI training product"
swarm cost
```

### Screen recording tools
- **macOS:** QuickTime Player (File → New Screen Recording)
- **Windows:** OBS Studio (free, no watermark)
- **Linux:** OBS Studio or `simplescreenrecorder`

### Editing
- Keep raw takes under 3 minutes; cut to 90s in post
- Add title cards between shots using DaVinci Resolve (free) or CapCut
- Export: H.264, 1080p, at least 8 Mbps for upload quality
- Upload to YouTube as unlisted first, test playback before publishing

### Captions
- Add auto-captions on YouTube, then manually fix any misheard technical terms
- Key terms to verify: Memvid, BashSecurityGate, Sonnet, Haiku, pyproject
