#!/usr/bin/env python3
"""Generate a single PDF compliance/deploy guide for the IconGameDev skin pack."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

ROOT = Path(r"C:\Users\forrydev\Desktop\IconGameDev")
OUT = Path(r"C:\Users\forrydev\Desktop\Roblox-guia.pdf")
CATALOG = ROOT / "roblox-ugc" / "catalog" / "roblox_catalog.json"
ASSETS = ROOT / "roblox-ugc" / "assets"

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table
    from reportlab.lib.colors import HexColor
    from reportlab.platypus import TableStyle
except Exception as e:
    raise SystemExit(f"REPORTLAB_REQUIRED: {e}")


def load_catalog() -> tuple[list[dict], dict[str, int]]:
    if not CATALOG.exists():
        return [], {}
    import json
    data = json.loads(CATALOG.read_text(encoding="utf-8"))
    items = data if isinstance(data, list) else data.get("items", [])
    counts: dict[str, int] = {}
    for it in items:
        t = str(it.get("asset_type") or it.get("type") or "unknown")
        counts[t] = counts.get(t, 0) + 1
    return items, counts


def count_images() -> int:
    if not ASSETS.exists():
        return 0
    files = list(ASSETS.glob("*.png")) + list(ASSETS.glob("*.jpg")) + list(ASSETS.glob("*.jpeg"))
    return len(set(files))


def build_pdf() -> None:
    title = "IconGameDev — Roblox Skin Pack Compliance & Deploy Guide"
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="H1", fontSize=18, leading=22, spaceAfter=8, textColor=HexColor("#111111")))
    styles.add(ParagraphStyle(name="H2", fontSize=13, leading=17, spaceAfter=6, textColor=HexColor("#222222")))
    styles.add(ParagraphStyle(name="Body", fontSize=10.5, leading=15, spaceAfter=6, textColor=HexColor("#333333")))
    styles.add(ParagraphStyle(name="Mono", fontName="Courier", fontSize=9.5, leading=13, spaceAfter=4, textColor=HexColor("#444444")))

    items, type_counts = load_catalog()
    image_count = count_images()
    file_gap = max(0, 720 - image_count)

    doc = SimpleDocTemplate(str(OUT), pagesize=A4, leftMargin=18*mm, rightMargin=18*mm, topMargin=18*mm, bottomMargin=18*mm)
    story = []
    story.append(Paragraph(title, styles["H1"]))
    story.append(Paragraph(f"Gerado em: {datetime.now().isoformat(timespec='seconds')}", styles["Body"]))
    story.append(Spacer(1, 6))
    story.append(Paragraph("<b>Resumo:</b> guia operacional para colocar o skin pack em produção com segurança e compliance. Ações, pré-requisitos, passos, scripts, segurança e verificação pós-deploy.", styles["Body"]))
    story.append(Spacer(1, 8))

    story.append(Paragraph("1) STATUS ATUAL", styles["H2"]))
    story.append(Paragraph("Projeto em estado operacional. O ponto bloqueante atual é preencher imagens em <b>roblox-ugc/assets</b>.", styles["Body"]))
    story.append(Paragraph(f"- <b>CATALOG</b>: {len(items)} itens registrados", styles["Body"]))
    story.append(Paragraph(f"- <b>IMAGENS</b>: {image_count} arquivos encontrados; ajuste para {720 if not items else max(0, len([i for i in items if (i.get('asset_type') or i.get('type')) != 'game_pass']))} itens não-gamepass", styles["Body"]))
    story.append(Paragraph("- <b>COMPLIANCE</b>: docs presentes", styles["Body"]))
    story.append(Paragraph("- <b>DEPLOY</b>: scripts presentes", styles["Body"]))
    story.append(Spacer(1, 8))

    story.append(Paragraph("2) PRÉ-REQUISITOS", styles["H2"]))
    for p in [
        "Python 3.10+",
        "Credenciais Roblox: ROBLOX_API_KEY, ROBLOX_GROUP_ID, ROBLOX_EXPERIENCE_ID",
        "Imagens para cada item do catálogo, salvas em roblox-ugc/assets",
        "Sem segredos versionados: usar ops/secrets.json ou variáveis de ambiente",
    ]:
        story.append(Paragraph(f"- {p}", styles["Body"]))
    story.append(Spacer(1, 8))

    story.append(Paragraph("3) ESTRUTURA DO PROJETO", styles["H2"]))
    rows = [["PASTA", "FUNÇÃO"], ["submit/", "Pipeline e scripts"], ["roblox-ugc/catalog/", "Catálogo oficial"], ["roblox-ugc/assets/", "Imagens"], ["ops/", "Segredos operacionais"], ["compliance/", "Conformidade"]]
    tbl = Table(rows, colWidths=[90, 260])
    tbl.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), HexColor("#eeeeee")), ("TEXTCOLOR", (0, 0), (-1, 0), HexColor("#000000")), ("GRID", (0, 0), (-1, -1), 0.4, HexColor("#cccccc")), ("VALIGN", (0, 0), (-1, -1), "TOP")]))
    story.append(tbl)
    story.append(Spacer(1, 8))

    story.append(Paragraph("4) PASSOS PARA SUBIR 100%", styles["H2"]))
    for s in ["Coloque as imagens em <b>roblox-ugc/assets</b> com nome igual ao campo <b>name</b> do catálogo.", "Rode: <b>python submit/submit_roblox.py --dry-run</b>", "Ajuste até não aparecer <b>[NO IMAGE]</b>.", "Teste controlado: <b>python submit/submit_roblox.py --test-one</b>", "Valide e confirme: <b>python submit/submit_roblox.py</b>", "Revise: <b>submit/last_run_report.json</b>"]:
        story.append(Paragraph(s, styles["Body"]))
    story.append(Spacer(1, 8))

    story.append(Paragraph("5) COMANDOS PRINCIPAIS", styles["H2"]))
    for label, cmd in [("Dry-run", "python submit/submit_roblox.py --dry-run"), ("Teste inicial", "python submit/submit_roblox.py --test-one"), ("Upload real", "python submit/submit_roblox.py"), ("Pipeline", "python submit/pipeline.py --dry-run")]:
        story.append(Paragraph(f"- <b>{label}</b>", styles["Mono"]))
        story.append(Paragraph(cmd, styles["Mono"]))
    story.append(Spacer(1, 8))

    story.append(Paragraph("6) FLUXO DE UPLOAD ROBLOX UGC", styles["H2"]))
    for item in ["ClassicShirt/ClassicPants: multipart com imagem.", "Avatar accessory/Hat: multipart com imagem.", "GamePass: criação via API JSON; ícone manual no Creator Hub.", "Idempotente por nome com retry automático em erros transitórios."]:
        story.append(Paragraph(f"- {item}", styles["Body"]))
    story.append(Spacer(1, 8))

    story.append(Paragraph("7) COMPLIANCE OBRIGATÓRIA", styles["H2"]))
    for item in ["Arte original própria ou licenciada.", "Sem assets protegidos de terceiros.", "Imagens seguem limites e formato aceito.", "Descrições/nomes sem conteúdo abusivo ou enganoso.", "Segredos fora do repositório."]:
        story.append(Paragraph(f"- {item}", styles["Body"]))
    story.append(Spacer(1, 8))

    story.append(Paragraph("8) SEGURANÇA", styles["H2"]))
    for s in ["Nunca comitar ops/secrets.json com valores reais.", "Nunca usar ROBLOX_API_KEY de produção em testes.", "Validar catálogo antes de upload real.", "Limitar volume por execução e revisar relatórios."]:
        story.append(Paragraph(f"- {s}", styles["Body"]))
    story.append(Spacer(1, 8))

    story.append(Paragraph("9) VERIFICAÇÃO PÓS-DEPLOY", styles["H2"]))
    story.append(Paragraph("Checar assets no grupo/experience vinculado e confirmar preços corretos.", styles["Body"]))
    story.append(Paragraph("Usar <b>submit/last_run_report.json</b> como evidência de sucesso.", styles["Body"]))
    story.append(Spacer(1, 8))

    story.append(Paragraph("10) PRÓXIMOS PASSOS", styles["H2"]))
    story.append(Paragraph("Após subir este pacote, mantenha o catálogo atualizado e replique para novas coleções.", styles["Body"]))
    story.append(Paragraph("Docs: submit/DEPLOY.md, compliance/INDEX.md, compliance/checks/pre_submission_checklist.md", styles["Body"]))

    doc.build(story)


if __name__ == "__main__":
    build_pdf()
    print(f"OK: {OUT}")
    print(f"SIZE: {OUT.stat().st_size}")
