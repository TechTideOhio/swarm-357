"""Cross-agent memory: flat `.swarm/` store and optional Memvid `.mv2`."""

from __future__ import annotations

import json
import logging
import os
import re
from pathlib import Path
from typing import Any

from techtide_swarm.memvid_bridge import MemvidBridge, MemvidBridgeError, resolve_bridge_binary
from techtide_swarm.persistence import store

logger = logging.getLogger(__name__)
_bridge_unavailable_warned = False


class MemoryManager:
    """
    Share knowledge between agents.

    - Default: in-memory + optional `.swarm/topics` JSONL-style persistence.
    - Memvid: set `memvid_path` to a `.mv2` file and ensure `memvid-swarm-bridge` is on PATH
      or `MEMVID_SWARM_BRIDGE` is set.
    """

    def __init__(
        self,
        *,
        swarm_root: Path | None = None,
        memvid_path: Path | None = None,
    ) -> None:
        self.swarm_root = swarm_root or Path.cwd()
        self._topics = self.swarm_root / ".swarm" / "topics"
        self._topics.mkdir(parents=True, exist_ok=True)
        self._shared: list[dict[str, Any]] = []
        self._interactions: list[dict[str, str]] = []
        self._memvid: MemvidBridge | None = None
        if memvid_path is not None:
            self._memvid = MemvidBridge(memvid_path)
            if self._memvid.available and not memvid_path.exists():
                self._memvid.create()
            elif not self._memvid.available:
                global _bridge_unavailable_warned
                if not _bridge_unavailable_warned:
                    logger.warning(
                        "Memvid bridge unavailable (set MEMVID_SWARM_BRIDGE or PATH); "
                        "falling back to flat .swarm/topics memory"
                    )
                    _bridge_unavailable_warned = True

    def share(
        self,
        *,
        from_agent: str,
        to_agent: str,
        key: str,
        content: str,
    ) -> None:
        entry = {
            "from": from_agent,
            "to": to_agent,
            "key": key,
            "content": content,
        }
        self._shared.append(entry)
        topic_file = self._topics / f"{self._safe_key(key)}.json"
        topic_file.write_text(json.dumps(entry, indent=2), encoding="utf-8")
        store.store_memory(
            from_agent=from_agent,
            to_agent=to_agent,
            key=key,
            content=content,
        )
        if self._memvid and self._memvid.available:
            uri = f"swarm://{key}"
            title = f"{from_agent}->{to_agent}"
            body = f"{content}\n\nmeta: {json.dumps(entry)}".encode("utf-8")
            try:
                self._memvid.put(uri=uri, title=title, body=body)
            except MemvidBridgeError as exc:
                logger.warning("Memvid put failed for key=%s: %s", key, exc)

    def recall(self, agent_id: str, query: str) -> list[dict[str, Any]]:
        q = query.lower()
        out: list[dict[str, Any]] = []
        for e in self._shared:
            if e["to"] != agent_id and e["from"] != agent_id:  # noqa: SIM108
                continue
            blob = f"{e['key']} {e['content']}".lower()
            if q in blob:
                out.append(
                    {
                        "key": e["key"],
                        "content": e["content"],
                        "confidence": 0.9,
                        "note": "matched shared memory",
                    }
                )
        if store.enabled:
            out.extend(store.recall_memory(query=query, agent_id=agent_id, top_k=5))
        if self._memvid and self._memvid.available:
            try:
                raw = self._memvid.search(query, top_k=5)
                for hit in raw.get("hits", [])[:5]:
                    text = hit.get("text") or hit.get("chunk_text") or ""
                    out.append(
                        {
                            "key": hit.get("uri", "memvid"),
                            "content": text[:2000],
                            "confidence": float(hit.get("score") or 0.5),
                            "note": "memvid search",
                        }
                    )
            except MemvidBridgeError as exc:
                logger.warning("Memvid search failed for query=%r: %s", query, exc)
        return out

    def log_interaction(self, agent_id: str, prompt: str, response: str) -> None:
        self._interactions.append(
            {"agent": agent_id, "prompt": prompt, "response": response},
        )

    async def run_dream_cycle(self) -> dict[str, Any]:
        """Consolidate memory: detect contradictions and prune duplicates.

        Uses simple string-overlap heuristics.  A future version can use
        LLM-as-judge for deeper semantic analysis.
        """
        contradictions: list[dict[str, Any]] = []
        duplicates: list[str] = []
        seen_keys: dict[str, str] = {}

        for entry in self._shared:
            key = entry["key"]
            content = entry["content"]
            if key in seen_keys:
                prev = seen_keys[key]
                if prev.strip().lower() != content.strip().lower():
                    contradictions.append({
                        "key": key,
                        "value_a": prev[:200],
                        "value_b": content[:200],
                    })
                else:
                    duplicates.append(key)
            seen_keys[key] = content

        for interaction in self._interactions:
            prompt_norm = interaction["prompt"].strip().lower()
            response = interaction["response"]
            for other in self._interactions:
                if other is interaction:
                    continue
                if other["prompt"].strip().lower() == prompt_norm:
                    if other["response"].strip().lower() != response.strip().lower():
                        contradictions.append({
                            "key": f"interaction:{prompt_norm[:80]}",
                            "value_a": response[:200],
                            "value_b": other["response"][:200],
                        })

        unique_contradictions: list[dict[str, Any]] = []
        seen_pairs: set[tuple[str, str]] = set()
        for c in contradictions:
            pair = (c["key"], c["value_a"])
            if pair not in seen_pairs:
                seen_pairs.add(pair)
                unique_contradictions.append(c)

        llm_notes: list[str] = []
        if (
            os.getenv("SWARM_DREAM_USE_LLM", "").lower() in ("1", "true", "yes")
            and unique_contradictions
        ):
            from techtide_swarm.llm import create_async_client, model_id, resolve_api_key

            key = resolve_api_key()
            if key:
                try:
                    client = create_async_client()
                    model = os.getenv("SWARM_DREAM_LLM_MODEL") or model_id("haiku")
                    brief = json.dumps(unique_contradictions[:5])[:8000]
                    msg = await client.messages.create(
                        model=model,
                        max_tokens=400,
                        messages=[
                            {
                                "role": "user",
                                "content": (
                                    "Given these potential memory contradictions (JSON), "
                                    "list 1-3 concise remediation bullets. Plain text only.\n"
                                    f"{brief}"
                                ),
                            }
                        ],
                    )
                    for block in msg.content:
                        if getattr(block, "type", None) == "text":
                            llm_notes.append(getattr(block, "text", "")[:2000])
                except Exception:
                    llm_notes.append("(llm dream assist skipped)")

        out: dict[str, Any] = {
            "status": "ok",
            "contradictions_found": len(unique_contradictions),
            "contradictions": unique_contradictions,
            "duplicates_found": len(duplicates),
            "total_entries": len(self._shared),
            "total_interactions": len(self._interactions),
        }
        if llm_notes:
            out["llm_remediation_notes"] = llm_notes
        return out

    def migrate_flat_to_memvid(self, dest: Path) -> dict[str, Any]:
        """Copy `.swarm/topics/*.json` into a new `.mv2` via the bridge."""
        bridge = MemvidBridge(dest)
        if not bridge.available:
            return {"status": "skipped", "reason": "memvid-swarm-bridge not available"}
        if not dest.exists():
            bridge.create()
        count = 0
        for fp in sorted(self._topics.glob("*.json")):
            data = json.loads(fp.read_text(encoding="utf-8"))
            key = data.get("key", fp.stem)
            uri = f"swarm://{key}"
            bridge.put(
                uri=uri,
                title=str(data.get("from", "unknown")),
                body=json.dumps(data).encode("utf-8"),
            )
            count += 1
        return {"status": "ok", "files_migrated": count, "mv2": str(dest)}

    @staticmethod
    def _safe_key(key: str) -> str:
        return re.sub(r"[^a-zA-Z0-9_.-]+", "_", key)[:120]

    @classmethod
    def for_layer(
        cls,
        layer: str,
        *,
        swarm_root: Path | None = None,
        use_memvid: bool = True,
    ) -> "MemoryManager":
        """Factory: one MemoryManager per business layer with optional .mv2 backing."""
        root = swarm_root or Path.cwd()
        mv2 = root / ".swarm" / f"layer-{layer}.mv2" if use_memvid else None
        return cls(swarm_root=root, memvid_path=mv2)


__all__ = ["MemoryManager", "MemvidBridge", "MemvidBridgeError", "resolve_bridge_binary"]
