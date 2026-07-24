# Twitter/X Thread u2014 10 Tweets

**Hook:** "I built a 357-agent AI system that can run an entire business. Here is what I learned."

---

## Tweet 1 (Hook)

> I built a 357-agent AI system that can run an entire business.
>
> Sales. Support. Marketing. SEO. Research. Ops. All coordinated by a management layer of 10 Opus agents.
>
> One `pip install`. $0.0773 for a full GTM campaign.
>
> Hereu2019s what I learned. ud83euddf5

*[attach: architecture diagram screenshot]*

---

## Tweet 2 (Architecture)

> The org chart maps to real business structure:
>
> ud83cudfc6 Management (10) u2014 Conductor routes every task
> ud83dudcbc Sales (62) u2014 CRM, outreach, SDR, deal closing
> ud83cudfa7 Support (55) u2014 tier-1 through escalation
> ud83dudcca Marketing (68) u2014 content, email, social, ads
> ud83dudd0d SEO (47) u2014 keywords, technical audits, AEO
> ud83dudd2c Research (58) u2014 market, competitor, product
> u2699ufe0f Operations (57) u2014 finance, project coordination
>
> Not agent A talking to agent B. An actual org structure.

---

## Tweet 3 (Cost controls)

> The scariest thing about multi-agent systems: runaway costs.
>
> Hereu2019s how I solved it:
>
> u2192 Per-agent budget caps (enforced per turn)
> u2192 Per-layer daily limits ($500 Sales, $300 Support, $200 SEOu2026)
> u2192 Auto model downgrade at 80% utilization
>
> Total ceiling: $2,500/day for all 357 agents.
> A full GTM campaign costs $0.0773.
>
> Cost controls arenu2019t bolted on. Theyu2019re enforced in code.

---

## Tweet 4 (Memory)

> Every agent forgets everything between sessions.
>
> My fix: three-layer memory architecture.
>
> 1ufe0fu20e3 MEMORY.md u2014 pointer index, always in context
> 2ufe0fu20e3 topics/ u2014 knowledge files, fetched on demand
> 3ufe0fu20e3 Memvid .mv2 u2014 single-file store, WAL-based, full-text + vector search
>
> No database server. The .mv2 file travels with the agent.
>
> `swarm dream` consolidates memory across the whole swarm.

---

## Tweet 5 (Security)

> Giving 357 agents access to a Bash tool isu2026 a liability.
>
> Built BashSecurityGate: 13 regex patterns that block:
>
> u2022 `rm -rf /` and `rm -rf ~`
> u2022 `curl | bash` and `wget | sh`
> u2022 Secret env vars in argv (`$ANTHROPIC_API_KEY`)
> u2022 Writes to `/etc/`, block devices, network listeners
> u2022 `chmod 777`, `sudo rm`, disk format commands
>
> 50+ tests. Every new pattern gets a scenario test first.
>
> Security at the tool layer, not just the prompt.

---

## Tweet 6 (Soul templates)

> Each agent has a u201csoulu201d u2014 a YAML front-matter personality file.
>
> Example from the Conductor:
> u2022 Primary mission
> u2022 Decision rules with confidence gates
> u2022 Tool usage guidelines
> u2022 2u20134 worked examples of routing decisions
>
> 42 personality files across all layers.
>
> This is what separates a research agent from a sales agent from an ops agent.
> Same model. Different behavior.

---

## Tweet 7 (What surprised me)

> What surprised me most:
>
> The routing problem is harder than the agent problem.
>
> Writing a good Sales agent: 2 hours.
> Building a Conductor that routes correctly across 357 agents: 2 weeks.
>
> Lesson: multi-agent systems fail at the seams.
> The handoff logic determines whether the whole thing works.

---

## Tweet 8 (Eval results)

> We run a 5-task benchmark on every change:
>
> Task 1: Market research synthesis u2014 u2713
> Task 2: Cold email sequence u2014 u2713
> Task 3: Technical SEO audit u2014 u2713
> Task 4: Support ticket triage u2014 u2713
> Task 5: Financial variance report u2014 u2713
>
> Scored by keyword overlap vs. baseline.
> Rudimentary? Yes. But it catches regressions before they ship.
>
> `swarm eval` u2014 run it yourself.

---

## Tweet 9 (Open source)

> Iu2019m open-sourcing all of it:
>
> u2022 357-agent config (swarm.yaml)
> u2022 42 soul template files
> u2022 BashSecurityGate (13 patterns, 50+ tests)
> u2022 Memvid bridge (Rust CLI for .mv2 memory)
> u2022 Full CLI: init, boot, run, dream, plan, eval, serve
> u2022 FastAPI server + Docker
>
> Apache 2.0.
>
> Because the framework for running a business with AI shouldnu2019t be proprietary.

---

## Tweet 10 (CTA)

> ud83euddea Try it:
> `pip install techtide-swarm`
> `swarm demo`  u2190 works without an API key
>
> ud83dudcfa Watch the 90-second demo:
> [youtube link]
>
> u2b50 Star the repo:
> github.com/TechTideOhio/swarm357
>
> ud83dudcac Questions? Reply here.
>
> Everything is documented. Nothing is hidden.

---

## Thread Notes

- Post all 10 tweets in one thread (reply chain starting from Tweet 1)
- Best posting times: Tuesdayu2013Thursday, 9u201311 AM ET or 1u20133 PM ET
- Pin Tweet 1 to your profile during launch week
- Add architecture screenshot to Tweet 1, terminal screenshot to Tweet 3
- Engage with every reply in the first 2 hours u2014 this is how threads go viral
- Repost Tweet 10 standalone 24 hours later for second wave reach
