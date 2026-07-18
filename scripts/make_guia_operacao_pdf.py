#!/usr/bin/env python3
"""Gera out/GUIA_OPERACAO.pdf — resumo do Guia de Operacao (mesmo conteudo da
pagina /admin/guia do website-next). Via Pillow (ja instalada), sem deps novas.

    python scripts/make_guia_operacao_pdf.py

Contagens dinamicas lidas de out/inventory_report.json quando disponivel.
"""
import json
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out" / "GUIA_OPERACAO.pdf"
INVENTORY = ROOT / "out" / "inventory_report.json"

W, H = 1240, 1754  # A4 @150dpi
BG = (13, 14, 22)
PANEL = (22, 24, 38)
ACCENT = (0, 200, 255)
ACCENT2 = (255, 200, 0)
TEXT = (224, 228, 240)
MUTE = (140, 148, 170)
LINE = (40, 44, 66)


def font(sz, bold=False):
    cand = [
        "C:/Windows/Fonts/segoeui%s.ttf" % ("" if not bold else "b"),
        "C:/Windows/Fonts/arial%s.ttf" % ("" if not bold else "bd"),
        "C:/Windows/Fonts/calibri%s.ttf" % ("" if not bold else "b"),
    ]
    for c in cand:
        if os.path.isfile(c):
            return ImageFont.truetype(c, sz)
    return ImageFont.load_default()


def wrap(draw, text, fnt, maxw):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=fnt) <= maxw:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def page(title, blocks, footer):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 96], fill=PANEL)
    d.rectangle([0, 96, W, 100], fill=ACCENT)
    d.text((56, 30), title, font=font(38, True), fill=TEXT)
    y = 140
    for b in blocks:
        if b[0] == "h":
            y += 14
            d.text((56, y), b[1], font=font(26, True), fill=ACCENT)
            y += 40
        elif b[0] == "p":
            for ln in wrap(d, b[1], font(20), W - 130):
                d.text((72, y), ln, font=font(20), fill=TEXT)
                y += 30
            y += 12
        elif b[0] == "b":
            d.text((72, y), "*", font=font(20, True), fill=ACCENT2)
            for ln in wrap(d, b[1], font(20), W - 160):
                d.text((100, y), ln, font=font(20), fill=TEXT)
                y += 30
            y += 4
        elif b[0] == "code":
            d.rectangle([72, y, W - 72, y + 34 * (b[1].count("\n") + 1)], fill=(10, 12, 20),
                        outline=LINE)
            for i, ln in enumerate(b[1].split("\n")):
                d.text((86, y + 8 + i * 30), ln, font=font(18), fill=ACCENT)
            y += 34 * (b[1].count("\n") + 1) + 16
        elif b[0] == "warn":
            d.rectangle([72, y, W - 72, y + 30 * (b[1].count("\n") + 1) + 20], fill=(40, 16, 16),
                        outline=(200, 60, 60))
            for i, ln in enumerate(wrap(d, b[1], font(19), W - 160)):
                d.text((88, y + 10 + i * 28), ln, font=font(19), fill=(255, 170, 170))
            y += 30 * (b[1].count("\n") + 1) + 36
        elif b[0] == "sep":
            d.line([72, y, W - 72, y], fill=LINE)
            y += 24
    d.text((56, H - 50), footer, font=font(15), fill=MUTE)
    return img


def inventory_counts():
    try:
        data = json.loads(INVENTORY.read_text(encoding="utf-8"))
        after = data.get("after", {})
        return after.get("mcpack", "?"), after.get("mctemplate", "?")
    except Exception:
        return "?", "?"


