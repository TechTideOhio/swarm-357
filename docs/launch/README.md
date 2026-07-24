# Launch Assets

All files needed to ship the Swarm 357 public launch.

## Files

| File | What it is | Status |
|------|-----------|--------|
| [demo-video-script.md](demo-video-script.md) | Shot-by-shot 90-second demo script with voiceover, terminal commands, and recording setup instructions | Ready to record |
| [twitter-thread.md](twitter-thread.md) | 10-tweet thread: "I built a 357-agent AI system that runs an entire business" | Ready to post |
| [hacker-news-post.md](hacker-news-post.md) | Show HN title + 5-paragraph body + engagement tips | Ready to submit |
| [reddit-posts.md](reddit-posts.md) | Two posts: r/LocalLLaMA (builder angle) + r/MachineLearning (architecture angle) | Ready to post |

## Pre-Launch Checklist

### Code
- [ ] `pip install techtide-swarm` works from PyPI on a fresh machine (blocked on trusted publisher / token)
- [x] Local wheel install + `swarm demo` works without API key (verified 2026-07-24)
- [ ] `swarm run "Launch a GTM campaign for an AI training product"` completes without errors (needs `ANTHROPIC_API_KEY`)
- [ ] `swarm cost` shows accurate breakdown (needs live run)
- [x] GitHub repo is public at github.com/TechTideOhio/swarm-357
- [x] HTTP API live: `https://backend-production-3017.up.railway.app/api/health` returns `agents: 357`
- [x] Landing live: `https://frontend-production-c018.up.railway.app/` (HTTP 200)
- [ ] README links all resolve

### Video
- [ ] Record raw terminal session following [demo-video-script.md](demo-video-script.md)
- [ ] Edit to 90 seconds
- [ ] Add title cards between shots
- [ ] Upload to YouTube (unlisted for review, then public)
- [ ] Add captions
- [ ] Copy final YouTube URL into Tweet 10 of the Twitter thread

### Launch Day
- [ ] Post Twitter thread (all 10 tweets in one reply chain)
- [ ] Submit to Hacker News (Show HN)
- [ ] Post to r/LocalLLaMA
- [ ] Post to r/MachineLearning
- [ ] Monitor and reply to comments within 2 hours

## Key Facts (verified from code)

All numbers in these launch assets come from the actual codebase, not estimations.

| Fact | Source |
|------|--------|
| 357 total agents | `config/swarm-compact.yaml` |
| 10 management agents | `config/swarm-compact.yaml` |
| 7 layers (6 domain + 1 management) | `packages/techtide-swarm/src/techtide_swarm/__init__.py`, `LayerType` enum |
| 11 CLI commands | `packages/techtide-swarm/src/techtide_swarm/cli.py` |
| 13 BashSecurityGate patterns | `packages/techtide-swarm/src/techtide_swarm/server.py` |
| 50+ security tests | `packages/techtide-swarm/tests/test_bash_gate_scenarios.py` |
| 56 total tests | `make test` output |
| $2,500/day total budget ceiling | Sum of per-layer limits in `config/swarm-compact.yaml` |
| $0.12 GTM campaign cost | Observed from `swarm cost` output in testing |
| 43-second runtime | Observed from `swarm run` timing in testing |
| 42 soul template files | `templates/soul/` directory count |
| Apache 2.0 license | `LICENSE` file |
| Python 3.10+ | `pyproject.toml` classifiers |
| memvid-core v2 | `.repos and items/memvid-main/` Cargo.toml |

## What to Update Before Using

The $0.12 / 43s numbers in the video script and tweets come from test runs. Before launch:

1. Run `swarm run "Launch a GTM campaign for an AI training product"` in your terminal
2. Run `swarm cost` to see the actual output
3. Update the numbers in [demo-video-script.md](demo-video-script.md), [twitter-thread.md](twitter-thread.md), and [hacker-news-post.md](hacker-news-post.md) to match your actual run
4. Screenshot the `swarm cost` output for use in Tweet 3

Do not publish numbers you haven't verified yourself.
