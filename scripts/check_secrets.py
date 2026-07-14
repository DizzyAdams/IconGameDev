#!/usr/bin/env python3
"""Minimal, stdlib-only secret/token pattern scanner.

Usage:
    python scripts/check_secrets.py            # scan repo (respects .gitignore)
    python scripts/check_secrets.py --strict   # also fail if git repo is missing

What it does:
  1. Confirms the 4 known secret files (.env, keyroblox.env, ROBLOX_CONFIG.env,
     ops/secrets.json) are NOT tracked by git (via `git ls-files`).
  2. Greps tracked / non-ignored text files for common secret/token patterns
     (Vercel, AWS, GitHub, Slack, Stripe, GCP, GitLab, JWT, private keys,
     generic secret assignments).

Exit code: 0 = clean, 1 = secrets found / tracked secret files detected.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Files that must NEVER be committed.
FORBIDDEN_TRACKED = [
    ".env",
    "keyroblox.env",
    "ROBLOX_CONFIG.env",
    "ops/secrets.json",
]

# Skip heavy / tooling / build directories when walking the tree.
SKIP_DIRS = {
    ".git", ".codegraph", ".omo", ".opencode", ".agents",
    "node_modules", ".next", "__pycache__", "_ip_quarantine",
    "arq_zip", "dist", "out", ".venv", "bedrock_master",
    "analytics_data", "audit", "website-next", "website",
    "marketplace-content", "submission_mcpacks",
}

# Skip files larger than this (likely binaries / generated blobs).
MAX_FILE_BYTES = 512 * 1024

TEXT_EXT = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".json", ".yaml", ".yml",
    ".toml", ".md", ".txt", ".env", ".sh", ".ps1", ".bat", ".cfg",
    ".ini", ".html", ".css", ".sql", ".xml", ".csv", ".lock",
}

# Secret/token patterns. Kept simple on purpose (grep-like, no entropy math).
PATTERNS = [
    ("vercel_token", re.compile(r"(?i)vercel[_\-]?token\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{20,}")),
    ("aws_key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("github_token", re.compile(r"\b(ghp|gho|ghu|ghs|ghr)_[0-9A-Za-z]{36}\b")),
    ("slack_token", re.compile(r"\bxox[baprs]-[0-9A-Za-z-]{10,}\b")),
    ("stripe_key", re.compile(r"\b(sk|rk)_(live|test)_[0-9A-Za-z]{16,}\b")),
    ("gcp_key", re.compile(r"\bAIza[0-9A-Za-z_\-]{35}\b")),
    ("gitlab_token", re.compile(r"\bglpat-[0-9A-Za-z_\-]{20,}\b")),
    ("private_key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA |PGP )?PRIVATE KEY-----")),
    ("jwt", re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}")),
    ("secret_assignment", re.compile(
        r"(?i)\b(password|passwd|secret|token|api[_-]?key|access[_-]?key|"
        r"private[_-]?key|client[_-]?secret)\b\s*[:=]\s*['\"][^'\"]{8,}['\"]")),
]

PLACEHOLDER_HINTS = ("<", ">", "xxx", "your-", "changeme", "todo", "example", "placeholder")


def is_repo() -> bool:
    try:
        subprocess.run(["git", "rev-parse", "--is-inside-work-tree"],
                       cwd=ROOT, capture_output=True, check=True)
        return True
    except Exception:
        return False


def git_check_ignore(path: str) -> bool:
    try:
        r = subprocess.run(["git", "check-ignore", "-q", path],
                           cwd=ROOT, capture_output=True)
        return r.returncode == 0
    except Exception:
        return False


def git_ls_files() -> set[str]:
    try:
        out = subprocess.run(["git", "ls-files"], cwd=ROOT,
                             capture_output=True, text=True, check=True).stdout
        return {line.strip() for line in out.splitlines() if line.strip()}
    except Exception:
        return set()


def is_placeholder(value: str) -> bool:
    low = value.lower()
    return any(h in low for h in PLACEHOLDER_HINTS)


def scan_file(path: str) -> list[tuple[str, int, str]]:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as fh:
            text = fh.read()
    except Exception:
        return []
    hits = []
    for name, rx in PATTERNS:
        for m in rx.finditer(text):
            snippet = m.group(0)
            if name == "secret_assignment":
                # Strip trailing quote to inspect the value for placeholders.
                val = snippet.rsplit("=", 1)[-1].strip().strip("'\"")
                if is_placeholder(val):
                    continue
            line_no = text.count("\n", 0, m.start()) + 1
            hits.append((name, line_no, snippet))
    return hits


def main() -> int:
    problems: list[str] = []
    repo = is_repo()

    if repo:
        tracked = git_ls_files()
        for f in FORBIDDEN_TRACKED:
            if f in tracked:
                problems.append(f"[TRACKED] secret file is committed: {f}")
    else:
        print("! Not a git repository. Skipping `git ls-files` tracked-file check.")
        print("  Run `git init` then re-run this check before the first commit.")
        if "--strict" in sys.argv:
            problems.append("[CONFIG] not a git repository (--strict)")

    scanned = 0
    for dirpath, dirnames, filenames in os.walk(ROOT):
        rel_dir = os.path.relpath(dirpath, ROOT)
        parts = [] if rel_dir == "." else rel_dir.split(os.sep)
        # Skip hidden dot-directories and known heavy dirs entirely.
        dirnames[:] = [d for d in dirnames
                       if not d.startswith(".") and d not in SKIP_DIRS]
        if any(p in SKIP_DIRS for p in parts):
            dirnames[:] = []
            continue
        for fn in filenames:
            ext = os.path.splitext(fn)[1].lower()
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, ROOT)
            if repo and git_check_ignore(rel):
                continue
            if ext not in TEXT_EXT:
                continue
            try:
                if os.path.getsize(full) > MAX_FILE_BYTES:
                    continue
            except OSError:
                continue
            scanned += 1
            for name, line_no, snippet in scan_file(full):
                problems.append(
                    f"[SECRET:{name}] {rel}:{line_no}: {snippet[:80]}")

    print(f"Scanned {scanned} text files.")
    if problems:
        print("\nFAILED — potential secrets detected:")
        for p in problems:
            print("  " + p)
        return 1
    print("OK — no tracked secret files and no token patterns found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
