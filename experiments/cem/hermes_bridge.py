"""Bridge to the *real* Hermes Agent memory implementation.

We import `tools.memory_tool` / `tools.memory_tool_store` and
`agent.prompt_builder.build_memory_guidance` straight from the pinned
hermes-agent checkout (third_party/hermes-agent, commit recorded in
docs/environment.md), so budget accounting, the '§' entry format, overflow
errors and the tool schema are exactly what a Hermes user gets.
"""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

HERMES_DIR = Path(__file__).resolve().parents[2] / "third_party" / "hermes-agent"
_TMP_HOME = Path(tempfile.mkdtemp(prefix="hermes_home_"))
os.environ.setdefault("HERMES_HOME", str(_TMP_HOME))
if str(HERMES_DIR) not in sys.path:
    sys.path.insert(0, str(HERMES_DIR))

from tools.memory_tool_store import ENTRY_DELIMITER, MemoryStore  # noqa: E402
from tools.memory_tool import MEMORY_SCHEMA, memory_tool  # noqa: E402
from tools.memory_tool_store import _scan_memory_content  # noqa: E402

try:  # the prompt builder pulls in more of the agent; fall back to the verbatim text
    from agent.prompt_builder import build_memory_guidance  # noqa: E402
    MEMORY_GUIDANCE = build_memory_guidance(True, False, skill_manage_available=False)
except Exception:  # pragma: no cover
    MEMORY_GUIDANCE = None


def fresh_store(limit: int) -> MemoryStore:
    """A MemoryStore whose files live in a private, empty HERMES_HOME."""
    home = Path(tempfile.mkdtemp(prefix="hermes_home_"))
    os.environ["HERMES_HOME"] = str(home)
    store = MemoryStore(memory_char_limit=limit, user_char_limit=1375)
    store.load_from_disk()
    return store


def char_count(entries: list[str]) -> int:
    return len(ENTRY_DELIMITER.join(entries))


def render_block(entries: list[str], limit: int) -> str:
    """Exactly the block Hermes injects into the system prompt."""
    s = MemoryStore(memory_char_limit=limit, user_char_limit=1375)
    return s._render_block("memory", list(entries)) or "(memory is empty)"


def fit_entries(entries: list[str], limit: int) -> list[str]:
    """Keep leading entries that fit; cut the first overflowing entry at a sentence/clause
    boundary so that a single long line is truncated, not dropped."""
    out: list[str] = []
    for e in entries:
        if char_count(out + [e]) <= limit:
            out.append(e)
            continue
        room = limit - char_count(out) - (len(ENTRY_DELIMITER) if out else 0)
        if room > 30:
            cut = e[:room]
            b = max(cut.rfind(". "), cut.rfind("; "), cut.rfind(" | "), cut.rfind(", "))
            if b > room * 0.5:
                cut = cut[:b + 1]
            out.append(cut.rstrip())
        break
    return out


TOOL_SPEC = {"type": "function", "function": {
    "name": MEMORY_SCHEMA["name"], "description": MEMORY_SCHEMA["description"],
    "parameters": MEMORY_SCHEMA["parameters"]}}
