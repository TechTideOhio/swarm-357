#!/usr/bin/env python3
"""
TechTide Swarm 357 — CLI

The command-line interface. This is the first thing people interact with.
Every command must feel fast, look beautiful, and deliver instant value.

Usage:
    swarm init          # Initialize a new swarm project
    swarm demo          # Run the 60-second demo (5 agents, real output)
    swarm boot          # Boot all 357 agents
    swarm run <task>    # Run a task across the swarm
    swarm status        # Show swarm health dashboard
    swarm agent <id>    # Inspect a specific agent
    swarm cost          # Show cost report
    swarm dream         # Trigger a memory consolidation cycle
    swarm plan <task>   # ULTRAPLAN: deep Opus planning session
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

if TYPE_CHECKING:
    from rich.console import Console

# Rich imports for beautiful terminal output. `rich` is a hard dependency, so
# this import succeeds in any correctly installed environment; the fallback is a
# defensive guard for partial installs.
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import (
        BarColumn,
        Progress,
        SpinnerColumn,
        TextColumn,
        TimeElapsedColumn,
    )
    from rich.table import Table
    from rich.tree import Tree
    from rich import box
    HAS_RICH = True
except ImportError:  # pragma: no cover - rich is a declared dependency
    HAS_RICH = False

console: Console = Console() if HAS_RICH else cast("Console", None)

# ──────────────────────────────────────────────
# ASCII Banner
# ──────────────────────────────────────────────

BANNER = r"""
[bold cyan]
  ████████╗███████╗ ██████╗██╗  ██╗████████╗██╗██████╗ ███████╗
  ╚══██╔══╝██╔════╝██╔════╝██║  ██║╚══██╔══╝██║██╔══██╗██╔════╝
     ██║   █████╗  ██║     ███████║   ██║   ██║██║  ██║█████╗
     ██║   ██╔══╝  ██║     ██╔══██║   ██║   ██║██║  ██║██╔══╝
     ██║   ███████╗╚██████╗██║  ██║   ██║   ██║██████╔╝███████╗
     ╚═╝   ╚══════╝ ╚═════╝╚═╝  ╚═╝   ╚═╝   ╚═╝╚═════╝ ╚══════╝
[/bold cyan]
[bold white]               ⚡ S W A R M   3 5 7 ⚡[/bold white]
[dim]        357 Claude AI Agents · 6 Business Layers · 1 Swarm[/dim]
"""

BANNER_PLAIN = """
  TECHTIDE SWARM 357
  357 Claude AI Agents · 6 Business Layers · 1 Swarm
