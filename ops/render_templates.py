#!/usr/bin/env python3
"""Render IconMineMods compliance templates with the real legal/domain identity.

Reads ops/secrets.json (gitignored) if present, else environment variables,
else ops/secrets.example.json placeholders. Substitutes identity tokens in
compliance/templates/* and writes finalized copies to ops/rendered/.
Idempotent. This is how the SAME CNPJ/legal entity feeds both the Bedrock
W-8BEN-E (Microsoft) and the Roblox payout profile.

Tokens replaced: <SEU_CNPJ>, <XX.XXX.XXX/XXXX-XX>, <razao_social>,
<seu nome legal / razão social do MEI>, <data>, <AAAA-MM-DD>,
bussins@iconMine.tech, iconmine.tech, iconMine.tech, https://iconmine.tech.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SECRETS = ROOT / "ops" / "secrets.json"
EXAMPLE = ROOT / "ops" / "secrets.example.json"
TPL_DIR = ROOT / "compliance" / "templates"
OUT = ROOT / "ops" / "rendered"

TEMPLATES = ["privacy-policy.md", "w8ben.md", "terms-of-use.md", "store-listing.md"]


def load_cfg() -> dict:
    cfg: dict = {}
    for p in (SECRETS, EXAMPLE):
        if p.exists():
            try:
                cfg = json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                pass
            if p == SECRETS:
                break
    if os.environ.get("ICONMINEMODS_CNPJ"):
        cfg.setdefault("legal", {})["cnpj"] = os.environ["ICONMINEMODS_CNPJ"]
    return cfg


def vals(cfg: dict) -> dict:
    legal = cfg.get("legal", {})
    dom = cfg.get("domain", {})
    privacy = dom.get("privacy_url", "https://iconminemods.dpdns.org/privacy")
    host = privacy.split("//", 1)[-1].split("/", 1)[0]
    site = "https://" + host
    email = legal.get("email", "contato@iconminemods.dpdns.org")
    return {
        "<SEU_CNPJ>": legal.get("cnpj", "<SEU_CNPJ>"),
        "<XX.XXX.XXX/XXXX-XX>": legal.get("cnpj", "<XX.XXX.XXX/XXXX-XX>"),
        "<razao_social>": legal.get("razao_social", "<razao_social>"),
        "<seu nome legal / razão social do MEI>": legal.get("razao_social", "<razao_social>"),
        "<data>": "<AAAA-MM-DD>",
        "<AAAA-MM-DD>": legal.get("data_nascimento", "<AAAA-MM-DD>"),
        "bussins@iconMine.tech": email,
        "iconMine.tech": host,
        "iconmine.tech": host,
        "https://iconmine.tech": site,
    }


def main() -> int:
    cfg = load_cfg()
    v = vals(cfg)
    OUT.mkdir(parents=True, exist_ok=True)
    warnings = []
    if v["<SEU_CNPJ>"] == "<SEU_CNPJ>":
        warnings.append("CNPJ not set - placeholders left in rendered files. "
                        "Add ops/secrets.json or ICONMINEMODS_CNPJ env.")
    for tpl in TEMPLATES:
        src = TPL_DIR / tpl
        if not src.exists():
            continue
        txt = src.read_text(encoding="utf-8")
        for k, val in v.items():
            txt = txt.replace(k, val)
        out = OUT / tpl
        out.write_text(txt, encoding="utf-8")
        print(f"rendered {tpl} -> {out}")
    for w in warnings:
        print("WARN:", w)
    print("done")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