def main():
    mcpack, mctemplate = inventory_counts()

    pages = []

    pages.append(page("GUIA DE OPERACAO — IconGameDev", [
        ("p", "Resumo pratico do pipeline de producao e submissao (Bedrock Marketplace + Roblox UGC). Versao web completa e dinamica em /admin/guia do portal (website-next)."),
        ("sep", ""),
        ("h", "ESTADO ATUAL"),
        ("b", f"Packs prontos para submissao: {mcpack} .mcpack + {mctemplate} .mctemplate em submission_mcpacks/ (100% IP-clean)."),
        ("b", "Fonte da verdade do inventario: out/inventory_report.json (atualizado a cada run_daily)."),
        ("sep", ""),
        ("h", "MAPA DO SISTEMA (7 etapas)"),
        ("b", "1. Geradores: scale-products.py cria packs novos com temas livres de IP (anime/kawaii removidos)."),
        ("b", "2. Empacotamento: package_incremental.py zipa dirs novos -> submission_mcpacks/."),
        ("b", "3. Quarentena IP: quarantine_ip.py move packs sinalizados -> _ip_quarantine/ (nada deletado)."),
        ("b", "4. Submit Gate: submit_gate.py --audit (GO/NO-GO). NO-GO aborta tudo."),
        ("b", "5. Certify: certify.py roda 6 gates (build, testes, compliance, catalogo, Roblox, Epic)."),
        ("b", "6. Submissao: passos humanos no Partner Center (SUBMISSION_PLAYBOOK.md)."),
        ("b", "7. Portal/Afiliados: website-next + compute_payouts.py (comissao 15%)."),
    ], "Guia de Operacao — pagina 1/3"))

    pages.append(page("DIA A DIA — COMANDOS", [
        ("h", "Comando principal (orquestrador)"),
        ("code", "python ops/run_daily.py              # pipeline completo (batch 500)\npython ops/run_daily.py --batch 2000  # escala volume\npython ops/run_daily.py --dry-run     # simula sem executar"),
        ("p", "Idempotente. Aborta (exit 2) se o submit_gate der NO-GO. Atualiza out/inventory_report.json ao final. Agendamento (Task Scheduler/cron) no cabecalho do script."),
        ("h", "Comandos individuais"),
        ("b", "python certify.py — suite de certificacao, deve estar 6/6 verde antes de submeter."),
        ("b", "python compliance/checks/submit_gate.py --audit — gate GO/NO-GO isolado."),
        ("b", "python package_incremental.py — empacota so os dirs novos."),
        ("b", "python marketplace-content/scripts/quarantine_ip.py — quarentena de IP (seguro re-rodar)."),
        ("b", "python submit/run_all.py --resume — retoma fila de submissao de onde parou."),
        ("b", "python affiliates/compute_payouts.py — recalcula comissoes -> affiliates/payouts.json."),
        ("b", "python scripts/make_guia_operacao_pdf.py — regenera este PDF."),
        ("warn", "Se o gate falhar: leia o output do submit_gate, corrija a causa (pack com IP ou manifesto invalido), rode quarantine_ip.py e repita. NUNCA submeta com NO-GO."),
    ], "Guia de Operacao — pagina 2/3"))

    pages.append(page("PASSOS HUMANOS + CAMINHOS", [
        ("h", "Passos humanos obrigatorios (nao automatizaveis)"),
        ("b", "Conta Microsoft Partner Center aprovada (identidade/empresa)."),
        ("b", "CPF (e CNPJ/MEI se PJ); conta PayPal/Wise verificada para recebimento."),
        ("b", "W-8BEN preenchido e aprovado no Partner Center."),
        ("b", "IARC (classificacao etaria) gerado por oferta; URL de privacy policy publica."),
        ("b", "Store listing por oferta; credenciais Roblox em ops/secrets.json."),
        ("p", "Detalhes completos: SUBMISSION_PLAYBOOK.md (checklist final antes do Submit)."),
        ("sep", ""),
        ("h", "Onde ficam as coisas"),
        ("b", "submission_mcpacks/ — pacotes finais prontos (IP-clean)."),
        ("b", "_ip_quarantine/ — packs sinalizados pelo scan de IP (auditoria manual)."),
        ("b", "out/inventory_report.json — contagens, gates e historico de rodadas."),
        ("b", "affiliates/payouts.json — comissoes calculadas por afiliado."),
        ("b", "ops/secrets.json — credenciais (NUNCA commitar/compartilhar)."),
        ("b", "marketplace-content/ — fonte dos packs + geradores + testes."),
        ("sep", ""),
        ("h", "FAQ rapido"),
        ("b", "Escalar volume: --batch N no run_daily (limite pratico = tempo do gate)."),
        ("b", "Novo afiliado: editar affiliates.csv -> compute_payouts.py -> payouts.json."),
    ], "Guia de Operacao — pagina 3/3"))

    OUT.parent.mkdir(exist_ok=True)
    pages[0].save(str(OUT), "PDF", save_all=True, append_images=pages[1:])
    print("PDF gerado:", OUT)
    print("paginas:", len(pages), "tamanho:", os.path.getsize(str(OUT)), "bytes")


if __name__ == "__main__":
    main()