"""


def print_banner() -> None:
    if HAS_RICH:
        try:
            console.print(BANNER)
        except UnicodeEncodeError:
            console.print(BANNER_PLAIN)
    else:
        print(BANNER_PLAIN)


# ──────────────────────────────────────────────
# Commands
# ──────────────────────────────────────────────

def cmd_init(args: argparse.Namespace) -> None:
    """Initialize a new swarm project in the current directory."""
    print_banner()
    console.print("\n[bold green]⚡ Initializing TechTide Swarm 357...[/bold green]\n")

    dirs = [
        ".swarm",
        ".swarm/topics",
        ".swarm/transcripts",
        ".swarm/audit",
        "agents/sales",
        "agents/support",
        "agents/marketing",
        "agents/seo",
        "agents/research",
        "agents/operations",
    ]

    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Creating directories...", total=len(dirs))
        for d in dirs:
            Path(d).mkdir(parents=True, exist_ok=True)
            progress.advance(task)
            time.sleep(0.05)

        # Create .env if not exists
        progress.update(task, description="Creating .env...")
        env_path = Path(".env")
        if not env_path.exists():
            env_path.write_text(
                "ANTHROPIC_API_KEY=sk-ant-your-key-here\n"
                "OPIK_API_KEY=your-opik-key\n"
                "OPIK_WORKSPACE=techtide\n"
            )

        # Create MEMORY.md
        progress.update(task, description="Initializing memory...")
        mem_path = Path(".swarm/MEMORY.md")
        if not mem_path.exists():
            mem_path.write_text("# TechTide Swarm 357 — Memory Index\n# 0 pointers\n")

    console.print("\n[bold green]✅ Swarm initialized![/bold green]")
    console.print("\n[dim]Next steps:[/dim]")
    console.print("  1. Add your ANTHROPIC_API_KEY to .env")
    console.print("  2. Run [bold]swarm demo[/bold] to see architecture + sample output")
    console.print("  3. Run [bold]swarm run 'your task'[/bold] to execute across the swarm\n")


def cmd_demo(args: argparse.Namespace) -> None:
    """Run the demo — live with API key, architecture overview without."""
    print_banner()

    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    has_key = bool(api_key) and "your-key" not in api_key

    if has_key:
        console.print("\n[bold green]LIVE DEMO — calling Claude API[/bold green]\n")
        asyncio.run(_demo_live())
    else:
        console.print("\n[bold yellow]SIMULATION — no ANTHROPIC_API_KEY set[/bold yellow]")
        console.print("[dim]Set ANTHROPIC_API_KEY for live agent execution.[/dim]\n")
        _demo_simulation()


def _demo_simulation() -> None:
    """Show architecture + run real parallel stub pipeline — clearly labeled as simulation."""
    # Architecture tree
    tree = Tree("[bold]Swarm 357 Architecture[/bold]")
    layers = [
        ("Management", 10, "opus", "Conductor, strategy, memory curation"),
        ("Sales", 62, "sonnet/haiku", "CRM, outreach, prospecting, SDR"),
        ("Support", 55, "haiku", "Tier-1/2 resolution, knowledge base"),
        ("Marketing", 68, "sonnet", "Content, social, ads, email, brand"),
        ("SEO", 47, "haiku", "Keywords, technical audit, link building"),
        ("Research", 58, "sonnet", "Market, competitor, trends, synthesis"),
        ("Operations", 57, "sonnet", "Project coordination, finance, infra"),
    ]
    for name, count, model, desc in layers:
        branch = tree.add(f"[bold]{name}[/bold] ({count} agents, {model})")
        branch.add(f"[dim]{desc}[/dim]")
    console.print(tree)
    console.print()

    # Run a real 3-agent parallel stub pipeline using asyncio.gather — proves architecture works
    console.print("[bold]Running 3-agent parallel stub pipeline[/bold] [dim](no API key — stub mode)[/dim]\n")

    async def _run_stub_pipeline() -> list[Any]:
        from techtide_swarm import Agent, AgentConfig
        from techtide_swarm.core.types import LayerType

        task = "What are the top 3 growth opportunities for a B2B SaaS company in 2026?"
        agents = [
            Agent(AgentConfig(
                name="demo-market-analyst-001", layer=LayerType.RESEARCH,
                role="market_analyst", soul="templates/soul/research/market-analyst.md",
                tools=["Read", "Write"], model="sonnet", budget_limit_usd=1.0,
            )),
            Agent(AgentConfig(
                name="demo-content-strategist-001", layer=LayerType.MARKETING,
                role="content_strategist", soul="templates/soul/marketing/content-strategist.md",
                tools=["Read", "Write"], model="sonnet", budget_limit_usd=1.0,
            )),
            Agent(AgentConfig(
                name="demo-keyword-researcher-001", layer=LayerType.SEO,
                role="keyword_researcher", soul="templates/soul/seo/keyword-researcher.md",
                tools=["Read", "Write"], model="haiku", budget_limit_usd=0.5,
            )),
        ]
        # asyncio.gather proves real concurrency — not time.sleep
        return list(await asyncio.gather(*[a.run(task) for a in agents]))

    import time as _time
    started = _time.perf_counter()
    results = asyncio.run(_run_stub_pipeline())
    elapsed = _time.perf_counter() - started

    table = Table(box=box.SIMPLE_HEAD, show_header=True, title="Parallel Stub Pipeline")
    table.add_column("Agent", style="cyan", min_width=30)
    table.add_column("Layer", min_width=10)
    table.add_column("Status", justify="center")
    table.add_column("Output Preview", max_width=55)

    role_layer = [("Research", "market_analyst"), ("Marketing", "content_strategist"), ("SEO", "keyword_researcher")]
    for r, (layer_name, _) in zip(results, role_layer):
        preview = (r.output or "")[:80].replace("\n", " ")
        table.add_row(r.agent_name, layer_name, "[green]stub[/green]", preview)

    console.print(table)
    console.print(
        f"\n[dim]3 agents dispatched via asyncio.gather · {elapsed:.2f}s · "
        f"[simulation mode — set ANTHROPIC_API_KEY for live][/dim]\n"
    )
    console.print("[bold]Next steps:[/bold]")
    console.print("  1. [cyan]export ANTHROPIC_API_KEY=sk-ant-...[/cyan]")
    console.print("  2. [cyan]swarm demo[/cyan]   (3 live API calls, real output)")
    console.print("  3. [cyan]swarm run 'your task' --layer research[/cyan]   (58 agents in parallel)\n")


async def _demo_live() -> None:
    """Live 3-layer pipeline: Research -> Marketing -> SEO. Three real API calls."""
    from techtide_swarm import Agent, AgentConfig
    from techtide_swarm.core.types import LayerType

    TASK = "What are the top 3 growth opportunities for a B2B SaaS company in 2026?"

    pipeline = [
        ("Research", AgentConfig(
            name="demo-market-analyst-001", layer=LayerType.RESEARCH,
            role="market_analyst", soul="templates/soul/research/market-analyst.md",
            tools=["Read", "Write"], model="sonnet", max_turns=3, budget_limit_usd=1.50,
        )),
        ("Marketing", AgentConfig(
            name="demo-content-strategist-001", layer=LayerType.MARKETING,
            role="content_strategist", soul="templates/soul/marketing/content-strategist.md",
            tools=["Read", "Write"], model="sonnet", max_turns=3, budget_limit_usd=1.50,
        )),
        ("SEO", AgentConfig(
            name="demo-keyword-researcher-001", layer=LayerType.SEO,
            role="keyword_researcher", soul="templates/soul/seo/keyword-researcher.md",
            tools=["Read", "Write"], model="haiku", max_turns=3, budget_limit_usd=0.50,
        )),
    ]

    console.print(f"[bold]Task:[/bold] {TASK}\n")
    console.print("[dim]Pipeline: Research -> Marketing -> SEO[/dim]\n")

    total_cost = 0.0
    context = TASK

    for layer_name, cfg in pipeline:
        with Progress(
            SpinnerColumn(),
            TextColumn(f"[bold blue]{layer_name} ({cfg.name})...[/bold blue]"),
            TimeElapsedColumn(),
            console=console,
            transient=True,
        ) as progress:
            progress.add_task("", total=None)
            result = await Agent(cfg).run(context)

        if result.status == "success":
            total_cost += result.cost_usd
            # Pass output as context to the next layer
            context = f"Prior research:\n{result.output}\n\nOriginal task: {TASK}"
            console.print(Panel(
                result.output[:1200],
                title=f"{layer_name} — {cfg.name}",
                border_style="green",
                subtitle=f"${result.cost_usd:.4f} · {result.latency_ms}ms",
            ))
        else:
            console.print(f"[red]{layer_name} failed: {result.error}[/red]")

    console.print(f"\n[bold]Pipeline complete. Total cost: [yellow]${total_cost:.4f}[/yellow][/bold]\n")


def cmd_status(args: argparse.Namespace) -> None:
    """Show swarm health dashboard."""
    print_banner()
    console.print("\n[bold]📊 Swarm Status Dashboard[/bold]\n")
    
    try:
        from techtide_swarm.telemetry import get_layer_stats
        stats = get_layer_stats()
        if not stats:
            console.print("[dim]No live telemetry data available yet. Run agents to generate metrics.[/dim]")
            return
            
        table = Table(
            title="Layer Health",
            box=box.HEAVY_EDGE,
            show_header=True,
            header_style="bold white on blue",
        )
        table.add_column("Layer", style="bold", min_width=12)
        table.add_column("Calls", justify="center")
        table.add_column("Cost", justify="right", style="yellow")
        table.add_column("Avg Latency", justify="right")
        
        total_calls = 0
        total_cost = 0.0
        for layer, data in stats.items():
            avg_latency = data["latency"] / data["calls"] if data["calls"] > 0 else 0
            table.add_row(
                layer.upper(),
                str(data["calls"]),
                f"${data['cost']:.4f}",
                f"{avg_latency:.0f}ms"
            )
            total_calls += data["calls"]
            total_cost += data["cost"]
            
        table.add_row(
            "[bold]TOTAL[/bold]",
            f"[bold]{total_calls}[/bold]",
            f"[bold]${total_cost:.4f}[/bold]",
            "",
            style="bold",
        )
        
        console.print(table)
    except Exception as e:
        console.print(f"[red]Error loading telemetry: {e}[/red]")

def cmd_cost(args: argparse.Namespace) -> None:
    """Show cost report."""
    print_banner()
    console.print("\n[bold]💰 Cost Report[/bold]\n")
    
    try:
        from techtide_swarm.telemetry import get_total_cost
        total = get_total_cost()
        if total == 0.0:
            console.print("[dim]No cost data available yet. Run agents to generate metrics.[/dim]")
        else:
            console.print(f"[bold green]Total Swarm Cost: ${total:.4f}[/bold green]")
    except Exception as e:
        console.print(f"[red]Error loading cost data: {e}[/red]")


def cmd_migrate(args: argparse.Namespace) -> None:
    """Migrate .swarm/topics/ flat files into a Memvid .mv2 store."""
    print_banner()
    console.print("\n[bold]🔄 Migrating flat memory to Memvid .mv2[/bold]\n")

    from techtide_swarm.memory import MemoryManager

    layer = args.layer or "all"
    swarm_root = Path.cwd()
    dest = Path(args.dest) if args.dest else swarm_root / ".swarm" / f"layer-{layer}.mv2"

    mem = MemoryManager(swarm_root=swarm_root)
    result = mem.migrate_flat_to_memvid(dest)

    if result["status"] == "ok":
        console.print(
            f"[bold green]✅ Migrated {result['files_migrated']} topic files → {result['mv2']}[/bold green]"
        )
    else:
        console.print(f"[yellow]⚠️  Skipped: {result.get('reason', 'unknown')}[/yellow]")
        console.print("[dim]Build packages/memvid-swarm-bridge and ensure it is on PATH.[/dim]")


def cmd_boot(args: argparse.Namespace) -> None:
    """Boot all 357 agents — load roster, register budgets, validate soul files."""
    print_banner()
    console.print("\n[bold]⚡ Booting Swarm 357...[/bold]\n")

    config_path = getattr(args, "config", "config/swarm.yaml")

    try:
        import yaml
        from techtide_swarm import Swarm

        if not Path(config_path).is_file():
            console.print(f"[red]Config not found: {config_path}[/red]")
            console.print("[dim]Run 'swarm init' first, then ensure config/swarm.yaml exists.[/dim]")
            sys.exit(1)

        swarm = Swarm.from_config(config_path)
        asyncio.run(swarm.boot())

        raw = yaml.safe_load(Path(config_path).read_text(encoding="utf-8")) or {}
        agents = raw.get("agents", [])
        layer_budgets = raw.get("swarm", {}).get("layer_budgets", {})

        from collections import Counter
        counts = Counter(a["layer"] for a in agents)

        table = Table(
            title="Swarm 357 — Layer Manifest",
            box=box.HEAVY_EDGE,
            show_header=True,
            header_style="bold white on blue",
        )
        table.add_column("Layer", style="bold", min_width=12)
        table.add_column("Agents", justify="center")
        table.add_column("Model", justify="center")
        table.add_column("Daily Budget", justify="right", style="yellow")

        for layer_name in ["management", "sales", "support", "marketing", "seo", "research", "operations"]:
            budget_cfg = layer_budgets.get(layer_name, {})
            table.add_row(
                layer_name.upper(),
                str(counts.get(layer_name, 0)),
                budget_cfg.get("model_preference", "sonnet"),
                f"${budget_cfg.get('daily_limit_usd', 0):.2f}",
            )

        table.add_row(
            "[bold]TOTAL[/bold]",
            f"[bold]{len(agents)}[/bold]",
            "",
            f"[bold]${raw.get('swarm', {}).get('daily_budget_usd', 0):.2f}[/bold]",
            style="bold",
        )

        console.print(table)
        console.print(f"\n[bold green]✅ {len(agents)} agents loaded across 7 layers. Ready.[/bold green]\n")

    except Exception as exc:
        console.print(f"[red]Boot failed: {exc}[/red]")
        sys.exit(1)


def cmd_run(args: argparse.Namespace) -> None:
    """Run a task across the swarm or a single layer."""
    print_banner()

    task = " ".join(args.task) if isinstance(args.task, list) else args.task
    config_path = getattr(args, "config", "config/swarm.yaml")
    layer = getattr(args, "layer", None)
    budget = float(getattr(args, "budget", 25.0))
    max_parallel = int(getattr(args, "max_parallel", 10))

    console.print(f"\n[bold]🚀 Swarm Run[/bold]\n[dim]Task:[/dim] {task[:120]}\n")

    try:
        from techtide_swarm import Swarm

        swarm = Swarm.from_config(config_path)
        asyncio.run(swarm.boot())

        if layer:
            console.print(f"[dim]Layer: {layer} · Budget: ${budget:.2f} · Max parallel: {max_parallel}[/dim]\n")
            results = asyncio.run(swarm.execute_layer(layer, task, budget_usd=budget, max_parallel=max_parallel))

            table = Table(
                title=f"Layer: {layer.upper()}",
                box=box.SIMPLE_HEAD,
                show_header=True,
            )
            table.add_column("Agent", style="cyan", min_width=30)
            table.add_column("Status", justify="center")
            table.add_column("Cost", justify="right", style="yellow")
            table.add_column("ms", justify="right")
            table.add_column("Output Preview", max_width=60)

            total_cost = 0.0
            for r in results:
                status_str = "[green]✓[/green]" if r.status == "success" else (
                    "[dim]—[/dim]" if r.status == "skipped" else "[red]✗[/red]"
                )
                preview = (r.output or r.error or "")[:80].replace("\n", " ")
                table.add_row(
                    r.agent_name or "—",
                    status_str,
                    f"${r.cost_usd:.4f}",
                    str(r.latency_ms),
                    preview,
                )
                total_cost += r.cost_usd

            console.print(table)
            success = sum(1 for r in results if r.status == "success")
            console.print(
                f"\n[bold]Agents run: {len(results)} · Successful: {success} · "
                f"Total cost: [yellow]${total_cost:.4f}[/yellow][/bold]\n"
            )

        else:
            console.print(f"[dim]Budget: ${budget:.2f} · All layers[/dim]\n")

            with Progress(
                SpinnerColumn(),
                TextColumn("[bold blue]{task.description}"),
                TimeElapsedColumn(),
                console=console,
            ) as progress:
                prog_task = progress.add_task("Swarm executing...", total=None)
                result = asyncio.run(swarm.execute(task, budget_usd=budget))
                progress.update(prog_task, description="Done", completed=True)

            console.print(Panel(
                result.final_output[:3000] if result.final_output else "[dim]No output[/dim]",
                title="Swarm Output",
                border_style="green",
            ))
            total_cost = result.total_cost_usd
            console.print(
                f"\n[bold]Agents run: {len(result.agent_results)} · "
                f"Total cost: [yellow]${total_cost:.4f}[/yellow][/bold]\n"
            )

    except Exception as exc:
        console.print(f"[red]Run failed: {exc}[/red]")
        sys.exit(1)


def cmd_dream(args: argparse.Namespace) -> None:
    """Trigger a memory consolidation cycle."""
    print_banner()
    console.print("\n[bold]💤 Dream Cycle — Memory Consolidation[/bold]\n")

    try:
        from techtide_swarm.memory import MemoryManager

        swarm_root = Path.cwd()
        mem = MemoryManager(swarm_root=swarm_root)

        # Load any topic files into interactions so the cycle has something to analyze
        topics_dir = swarm_root / ".swarm" / "topics"
        loaded = 0
        if topics_dir.is_dir():
            import json
            for f in topics_dir.glob("*.json"):
                try:
                    data = json.loads(f.read_text(encoding="utf-8"))
                    mem.log_interaction(
                        agent_id=data.get("from", "unknown"),
                        prompt=data.get("key", f.stem),
                        response=data.get("content", ""),
                    )
                    loaded += 1
                except Exception:
                    pass

        if loaded:
            console.print(f"[dim]Loaded {loaded} topic file(s) into memory.[/dim]")

        report = asyncio.run(mem.run_dream_cycle())

        if isinstance(report, dict):
            dream_num = report.get("dream_number", "?")
            console.print(f"[bold green]Dream cycle #{dream_num} complete.[/bold green]\n")
            for phase, data in report.get("phases", {}).items():
                console.print(f"  [cyan]{phase}:[/cyan] {data}")
            contradictions = report.get("contradictions_found", 0)
            pruned = report.get("pointers_pruned", 0)
            console.print(f"\n  Contradictions found: {contradictions}")
            console.print(f"  Pointers pruned: {pruned}")
        else:
            console.print(f"[dim]{report}[/dim]")

        if getattr(args, "migrate", False):
            console.print("\n[dim]Running migration to Memvid...[/dim]")
            dest = swarm_root / ".swarm" / "layer-all.mv2"
            mig_result = mem.migrate_flat_to_memvid(dest)
            if mig_result["status"] == "ok":
                console.print(f"[green]✅ Migrated {mig_result['files_migrated']} files → {mig_result['mv2']}[/green]")
            else:
                console.print(f"[yellow]Migration skipped: {mig_result.get('reason', 'unknown')}[/yellow]")

    except Exception as exc:
        console.print(f"[red]Dream cycle failed: {exc}[/red]")
        sys.exit(1)


def cmd_plan(args: argparse.Namespace) -> None:
    """ULTRAPLAN: deep Opus planning session."""
    print_banner()

    task = " ".join(args.task) if isinstance(args.task, list) else args.task
    model = getattr(args, "model", "opus")

    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    has_key = bool(api_key) and "your-key" not in api_key

    if not has_key:
        console.print("\n[bold yellow][simulation mode] — no ANTHROPIC_API_KEY set[/bold yellow]")
        console.print("[dim]Set ANTHROPIC_API_KEY for live Opus planning.[/dim]\n")
        console.print(Panel(
            f"[bold]Task:[/bold] {task}\n\n"
            "[stub] Phase 1: Research & Discovery\n"
            "  — Analyze task requirements\n"
            "  — Identify key stakeholders and constraints\n\n"
            "[stub] Phase 2: Strategy Design\n"
            "  — Define objectives and success criteria\n"
            "  — Map dependencies and risks\n\n"
            "[stub] Phase 3: Execution Roadmap\n"
            "  — Break into actionable milestones\n"
            "  — Assign agent layers and resource budget\n\n"
            "[dim][simulation mode — real plan requires ANTHROPIC_API_KEY][/dim]",
            title="ULTRAPLAN (stub)",
            border_style="yellow",
        ))
        return

    console.print("\n[bold green]ULTRAPLAN — Live Opus Planning[/bold green]\n")
    console.print(f"[dim]Task:[/dim] {task[:200]}\n")

    try:
        from techtide_swarm import UltraPlan, UltraPlanConfig

        plan_config = UltraPlanConfig(model=model)

        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            prog_task = progress.add_task(f"Opus planning ({model})...", total=None)
            result = asyncio.run(UltraPlan(plan_config).plan(task))
            progress.update(prog_task, description="Done", completed=True)

        plan_text = result.get("plan", str(result))
        duration = result.get("duration_seconds", 0)
        cost = result.get("cost_usd", 0.0)

        console.print(Panel(plan_text, title="ULTRAPLAN", border_style="green"))
        console.print(f"\n[dim]Duration: {duration:.0f}s · Cost: ${cost:.4f}[/dim]\n")

    except Exception as exc:
        console.print(f"[red]Plan failed: {exc}[/red]")
        sys.exit(1)


def cmd_agent(args: argparse.Namespace) -> None:
    """List agents or inspect/run a specific agent."""
    print_banner()

    config_path = getattr(args, "config", "config/swarm.yaml")
    list_flag = getattr(args, "list", False)
    layer_filter = getattr(args, "layer", None)
    agent_id = getattr(args, "agent_id", None)
    run_task = getattr(args, "run", None)
    info_flag = getattr(args, "info", False)

    try:
        import yaml

        if not Path(config_path).is_file():
            console.print(f"[red]Config not found: {config_path}[/red]")
            sys.exit(1)

        raw = yaml.safe_load(Path(config_path).read_text(encoding="utf-8")) or {}
        agents = raw.get("agents", [])

        if list_flag or (not agent_id and not run_task):
            if layer_filter:
                agents = [a for a in agents if a.get("layer") == layer_filter]

            table = Table(
                title=f"Agents{' — ' + layer_filter.upper() if layer_filter else ' (all 357)'}",
                box=box.SIMPLE_HEAD,
                show_header=True,
            )
            table.add_column("#", justify="right", style="dim", min_width=4)
            table.add_column("Name", style="cyan", min_width=32)
            table.add_column("Layer", min_width=12)
            table.add_column("Role", min_width=20)
            table.add_column("Model", justify="center")

            for i, a in enumerate(agents, 1):
                table.add_row(
                    str(i),
                    a.get("name", ""),
                    a.get("layer", ""),
                    a.get("role", ""),
                    a.get("model", "sonnet"),
                )

            console.print(table)
            console.print(f"\n[dim]{len(agents)} agents listed.[/dim]\n")
            return

        # Find the agent by name/id
        match = next((a for a in agents if a.get("name") == agent_id), None)
        if not match:
            console.print(f"[red]Agent not found: {agent_id}[/red]")
            console.print("[dim]Use 'swarm agent --list' to see all agent names.[/dim]")
            sys.exit(1)

        if info_flag or not run_task:
            console.print(Panel(
                "\n".join(f"  [cyan]{k}:[/cyan] {v}" for k, v in match.items()),
                title=f"Agent: {agent_id}",
                border_style="cyan",
            ))
            return

        # Run the agent
        from techtide_swarm import Agent, AgentConfig
        from techtide_swarm.core.types import LayerType

        layer_type = LayerType(match["layer"])
        cfg = AgentConfig(
            name=match["name"],
            layer=layer_type,
            role=match.get("role", "agent"),
            soul=match.get("soul", ""),
            tools=match.get("tools", []),
            model=match.get("model", "sonnet"),
            budget_limit_usd=float(match.get("budget_usd", 1.0)),
        )

        console.print(f"\n[dim]Running agent:[/dim] {agent_id}\n")

        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            prog_task = progress.add_task(f"{agent_id} working...", total=None)
            result = asyncio.run(Agent(cfg).run(run_task))
            progress.update(prog_task, description="Done", completed=True)

        if result.status == "success":
            console.print(Panel(result.output, title=f"{agent_id} Output", border_style="green"))
        else:
            console.print(f"[red]Error: {result.error}[/red]")

        console.print(f"\n[dim]Cost: ${result.cost_usd:.4f} · Latency: {result.latency_ms}ms[/dim]\n")

    except Exception as exc:
        console.print(f"[red]Agent command failed: {exc}[/red]")
        sys.exit(1)


def cmd_eval(args: argparse.Namespace) -> None:
    """Run the evaluation harness."""
    print_banner()
    console.print("\n[bold]Evaluation Harness[/bold]\n")

    try:
        sys.path.insert(0, str(Path.cwd()))
        # The eval harness lives in the repo's top-level evals/ package, loaded
        # dynamically at runtime (see sys.path.insert above); it is not part of
        # this installable package and has no importable stub at type-check time.
        from evals.run_evals import (  # type: ignore[import-not-found]
            run_all_evals,
            load_baseline,
            compare_to_baseline,
            EVAL_TASKS,
        )

        save = getattr(args, "save_baseline", False)
        use_swarm = getattr(args, "swarm", False)
        do_compare = getattr(args, "compare", False)

        console.print(f"[dim]Tasks: {len(EVAL_TASKS)} · Mode: {'swarm' if use_swarm else 'single-agent'}[/dim]\n")

        results = asyncio.run(run_all_evals(save=save, use_swarm=use_swarm))

        table = Table(
            title="Eval Results",
            box=box.SIMPLE_HEAD,
            show_header=True,
        )
        table.add_column("Task", style="cyan", min_width=12)
        table.add_column("Status", justify="center")
        table.add_column("KW Score", justify="center")
        table.add_column("Length", justify="center")
        table.add_column("Cost", justify="right", style="yellow")
        table.add_column("Latency", justify="right")

        for r in results:
            status_str = "[green]PASS[/green]" if r.status == "success" and r.keyword_score >= 0.5 else "[red]FAIL[/red]"
            kw_color = "green" if r.keyword_score >= 0.7 else ("yellow" if r.keyword_score >= 0.4 else "red")
            table.add_row(
                r.task_id,
                status_str,
                f"[{kw_color}]{r.keyword_score:.2f}[/{kw_color}]",
                "[green]OK[/green]" if r.length_ok else "[red]SHORT[/red]",
                f"${r.cost_usd:.4f}",
                f"{r.latency_ms}ms",
            )

        console.print(table)

        total_cost = sum(r.cost_usd for r in results)
        avg_kw = sum(r.keyword_score for r in results) / len(results) if results else 0
        console.print(f"\n[bold]Avg KW score: {avg_kw:.2f} · Total cost: ${total_cost:.4f}[/bold]")

        if do_compare:
            baseline = load_baseline(Path("evals/baselines"))
            if baseline:
                regressions = compare_to_baseline(results, baseline)
                if regressions:
                    console.print(f"\n[red]REGRESSIONS ({len(regressions)}):[/red]")
                    for reg in regressions:
                        console.print(f"  {reg['task_id']}: {reg['metric']} {reg['baseline']} -> {reg['current']}")
                else:
                    console.print("\n[green]No regressions.[/green]")
            else:
                console.print("\n[yellow]No baseline found. Run with --save-baseline first.[/yellow]")

        console.print()

    except Exception as exc:
        console.print(f"[red]Eval failed: {exc}[/red]")
        sys.exit(1)


def cmd_serve(args: argparse.Namespace) -> None:
    """Start the FastAPI HTTP server."""
    try:
        import uvicorn
    except ImportError:
        print("uvicorn not installed. Run: pip install techtide-swarm")
        sys.exit(1)

    host = getattr(args, "host", "0.0.0.0")
    port = int(getattr(args, "port", 8000))
    reload = getattr(args, "reload", False)

    if HAS_RICH and console:
        console.print(
            f"\n[bold green]🚀 Starting Swarm 357 API server on {host}:{port}[/bold green]"
        )
        console.print("[dim]Press Ctrl+C to stop.[/dim]\n")

    uvicorn.run(
        "techtide_swarm.server:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info",
    )


def cmd_mcp_list(args: argparse.Namespace) -> None:
    """List all configured MCP servers from config/mcp/."""
    import yaml as _yaml
    from pathlib import Path as _Path

    config_dir = getattr(args, "config_dir", "config/mcp")
    config_path = _Path(config_dir)
    all_raw: list[dict[str, Any]] = []
    if config_path.is_dir():
        for f in sorted(config_path.glob("*.yaml")):
            try:
                raw = _yaml.safe_load(f.read_text(encoding="utf-8")) or {}
                all_raw.append(raw)
            except Exception:
                pass

    if not all_raw:
        console.print(f"[yellow]No MCP configs found in {config_dir}/[/yellow]")
        console.print("[dim]Create YAML files in config/mcp/ to add MCP servers.[/dim]")
        return

    enabled_count = sum(1 for r in all_raw if r.get("enabled", True))

    table = Table(
        title=f"MCP Servers ({config_dir})",
        box=box.HEAVY_EDGE,
        show_header=True,
        header_style="bold white on blue",
    )
    table.add_column("Name", style="cyan", min_width=12)
    table.add_column("Transport", justify="center")
    table.add_column("Command / URL", min_width=28)
    table.add_column("Toolset", min_width=16)
    table.add_column("Enabled", justify="center")
    table.add_column("Description", max_width=40)

    for r in all_raw:
        enabled = bool(r.get("enabled", True))
        transport = r.get("transport", "stdio")
        if transport == "http":
            cmd_url = r.get("url", "")
        else:
            cmd_parts = [r.get("command", "")] + [str(a) for a in r.get("args", [])]
            cmd_url = " ".join(cmd_parts)[:40]
        table.add_row(
            r.get("name", ""),
            transport,
            cmd_url,
            r.get("toolset", "core_tools"),
            "[green]yes[/green]" if enabled else "[dim]no[/dim]",
            r.get("description", "")[:40],
        )

    console.print(table)
    console.print(
        f"\n[dim]{len(all_raw)} server(s) configured \u00b7 {enabled_count} enabled[/dim]"
    )
    console.print(
        "[dim]Run [bold]swarm mcp connect <name>[/bold] to connect and register tools.[/dim]\n"
    )


def cmd_mcp_connect(args: argparse.Namespace) -> None:
    """Connect to an MCP server and show which tools were registered."""
    import yaml as _yaml
    from pathlib import Path as _Path
    from techtide_swarm.tools.mcp import MCPServerConfig, mcp_registry

    server_name: str = args.server
    config_dir = getattr(args, "config_dir", "config/mcp")
    config_path = _Path(config_dir) / f"{server_name}.yaml"

    if not config_path.exists():
        console.print(f"[red]Config not found: {config_path}[/red]")
        console.print("[dim]Available configs:[/dim]")
        for f in sorted(_Path(config_dir).glob("*.yaml")):
            console.print(f"  {f.stem}")
        sys.exit(1)

    raw = _yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    cfg = MCPServerConfig(
        name=raw.get("name", server_name),
        description=raw.get("description", ""),
        transport=raw.get("transport", "stdio"),
        command=raw.get("command", ""),
        args=tuple(str(a) for a in raw.get("args", [])),
        env={str(k): str(v) for k, v in raw.get("env", {}).items()},
        url=raw.get("url", ""),
        headers={str(k): str(v) for k, v in raw.get("headers", {}).items()},
        toolset=raw.get("toolset", "core_tools"),
        enabled=True,  # force-enable for direct connect
    )

    console.print(f"\n[bold]Connecting to MCP server:[/bold] [cyan]{cfg.name}[/cyan]")
    if cfg.transport == "http":
        console.print(f"[dim]Transport: http \u00b7 URL: {cfg.url}[/dim]\n")
    else:
        cmd_str = " ".join([cfg.command] + list(cfg.args))
        console.print(f"[dim]Transport: stdio \u00b7 Command: {cmd_str}[/dim]\n")

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]Connecting..."),
            TimeElapsedColumn(),
            console=console,
            transient=True,
        ) as progress:
            progress.add_task("", total=None)
            registered = mcp_registry.connect(cfg)

        console.print(f"[bold green]\u2705 Connected \u2014 {len(registered)} tool(s) registered:[/bold green]\n")
        for t in registered:
            console.print(f"  [cyan]{t}[/cyan]")
        console.print(
            "\n[dim]Add these names to agent 'tools:' lists in swarm config or soul templates.[/dim]\n"
        )
    except RuntimeError as exc:
        console.print(f"[red]Connection failed: {exc}[/red]")
        console.print("[dim]Check that the MCP server binary is installed and env vars are set.[/dim]")
        sys.exit(1)


def cmd_mcp(args: argparse.Namespace) -> None:
    """MCP server management dispatcher."""
    print_banner()
    mcp_command = getattr(args, "mcp_command", None)
    if mcp_command == "list":
        cmd_mcp_list(args)
    elif mcp_command == "connect":
        cmd_mcp_connect(args)
    else:
        console.print("[yellow]Usage: swarm mcp list | swarm mcp connect <server>[/yellow]")


# ──────────────────────────────────────────────
# Main Entry Point
# ──────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        prog="swarm",
        description="TechTide Swarm 357 — 357 Claude AI Agents, One Swarm",
    )
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("init", help="Initialize a new swarm project")
    subparsers.add_parser("demo", help="Run the 60-second demo")
    subparsers.add_parser("status", help="Show swarm health dashboard")
    subparsers.add_parser("cost", help="Show cost report")

    run_parser = subparsers.add_parser("run", help="Run a task across the swarm")
    run_parser.add_argument("task", nargs="+", help="The task to execute")
    run_parser.add_argument("--layer", default=None, help="Route to a single layer")
    run_parser.add_argument("--budget", type=float, default=25.0, help="Budget in USD (default: 25.0)")
    run_parser.add_argument("--config", default="config/swarm.yaml")
    run_parser.add_argument("--max-parallel", type=int, default=10, dest="max_parallel")

    boot_parser = subparsers.add_parser("boot", help="Boot all 357 agents")
    boot_parser.add_argument("--config", default="config/swarm.yaml")

    agent_parser = subparsers.add_parser("agent", help="List or inspect/run agents")
    agent_parser.add_argument("agent_id", nargs="?", default=None, help="Agent name to inspect or run")
    agent_parser.add_argument("--list", action="store_true", help="List all agents")
    agent_parser.add_argument("--layer", default=None, help="Filter by layer when listing")
    agent_parser.add_argument("--run", default=None, metavar="TASK", help="Run this agent on a task")
    agent_parser.add_argument("--info", action="store_true", help="Show agent config")
    agent_parser.add_argument("--config", default="config/swarm.yaml")

    dream_parser = subparsers.add_parser("dream", help="Trigger memory consolidation")
    dream_parser.add_argument("--migrate", action="store_true", help="Also migrate flat files to Memvid .mv2")
    dream_parser.add_argument("--topic-dir", default=None, dest="topic_dir")

    plan_parser = subparsers.add_parser("plan", help="ULTRAPLAN deep planning session")
    plan_parser.add_argument("task", nargs="+")
    plan_parser.add_argument("--model", default="opus")

    migrate_parser = subparsers.add_parser("migrate", help="Migrate .swarm/topics/ to Memvid .mv2")
    migrate_parser.add_argument("--layer", default=None, help="Layer name (default: all)")
    migrate_parser.add_argument("--dest", default=None, help="Destination .mv2 path")

    eval_parser = subparsers.add_parser("eval", help="Run evaluation harness")
    eval_parser.add_argument("--save-baseline", action="store_true", dest="save_baseline",
                             help="Save results as new baseline")
    eval_parser.add_argument("--swarm", action="store_true", help="Run through full swarm pipeline")
    eval_parser.add_argument("--compare", action="store_true", help="Compare against saved baseline")

    serve_parser = subparsers.add_parser("serve", help="Start the HTTP API server")
    serve_parser.add_argument("--host", default="0.0.0.0", help="Bind host (default: 0.0.0.0)")
    serve_parser.add_argument("--port", type=int, default=8000, help="Bind port (default: 8000)")
    serve_parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")

    mcp_parser = subparsers.add_parser("mcp", help="MCP server management")
    mcp_sub = mcp_parser.add_subparsers(dest="mcp_command")

    mcp_list_p = mcp_sub.add_parser("list", help="List configured MCP servers")
    mcp_list_p.add_argument(
        "--config-dir", default="config/mcp", dest="config_dir",
        help="Directory with MCP YAML configs (default: config/mcp)",
    )

    mcp_conn_p = mcp_sub.add_parser("connect", help="Connect to an MCP server")
    mcp_conn_p.add_argument("server", help="Server name (matches config/mcp/<name>.yaml)")
    mcp_conn_p.add_argument(
        "--config-dir", default="config/mcp", dest="config_dir",
        help="Directory with MCP YAML configs (default: config/mcp)",
    )

    args = parser.parse_args()

    if not HAS_RICH:
        print("Install 'rich' for the best experience: pip install rich")

    if args.command == "init":
        cmd_init(args)
    elif args.command == "demo":
        cmd_demo(args)
    elif args.command == "status":
        cmd_status(args)
    elif args.command == "cost":
        cmd_cost(args)
    elif args.command == "run":
        cmd_run(args)
    elif args.command == "boot":
        cmd_boot(args)
    elif args.command == "agent":
        cmd_agent(args)
    elif args.command == "dream":
        cmd_dream(args)
    elif args.command == "plan":
        cmd_plan(args)
    elif args.command == "migrate":
        cmd_migrate(args)
    elif args.command == "eval":
        cmd_eval(args)
    elif args.command == "serve":
        cmd_serve(args)
    elif args.command == "mcp":
        cmd_mcp(args)
    elif args.command is None:
        print_banner()
        parser.print_help()


if __name__ == "__main__":
    main()
