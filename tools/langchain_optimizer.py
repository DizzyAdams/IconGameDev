#!/usr/bin/env python3
"""IconGameDev - otimizador de receita orientado por LangChain (opcional).

Le os sinais reais do projeto (payouts de afiliados, volumes de catalogo e
packs Bedrock) e produz um plano de acoes priorizado para maximizar faturamento
nos proximos 90 dias.

- Se `langchain` + OPENAI_API_KEY estiverem disponiveis: usa um RunnableSequence
  (LCEL) para enriquecer o plano com raciocinio de LLM.
- Caso contrario: usa um analisador deterministico (stdlib) - roda hoje, sem
  dependencias externas. Eh o mesmo ponto de integracao; basta plugar a chave.

    python tools/langchain_optimizer.py
"""
from __future__ import annotations

import glob
import json
import os
import sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.dirname(os.path.abspath(__file__))
PAYOUTS = os.path.join(ROOT, "affiliates", "payouts.json")
SUBMIT_PACKS = os.path.join(ROOT, "submission_mcpacks")
RUBRIC = os.path.join(ROOT, "ops", "secrets.example.json")


def load_signals() -> dict:
    sig: dict = {
        "affiliate_total_commission_usd": 0.0,
        "top_affiliates": [],
        "bedrock_packs_ready": 0,
        "has_microsoft_secrets": False,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    if os.path.exists(PAYOUTS):
        try:
            data = json.load(open(PAYOUTS))
            sig["affiliate_total_commission_usd"] = float(data.get("total_commission_usd", 0.0))
            sig["top_affiliates"] = [
                a["handle"] for a in data.get("affiliates", [])[:3]
            ]
        except (json.JSONDecodeError, OSError):
            pass
    sig["bedrock_packs_ready"] = len(glob.glob(os.path.join(SUBMIT_PACKS, "*.mcpack")))
    sig["has_microsoft_secrets"] = os.path.exists(RUBRIC)
    return sig


def heuristic_plan(sig: dict) -> list[dict]:
    """Plano deterministico a partir dos sinais (sempre disponivel)."""
    plan = []
    if sig["bedrock_packs_ready"] < 150:
        plan.append({
            "priority": "ALTA",
            "action": f"Subir volume de packs Bedrock de {sig['bedrock_packs_ready']} "
                      f"para >=150/mes via agencias (revenue share 30%).",
            "impact": "Destrava teto de catalogo Minecraft apos aprovar Partner Center.",
        })
    if sig["affiliate_total_commission_usd"] < 4800:
        plan.append({
            "priority": "ALTA",
            "action": "Recrutar afiliados diretos (comissao 15%) com trafego proprio; "
                      "focar jogadores EUA 18+ verificados na experience.",
            "impact": "Aumenta a fatia de ~US$ 4.800/mes em afiliados; sobe taxa DevEx para 0,0054.",
        })
    if not sig["has_microsoft_secrets"]:
        plan.append({
            "priority": "CRITICA",
            "action": "Concluir KYC Microsoft Partner Center (CNPJ + IARC + W-8BEN-E).",
            "impact": "Sem aprovacao, receita Minecraft (net ~US$ 1.300) fica travada.",
        })
    plan.append({
        "priority": "MEDIA",
        "action": "Manter certify.py em 100% e rodar submit/pipeline.py --dry-run antes de cada envio.",
        "impact": "Evita retrabalho e rejeicoes de moderacao/Compliance.",
    })
    return plan


def llm_plan(sig: dict, heuristic: list[dict]) -> list[dict] | None:
    """Tenta enriquecer o plano com LangChain LCEL. Retorna None se indisponivel."""
    if not os.environ.get("OPENAI_API_KEY"):
        # Sem chave: nem importamos o langchain (import lento) -> fallback rapido.
        return None
    try:
        from langchain_openai import ChatOpenAI
        from langchain_core.prompts import PromptTemplate
        from langchain_core.runnables import RunnableSequence
    except Exception as e:  # noqa: BLE001
        print(f"[langchain] import indisponivel ({e}); usando plano deterministico.", file=sys.stderr)
        return None

    prompt = PromptTemplate.from_template(
        "Voce e consultor de crescimento do projeto IconGameDev (Roblox UGC + Minecraft "
        "Bedrock + afiliados). Sinais: {signals}. Plano base: {heuristic}. "
        "Retorne ate 5 acoes priorizadas para faturar US$ 20k em 90 dias, em PT-BR, "
        "formato JSON: [{{priority, action, impact}}]."
    )
    try:
        chain: RunnableSequence = prompt | ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
        out = chain.invoke({"signals": json.dumps(sig), "heuristic": json.dumps(heuristic)})
        text = out.content if hasattr(out, "content") else str(out)
        start, end = text.find("["), text.rfind("]")
        if start != -1 and end != -1:
            return json.loads(text[start:end + 1])
    except Exception as e:  # noqa: BLE001
        print(f"[langchain] falha no LLM ({e}); usando plano deterministico.", file=sys.stderr)
    return None


def main() -> int:
    sig = load_signals()
    print("=" * 64)
    print(" ICONGAMEDIV - OTIMIZADOR DE RECEITA (LangChain-ready)")
    print("=" * 64)
    print(f"  Packs Bedrock prontos : {sig['bedrock_packs_ready']}")
    print(f"  Comissao afiliados    : US$ {sig['affiliate_total_commission_usd']:.2f}")
    print(f"  Top afiliados         : {', '.join(sig['top_affiliates']) or '-'}")
    print(f"  Secrets Microsoft      : {'sim' if sig['has_microsoft_secrets'] else 'nao'}")
    print("-" * 64)

    plan = llm_plan(sig, heuristic_plan(sig)) or heuristic_plan(sig)
    for i, item in enumerate(plan, 1):
        print(f"  {i}. [{item.get('priority','?')}] {item.get('action')}")
        print(f"     impacto: {item.get('impact','')}")
    print("=" * 64)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
