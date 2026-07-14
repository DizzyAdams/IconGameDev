#!/usr/bin/env python3
"""Generate C:\\Users\\forrydev\\Desktop\\roblox-guia-subir-skins.pdf

Guia operacional (runbook) para publicar as skins/itens de avatar atuais do
Roblox via o pipeline do projeto IconGameDev:
  roblox-ugc/tools/generate_catalog.py -> roblox_catalog.json
  roblox-ugc/tools/roblox_checks.py    -> VERDICT PASS
  submit/submit_roblox.py              -> upload Open Cloud (idempotente)
  submit/pipeline.py + certify.py       -> orquestracao/qualidade
Baseado nos scripts reais do repo (lidos em 2026).
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, ListFlowable, ListItem, PageBreak)

OUT = r"C:\Users\\forrydev\\Desktop\\roblox-guia-subir-skins.pdf"

styles = getSampleStyleSheet()
NAVY = colors.HexColor("#0b3d63")
ACCENT = colors.HexColor("#1f8a4c")
LIGHT = colors.HexColor("#eef4f8")
GREY = colors.HexColor("#444444")

styles.add(ParagraphStyle("Capa", parent=styles["Title"], fontSize=24,
                          textColor=NAVY, leading=28, spaceAfter=4, alignment=TA_CENTER))
styles.add(ParagraphStyle("Sub", parent=styles["Normal"], fontSize=12,
                          textColor=GREY, alignment=TA_CENTER, leading=17, spaceAfter=2))
styles.add(ParagraphStyle("H1", parent=styles["Heading1"], fontSize=15,
                          textColor=NAVY, spaceBefore=12, spaceAfter=6))
styles.add(ParagraphStyle("H2", parent=styles["Heading2"], fontSize=12,
                          textColor=ACCENT, spaceBefore=8, spaceAfter=4))
styles.add(ParagraphStyle("Body", parent=styles["Normal"], fontSize=10,
                          leading=14, spaceAfter=6, alignment=TA_LEFT))
styles.add(ParagraphStyle("MyBullet", parent=styles["Normal"], fontSize=10, leading=13))
styles.add(ParagraphStyle("Cell", parent=styles["Normal"], fontSize=9, leading=12))
styles.add(ParagraphStyle("CellH", parent=styles["Normal"], fontSize=9, leading=12,
                          textColor=colors.white, fontName="Helvetica-Bold"))


def P(t, s="Body"):
    return Paragraph(t, styles[s])


def H1(t):
    return Paragraph(t, styles["H1"])


def H2(t):
    return Paragraph(t, styles["H2"])


def bullets(items, style="MyBullet"):
    return ListFlowable(
        [ListItem(Paragraph(i, styles[style]), leftIndent=10) for i in items],
        bulletType="bullet", start="\u2022", leftIndent=12, spaceAfter=6)


def table(data, col_widths, header=True):
    rows = []
    for r, row in enumerate(data):
        cells = []
        for c in row:
            st = "CellH" if (header and r == 0) else "Cell"
            cells.append(Paragraph(str(c), styles[st]))
        rows.append(cells)
    t = Table(rows, colWidths=col_widths, hAlign="LEFT")
    ts = [
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#bcd0de")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ]
    if header:
        ts.append(("BACKGROUND", (0, 0), (-1, 0), NAVY))
    t.setStyle(TableStyle(ts))
    return t


story = []

# ---------------------------------------------------------------- CAPA
story.append(Spacer(1, 36))
story.append(P("Guia Operacional - Subir Skins Roblox (UGC)", "Capa"))
story.append(P("Runbook de publicacao das skins/itens de avatar atuais | IconMineMods", "Sub"))
story.append(Spacer(1, 10))
story.append(P("Como levar nossas skins do catalogo para o Roblox via Open Cloud API, "
                "usando o pipeline do projeto IconGameDev (generate_catalog -> roblox_checks "
                "-> submit_roblox -> certify).", "Sub"))
story.append(Spacer(1, 20))
story.append(P("Baseado nos scripts reais do repositorio (roblox-ugc/tools, submit, certify). "
                "Revisado em 2026.", "Sub"))
story.append(PageBreak())

# ---------------------------------------------------------------- 1. FLUXO
story.append(H1("1. Resumo do fluxo (4 comandos)"))
story.append(table([
    ["Passo", "Comando", "Resultado"],
    ["1. Gerar catalogo", "python roblox-ugc/tools/generate_catalog.py", "roblox_catalog.json (900 itens)"],
    ["2. Validar", "python roblox-ugc/tools/roblox_checks.py", "VERDICT: PASS"],
    ["3. Dry-run upload", "python submit/submit_roblox.py --dry-run", "checa creds + imagens (sem rede)"],
    ["4. Subir", "python submit/submit_roblox.py --test-one", "1 item real; depois rode o completo"],
], [33*mm, 78*mm, 59*mm]))
story.append(Spacer(1, 6))
story.append(P("Antes do envio real, rode certify.py (meta 100%) e submit/pipeline.py --dry-run (GO)."))

# ---------------------------------------------------------------- 2. PRE-REQUISITOS
story.append(H1("2. Pre-requisitos humanos (uma vez)"))
story.append(bullets([
    "Conta Roblox com e-mail verificado; idade minima 13 anos.",
    "2FA (verificacao em duas etapas) ativa.",
    "DevEx habilitado + formulario fiscal W-8 (nao-EUA) / W-9 (EUA) com CPF/CNPJ.",
    "PayPal (ou Hyperwallet) vinculado no portal de pagamento.",
    "API key Open Cloud com permissao de upload (Creator Hub -> Develop -> API keys).",
    "Group ID e Universe/Experience ID da experiencia IconHub anotados.",
]))
story.append(P("Credenciais: preencha ops/secrets.json (roblox.api_key, roblox.group_id, "
                "roblox.experience_id) OU variaveis de ambiente ROBLOX_API_KEY / "
                "ROBLOX_GROUP_ID / ROBLOX_EXPERIENCE_ID. Nunca comite secrets.json."))

# ---------------------------------------------------------------- 3. PREPARAR ASSETS
story.append(H1("3. Preparar as skins (assets)"))
story.append(P("As imagens ficam em roblox-ugc/assets/, nomeadas pelo 'name' do catalogo:"))
story.append(bullets([
    "<name>.png | <name>.jpg | <name>.jpeg  (para shirts, pants e accessories/Hat).",
    "Game passes usam o mesmo nome para o icone, mas o upload do icone AINDA NAO e "
    "automatizado - adicione o icone manualmente no Creator Hub apos criar o pass.",
    "Tamanho da imagem: 1 byte a 10 MB por arquivo.",
    "Nomes 100% originais (zero IP de terceiros, zero NSFW) - o roblox_checks bloqueia "
    "substrings como pokemon, naruto, minecraft, marvel, etc.",
]))
story.append(P("Tipos mapeados no uploader (TYPE_MAP): classic_shirt -> ClassicShirt, "
                "classic_pants -> ClassicPants, avatar_accessory -> Hat, game_pass -> GamePass."))

# ---------------------------------------------------------------- 4. GERAR CATALOGO
story.append(H1("4. Gerar o catalogo"))
story.append(P("O generator e deterministico/idempotente. Roda do ROOT do projeto:"))
story.append(P("python roblox-ugc/tools/generate_catalog.py", "Sub"))
story.append(P("Gera roblox-ugc/catalog/roblox_catalog.json com 900 itens: 270 ClassicShirt "
                "(70 Robux), 180 ClassicPants (70), 270 avatar_accessory/Hat (150), 180 game_pass "
                "(250). O criador fica com 30% do preco (comissao oficial de itens de avatar); "
                "math de DevEx (taxa 0,0038) fica consistente para o roblox_checks aprovar."))

# ---------------------------------------------------------------- 5. VALIDAR
story.append(H1("5. Validar compliance (obrigatorio)"))
story.append(P("python roblox-ugc/tools/roblox_checks.py", "Sub"))
story.append(P("Verifica: count > 0, precos por tipo, math DevEx (net = preco*0.70; usd = "
                "net*taxa), limites 1..10000 Robux, e ausencia de IP/NSFW nos nomes. "
                "So continue se o veredito for PASS."))

# ---------------------------------------------------------------- 6. DRY-RUN
story.append(H1("6. Dry-run do upload (sem rede)"))
story.append(P("python submit/submit_roblox.py --dry-run", "Sub"))
story.append(P("Confere: itens encontrados, credenciais presentes, diretorio de assets, e "
                "lista os itens sem imagem (non-gamepass). Corrija imagens faltantes antes "
                "do real."))

# ---------------------------------------------------------------- 7. UPLOAD REAL
story.append(H1("7. Upload real (Open Cloud)"))
story.append(bullets([
    "Primeiro, 1 item so para validar ponta a ponta: python submit/submit_roblox.py --test-one",
    "Depois, run completo: python submit/submit_roblox.py",
    "Idempotente por nome (state_roblox.json): itens ja 'uploaded' sao pulados.",
    "Teto de seguranca: MAX_ITEMS = 500 por run real (hard cap).",
    "Retries (3x) com backoff em erros transientes de rede; guard de 250 MB de upload.",
    "Endpoints: assets/v1/assets (multipart) para itens; cloud/v2/universes/{universe}/"
    "user-game-passes para game passes.",
]))


# ---------------------------------------------------------------- 8. PIPELINE + CERTIFY
story.append(H1("8. Orquestracao completa (pipeline + certify)"))
story.append(bullets([
    "python submit/pipeline.py --dry-run  -> GO/NO-GO (Bedrock + Roblox + dominio).",
    "python certify.py  -> 6 gates; meta 100% antes do envio real.",
    "Envio real: python submit/pipeline.py (idempotente; falhas por estagio nao param o resto).",
    "No GitHub Actions: cadastre os secrets ROBLOX_API_KEY / ROBLOX_GROUP_ID / "
    "ROBLOX_EXPERIENCE_ID e descomente o bloco 'Real submission' do submit.yml.",
]))

# ---------------------------------------------------------------- 9. POS-UPLOAD
story.append(H1("9. Pos-upload: moderacao e DevEx"))
story.append(bullets([
    "A Roblox modera cada item apos o upload; pode levar dias. Acompanhe no Creator Hub.",
    "Game passes: adicione o icone manualmente no Creator Hub (nao automatizado ainda).",
    "DevEx so after acumular Earned Robux: 100.000 Robux = ~US$ 380 na taxa 0,0038.",
    "Taxa oficial atual (2026): US$ 0,0038 / Robux (padrao); US$ 0,0054 / Robux para "
    "compras de jogadores EUA 18+ verificados por ID/face (+42%).",
    "1 saque DevEx por mes calendario; group funds contam se ganhos legitimos.",
]))

# ---------------------------------------------------------------- 10. DICAS
story.append(H1("10. Dicas para maximizar faturamento"))
story.append(bullets([
    "Foque trafego de jogadores EUA 18+ verificados na experiencia -> taxa DevEx sobe para 0,0054.",
    "SEO de nome: use palavras de nicho + variantes (Neon, Glitch, Royal, Shadow, Prism...).",
    "Thumbnail de qualidade em 1..10 MB; primeira impressao decide a compra.",
    "Mantenha o catalogo variado (shirts/pants/accessories/passes) para ampliar alcance.",
    "Recrutar afiliados (comissao 15%) com trafego proprio multiplica o topo de funil.",
]))

# ---------------------------------------------------------------- 11. ACAO CORRETIVA
story.append(H1("11. Acao corretiva no codigo (taxa DevEx)"))
story.append(P("O generator e o checker usam DEVEX_RATE = 0,0035 (taxa antiga, pre 05/09/2025). "
                "A taxa oficial atual e 0,0038 (padrao) / 0,0054 (EUA 18+). Para os numeros de "
                "DevEx baterem com a realidade, atualize a constante nos dois arquivos:"))
story.append(bullets([
    "roblox-ugc/tools/generate_catalog.py  ->  DEVEX_RATE = 0.0038",
    "roblox-ugc/tools/roblox_checks.py      ->  DEVEX_RATE = 0.0038",
    "E o comentario '100000 Robux = US$350' em generate_catalog.py -> ~US$ 380 (0,0038).",
]))
story.append(P("Mantenha os DOIS iguais, senao o roblox_checks vai dar FAIL de inconsistencia."))

# ---------------------------------------------------------------- 12. CHECKLIST
story.append(H1("12. Checklist antes de subir as skins"))
story.append(bullets([
    "[ ] Conta Roblox + 2FA + DevEx + W-8BEN + PayPal (voce)",
    "[ ] API key Open Cloud criada; ops/secrets.json com roblox.* preenchido",
    "[ ] Imagens em roblox-ugc/assets/ com nome == catalog name",
    "[ ] python generate_catalog.py  (900 itens)",
    "[ ] python roblox_checks.py  -> VERDICT: PASS",
    "[ ] python submit/submit_roblox.py --dry-run  (creds + imagens OK)",
    "[ ] python submit/submit_roblox.py --test-one  (1 item real OK)",
    "[ ] python certify.py  -> 100%  e  python submit/pipeline.py --dry-run  -> GO",
    "[ ] python submit/submit_roblox.py  (run completo, idempotente)",
    "[ ] Acompanhar moderacao no Creator Hub; icones de pass manuais",
]))
story.append(Spacer(1, 8))
story.append(P("Fonte: scripts do repositorio IconGameDev (roblox-ugc/tools, submit) + documentacao "
                "oficial Roblox DevEx (2026). Nao e aconselhamento fiscal/juridico.", "Sub"))

# ---------------------------------------------------------------- LINKS
def _link(url):
    return Paragraph('<a href="%s">%s</a>' % (url, url), styles["Cell"])


def _links_table(rows):
    data = [["Recurso", "Link (clique para abrir)"]]
    for desc, url in rows:
        data.append([Paragraph(desc, styles["Cell"]), _link(url)])
    t = Table(data, colWidths=[55*mm, 115*mm], hAlign="LEFT")
    t.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#bcd0de")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ]))
    return t


_LINKS = [
    ("Criar conta Roblox", "https://www.roblox.com/"),
    ("API keys Open Cloud (crie a chave de upload aqui)",
     "https://create.roblox.com/dashboard/credentials"),
    ("Documentacao do Criador (hub)", "https://create.roblox.com/docs"),
    ("Roblox DevEx (regras e taxas)", "https://create.roblox.com/docs/production/monetization/developer-exchange"),
    ("Grupos Roblox (Group ID)", "https://www.roblox.com/groups"),
    ("Ajuda Roblox (2FA, seguranca)", "https://en.help.roblox.com/hc/pt-br"),
    ("Microsoft Partner Center (Bedrock)", "https://partner.microsoft.com/"),
    ("IARC (classificacao etaria - Bedrock)", "https://www.globalratings.com/"),
    ("PayPal (payout)", "https://www.paypal.com/"),
]
story.append(H1("Links uteis (clique para abrir)"))
story.append(P("A API key do Open Cloud fica em create.roblox.com/dashboard/credentials. Roblox muda "
                "as URLs de doc com frequencia; se um link quebrar, use o hub "
                "https://create.roblox.com/docs e procure o topico no menu."))
story.append(_links_table(_LINKS))

# ---------------------------------------------------------------- BUILD
doc = SimpleDocTemplate(OUT, pagesize=A4,
                        leftMargin=18*mm, rightMargin=18*mm,
                        topMargin=16*mm, bottomMargin=16*mm,
                        title="Guia Operacional - Subir Skins Roblox (UGC)",
                        author="IconGameDev")
doc.build(story)
print("PDF escrito em:", OUT)

