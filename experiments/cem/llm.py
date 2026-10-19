"""Thin Ollama /api/chat client with on-disk caching and usage accounting.

All experiments run local models on one RTX 3060 (12 GB) through Ollama.
Decoding is deterministic (temperature 0, fixed seed) and thinking is disabled
so that every method gets the same, cheap generation regime.
"""
from __future__ import annotations

import hashlib
import json
import os
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import requests

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434")


@dataclass
class Usage:
    calls: int = 0
    prompt_tokens: int = 0
    gen_tokens: int = 0
    seconds: float = 0.0
    cache_hits: int = 0

    def add(self, other: "Usage") -> None:
        self.calls += other.calls
        self.prompt_tokens += other.prompt_tokens
        self.gen_tokens += other.gen_tokens
        self.seconds += other.seconds
        self.cache_hits += other.cache_hits

    def as_dict(self) -> dict[str, Any]:
        return dict(calls=self.calls, prompt_tokens=self.prompt_tokens,
                    gen_tokens=self.gen_tokens, seconds=round(self.seconds, 2),
                    cache_hits=self.cache_hits)


@dataclass
class LLM:
    model: str
    num_ctx: int = 16384
    seed: int = 0
    cache_dir: Path | None = None
    timeout: int = 600
    usage: Usage = field(default_factory=Usage)
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    def chat(self, messages: list[dict[str, Any]], *, tools: list[dict] | None = None,
             fmt: dict | str | None = None, max_tokens: int = 1024,
             usage: Usage | None = None, extra_options: dict | None = None) -> dict[str, Any]:
        """Return the assistant message dict ({'content', 'tool_calls'?})."""
        options = {"temperature": 0, "top_k": 1, "top_p": 1.0, "seed": self.seed,
                   "num_ctx": self.num_ctx, "num_predict": max_tokens,
                   "presence_penalty": 0, "repeat_penalty": 1.0}
        options.update(extra_options or {})
        body: dict[str, Any] = {"model": self.model, "messages": messages, "stream": False,
                                "think": False, "options": options, "keep_alive": "30m"}
        if tools:
            body["tools"] = tools
        if fmt is not None:
            body["format"] = fmt
        key = hashlib.sha256(json.dumps(body, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
        cpath = self.cache_dir / key[:2] / f"{key}.json" if self.cache_dir else None
        if cpath and cpath.exists():
            data = json.loads(cpath.read_text())
            u = Usage(calls=1, prompt_tokens=data.get("prompt_eval_count", 0),
                      gen_tokens=data.get("eval_count", 0),
                      seconds=data.get("total_duration", 0) / 1e9, cache_hits=1)
        else:
            t0 = time.time()
            for attempt in range(4):
                try:
                    r = requests.post(f"{OLLAMA_URL}/api/chat", json=body, timeout=self.timeout)
                    r.raise_for_status()
                    data = r.json()
                    break
                except Exception:
                    if attempt == 3:
                        raise
                    time.sleep(3 * (attempt + 1))
            u = Usage(calls=1, prompt_tokens=data.get("prompt_eval_count", 0),
                      gen_tokens=data.get("eval_count", 0), seconds=time.time() - t0)
            if cpath:
                cpath.parent.mkdir(parents=True, exist_ok=True)
                cpath.write_text(json.dumps(data, ensure_ascii=False))
        with self._lock:
            self.usage.add(u)
            if usage is not None:
                usage.add(u)
        if data.get("prompt_eval_count", 0) >= self.num_ctx - 8 and not data.get("_warned"):
            print(f"WARNING: prompt filled num_ctx={self.num_ctx} (possible truncation)", flush=True)
        msg = dict(data.get("message", {}) or {})
        msg.setdefault("content", "")
        msg["_prompt_tokens"] = data.get("prompt_eval_count", 0)
        msg["_gen_tokens"] = data.get("eval_count", 0)
        return msg
