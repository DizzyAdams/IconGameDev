#!/usr/bin/env python3
"""Ecosystem dominance dashboard watchdog.

Aggregates the per-loop .loops/*.md state into one short status line so the
user (and other loops) can see platform progress at a glance. Read-only:
does NOT create, edit, or submit anything.

Run by cron (no_agent) every 6h. Prints nothing when nothing changed and not
Monday (watchdog silence). Always appends a dated weekly summary.

Source of truth: the .loops/*.md files written by the operational loops.
"""
import os
from pathlib import Path
from datetime import datetime, timezone

# Cron copies this file to ~/.hermes/scripts/, so __file__ is not reliable.
# Pin the project root explicitly.
HERE = Path(r"C:\Users\forrydev\Desktop\IconGameDev")
LOOPS = HERE / ".loops"


def read_state() -> dict:
    state = {}
    for f in LOOPS.glob("*.md"):
        if f.name == "README.md":
            continue
        try:
            state[f.stem] = f.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            pass
    return state


def main() -> int:
    if not LOOPS.exists():
        return 0
    state = read_state()
    now = datetime.now(timezone.utc)
    lines = [f"## ecosystem-status {now.date()}"]
    # crude but faithful extraction: last non-empty line of each state file
    for key in ["certify", "volume", "catalog", "submission", "ip-watch",
                "revenue", "funnel", "agency", "seo", "submissions", "payout"]:
        if key in state:
            body = [ln.strip() for ln in state[key].splitlines() if ln.strip()]
            last = body[-1] if body else "(empty)"
            lines.append(f"- {key}: {last[:200]}")
    summary = "\n".join(lines)

    # decide whether to write: changed since last, or Monday weekly
    stamp = LOOPS / "ecosystem-status.last"
    prev = stamp.read_text(encoding="utf-8", errors="ignore") if stamp.exists() else ""
    is_monday = now.weekday() == 0
    if summary == prev and not is_monday:
        return 0  # silent no-op
    stamp.write_text(summary, encoding="utf-8")
    log = LOOPS / "ecosystem-status.md"
    with log.open("a", encoding="utf-8") as fh:
        fh.write(summary + "\n\n")
    print(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
