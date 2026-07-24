"""TechTide Swarm 357 — public API."""

from importlib.metadata import PackageNotFoundError, version

from techtide_swarm.agent import Agent, AgentConfig, AgentResult
from techtide_swarm.bash_gate import BashSecurityGate
from techtide_swarm.memory import MemoryManager
from techtide_swarm.memvid_bridge import MemvidBridge, MemvidBridgeError, resolve_bridge_binary
from techtide_swarm.persistence import SwarmStore
from techtide_swarm.swarm import CostController, Swarm, SwarmExecutionResult
from techtide_swarm.tools.registry import TOOLSET_MAP, ToolRegistry, registry
from techtide_swarm.ultra_plan import UltraPlan, UltraPlanConfig

try:
    __version__ = version("techtide-swarm")
except PackageNotFoundError:  # pragma: no cover — editable / source tree
    __version__ = "0.2.0"

__all__ = [
    "Agent",
    "AgentConfig",
    "AgentResult",
    "BashSecurityGate",
    "CostController",
    "MemvidBridge",
    "MemvidBridgeError",
    "MemoryManager",
    "Swarm",
    "SwarmExecutionResult",
    "SwarmStore",
    "TOOLSET_MAP",
    "ToolRegistry",
    "UltraPlan",
    "UltraPlanConfig",
    "__version__",
    "registry",
    "resolve_bridge_binary",
]
