#!/usr/bin/env python3
"""
IconMineMods — Landing Page Generator
======================================
Generates static HTML landing pages for each affiliate.
Pages are saved to website-next/public/afiliados/ for direct access.

Usage:
    python scripts/tracking/landing_page_generator.py
    python scripts/tracking/landing_page_generator.py --affiliate-id aff_xxx

Requires: website-next/data/affiliates.json (with packs and tracking data)
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_FILE = REPO_ROOT / "website-next" / "data" / "affiliates.json"
OUTPUT_DIR = REPO_ROOT / "website-next" / "public" / "afiliados"
TEMPLATE_DIR = Path(__file__).parent / "templates"


def load_data():
    if not DATA_FILE.exists():
        print(f"[ERRO] Arquivo não encontrado: {DATA_FILE}")
        sys.exit(1)
    with open(DATA_FILE) as f:
        return json.load(f)


def fmt_brl(n: float) -> str:
    return f"R$ {n:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def generate_landing_page(affiliate: dict, data: dict) -> str:
    """Generate an HTML landing page for a single affiliate."""
    aid = affiliate["id"]
    name = affiliate.get("name", "Afiliado")
    ref_code = affiliate.get("ref_code", "")
    rate = affiliate.get("commission_rate", 15)
    platform = affiliate.get("platform", "Criador de Conteúdo")

    # Calculate stats
    aff_commissions = [c for c in data.get("commissions", []) if c.get("affiliate_id") == aid]
    aff_links = [l for l in data.get("links", []) if l.get("affiliate_id") == aid]

    total_earned = sum(c.get("amount", 0) for c in aff_commissions)
    total_pending = sum(c.get("amount", 0) for c in aff_commissions if c.get("status") == "pending")
    total_clicks = sum(l.get("clicks", 0) for l in aff_links)
    total_conversions = sum(l.get("conversions", 0) for l in aff_links)
    conv_rate = round((total_conversions / total_clicks * 100), 1) if total_clicks > 0 else 0

    ref_url = f"https://iconminemods.com/?ref={ref_code}"

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{name} — Afiliado IconMineMods</title>
  <meta name="description" content="Página do afiliado {name} — IconMineMods. Ganhe comissões indicando packs Minecraft, Roblox e Epic Games." />
  <meta property="og:title" content="{name} — Afiliado IconMineMods" />
  <meta property="og:description" content="{rate}% de comissão em packs Minecraft, Roblox e Epic Games." />
  <meta property="og:url" content="https://iconminemods.com/afiliados/{ref_code}" />
  <link rel="canonical" href="https://iconminemods.com/afiliados/landing/{ref_code}" />
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {{
      theme: {{
        extend: {{
          colors: {{
            zinc: {{ 950: '#09090b', 900: '#18181b', 800: '#27272a', 700: '#3f3f46', 600: '#52525b', 500: '#71717a', 400: '#a1a1aa', 300: '#d4d4d8', 200: '#e4e4e7', 100: '#f4f4f5', 50: '#fafafa' }},
          }}
        }}
      }}
    }}
  </script>
</head>
<body class="bg-zinc-950 text-white antialiased">
  <main class="max-w-4xl mx-auto px-4 py-10">
    <!-- Header -->
    <div class="text-center mb-10">
      <h1 class="text-4xl font-bold tracking-tight">
        <span class="text-green-400">{name}</span>
      </h1>
      <p class="mt-2 text-lg text-zinc-400">
        Criador parceiro da <a href="https://iconminemods.com" class="text-green-400 hover:underline">IconMineMods</a>
      </p>
      <p class="mt-1 text-sm text-zinc-500">{platform} · {rate}% de comissão</p>
      <div class="mt-4 inline-flex items-center gap-2 bg-zinc-900 border border-zinc-700 rounded-lg px-4 py-2">
        <code class="text-sm text-green-400">{ref_url}</code>
        <button onclick="navigator.clipboard.writeText('{ref_url}')"
          class="text-xs bg-zinc-800 hover:bg-zinc-700 px-2 py-1 rounded">Copiar</button>
      </div>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-10">
      <div class="border border-zinc-800 rounded-lg p-4">
        <div class="text-xs text-zinc-500">Total Ganho</div>
        <div class="mt-1 text-lg font-bold text-green-400">{fmt_brl(total_earned)}</div>
      </div>
      <div class="border border-zinc-800 rounded-lg p-4">
        <div class="text-xs text-zinc-500">Pendente</div>
        <div class="mt-1 text-lg font-bold text-amber-400">{fmt_brl(total_pending)}</div>
      </div>
      <div class="border border-zinc-800 rounded-lg p-4">
        <div class="text-xs text-zinc-500">Cliques</div>
        <div class="mt-1 text-lg font-bold text-zinc-200">{total_clicks}</div>
      </div>
      <div class="border border-zinc-800 rounded-lg p-4">
        <div class="text-xs text-zinc-500">Taxa Conv.</div>
        <div class="mt-1 text-lg font-bold text-zinc-200">{conv_rate}%</div>
      </div>
    </div>

    <!-- CTA -->
    <section class="border border-zinc-800 rounded-xl p-8 text-center bg-zinc-900/50">
      <h2 class="text-2xl font-bold tracking-tight mb-3">Quer criar seus próprios packs?</h2>
      <p class="text-zinc-400 max-w-md mx-auto mb-6">
        Junte-se ao programa de afiliados da IconMineMods e ganhe {rate}% de comissão em cada venda!
      </p>
      <div class="flex justify-center gap-3">
        <a href="https://iconminemods.com/afiliados?ref={ref_code}"
          class="px-6 py-3 bg-green-600 hover:bg-green-500 rounded-lg text-sm font-medium transition-colors">
          Quero ser Afiliado
        </a>
        <a href="https://iconminemods.com"
          class="px-6 py-3 bg-zinc-800 hover:bg-zinc-700 rounded-lg text-sm font-medium transition-colors">
          Ver Catálogo
        </a>
      </div>
    </section>

    <!-- Generated -->
    <p class="mt-8 text-center text-xs text-zinc-700">
      Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')} · IconMineMods Affiliate System
    </p>
  </main>
</body>
</html>"""
    return html


def generate_all(data: dict, single_id: str | None = None):
    """Generate landing pages for all (or one specific) affiliates."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    affiliates = data.get("affiliates", [])
    if single_id:
        affiliates = [a for a in affiliates if a.get("id") == single_id]
        if not affiliates:
            print(f"[ERRO] Afiliado não encontrado: {single_id}")
            return

    generated = 0
    for aff in affiliates:
        ref_code = aff.get("ref_code", "")
        if not ref_code:
            continue

        html = generate_landing_page(aff, data)
        out_path = OUTPUT_DIR / f"{ref_code}.html"

        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html)

        print(f"  ✅ Gerado: {out_path.name}")
        generated += 1

    print(f"\n📄 {generated} página(s) gerada(s) em: {OUTPUT_DIR}")


def main():
    data = load_data()
    args = sys.argv[1:]

    single_id = None
    for a in args:
        if a.startswith("--affiliate-id="):
            single_id = a.split("=", 1)[1]

    print("=" * 50)
    print("  ICONMINEMODS — GERADOR DE LANDING PAGES")
    print("=" * 50)
    print(f"\n📁 Data: {DATA_FILE}")
    print(f"📁 Output: {OUTPUT_DIR}\n")

    generate_all(data, single_id)


if __name__ == "__main__":
    main()
