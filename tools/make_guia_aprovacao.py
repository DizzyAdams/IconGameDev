#!/usr/bin/env python3
"""Generate C:\\Users\\forrydev\\Desktop\\roblox-guia-aprovacao.pdf

Guia de aprovacao e maximizacao de receita (PT-BR) para Roblox (DevEx,
Creator Rewards, UGC) + Minecraft Bedrock Marketplace, integrado a estrategia
de afiliados/automacao do projeto IconGameDev / IconMineMods.

Pontos oficiais da Roblox (docs acessados em 2026): DevEx taxa 0,0038/Robux
(0,0054 p/ EUA 18+ verificados), minimo 30.000 Earned Robux, 1 saque/mes;
Engagement-Based Payouts extinto em 24/07/2025 -> Creator Rewards.
Minecraft: programa de parceiros Partner Center (conhecimento consolidado,
valores contratuais rotulados como estimativa).
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, ListFlowable, ListItem, PageBreak)

OUT = r"C:\Users\forrydev\Desktop\roblox-guia-aprovacao.pdf"

styles = getSampleStyleSheet()
NAVY = colors.HexColor("#0b3d63")
ACCENT = colors.HexColor("#1f8a4c")
LIGHT = colors.HexColor("#eef4f8")
GREY = colors.HexColor("#444444")

styles.add(ParagraphStyle("Capa", parent=styles["Title"], fontSize=25,
                          textColor=NAVY, leading=29, spaceAfter=4, alignment=TA_CENTER))
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
story.append(Spacer(1, 40))
story.append(P("Guia de Aprovacao e Receita", "Capa"))
story.append(P("Roblox (UGC / DevEx) + Minecraft Bedrock Marketplace", "Sub"))
story.append(Spacer(1, 10))
story.append(P("Estrategia IconMineMods / IconGameDev para faturar ate US$ 20k em 90 dias "
                "via catalogo UGC, Marketplace e programa de afiliados", "Sub"))
story.append(Spacer(1, 24))
story.append(P("Base: documentacao oficial Roblox (acesso 2026) + programa de parceiros "
                "Minecraft (valores contratuais rotulados). Revisado para o projeto em "
                "C:\\Users\\forrydev\\Desktop\\IconGameDev.", "Sub"))
story.append(PageBreak())

# ---------------------------------------------------------------- 1. VISAO
story.append(H1("1. Visao geral e meta"))
story.append(P("Objetivo: atingir ~US$ 20k/mes combinando 4 fontes independentes de "
                "receita. Nenhuma delas e automatica por si so - o dinheiro vem de "
                "vendas reais apos a aprovacao das contas e do conteudo."))
story.append(table([
    ["Fonte", "Mecanica", "Papel no 20k/mes"],
    ["Roblox UGC / DevEx", "Venda de itens de avatar + DevEx (Robux->USD)", "Base ~US$ 2.000"],
    ["Afiliados (15%)", "Comissao sobre trafego proprio que converte", "Escala ~US$ 4.800"],
    ["Minecraft Bedrock", "Packs no Marketplace (apos aprovar Partner Center)", "Net ~US$ 1.300"],
    ["Agencias de skins", "Revenue share 30% (25% fast-track) de packs terceiros", "Empurra o resto ate 20k"],
], [55*mm, 70*mm, 45*mm]))
story.append(Spacer(1, 6))
story.append(P("Cronograma alvo: 90 dias. Aprovacoes (KYC/tributario) sao o gargalo - "
                "comece na Semana 1, em paralelo a producao de conteudo."))

# ---------------------------------------------------------------- 2. ROBLOX CONTA
story.append(H1("2. Roblox: conta e aprovacao (pre-requisitos humanos)"))
story.append(P("Tudo abaixo e ACAO HUMANA obrigatoria (uma vez). ToS proibe conta por bot; "
                "KYC/tributario e pessoal e o clawback de pagamentos irregulares destroi o projeto."))
story.append(bullets([
    "Criar conta Roblox com e-mail verificado; idade minima 13 anos.",
    "Ativar 2FA (verificacao em duas etapas).",
    "Habilitar DevEx: abrir conta no portal DevEx + formulario fiscal W-8 (nao-EUA) ou W-9 (EUA) com CPF/CNPJ.",
    "Vincular PayPal (ou Hyperwallet) no portal de pagamento.",
    "Criar API key Open Cloud (permissao de upload) para o catalogo UGC automatico.",
    "Anotar Group ID e Universe/Experience ID da experiencia IconHub.",
]))
story.append(P("No projeto: preencha ops/secrets.json (roblox.api_key, group_id, "
                "experience_id). Nunca comite secrets.json (ja esta no .gitignore)."))

# ---------------------------------------------------------------- 3. DEVEX
story.append(H1("3. Roblox DevEx - regras e taxas oficiais"))
story.append(P("DevEx troca Earned Robux por moeda real. Earned Robux = Robux de valor real "
                "(vendas in-game, passes, assinaturas, servidores privados, itens de avatar, "
                "Creator Rewards). NAO conta: Robux comprado, brinde, cartao ou transferencia. "
                "A Roblox decide discricionariamente o que qualifica."))
story.append(table([
    ["Requisito", "Detalhe (oficial)"],
    ["Idade minima", "13 anos"],
    ["Earned Robux minimo", "30.000"],
    ["E-mail verificado", "Sim"],
    ["Conta no portal DevEx", "Sim"],
    ["Formulario fiscal", "W-8 (nao-EUA) / W-9 (EUA)"],
    ["Taxa padrao", "US$ 0,0038 por Robux (US$ 114 / 30.000)"],
    ["Taxa elevada", "US$ 0,0054 / Robux (compras de jogadores EUA 18+ verificados por ID/face)"],
    ["Frequencia de saque", "1 por mes calendario"],
    ["Group funds", "Contam se os ganhos forem legitimos (bona fide)"],
], [50*mm, 120*mm]))
story.append(Spacer(1, 6))
story.append(P("Dica de ouro: direcione trafego de jogadores EUA maiores de 18 anos verificados "
                "-> a taxa sobe de 0,0038 para 0,0054 (+42% no mesmcambio)."))


# ---------------------------------------------------------------- 4. MONETIZACAO ROBLOX
story.append(H1("4. Como gerar Earned Robux na Roblox"))
story.append(H2("4.1 Creator Rewards (engajamento)"))
story.append(P("Desde 24/07/2025 substituiu o Engagement-Based Payouts. Voce ganha por engajamento "
                "de membros Premium no seu jogo, independente do tamanho. Dicas oficiais:"))
story.append(bullets([
    "Adicione o Premium Purchase Modal no jogo (compra dentro da experiencia).",
    "NAO use o modal como paywall na entrada do jogo.",
    "NAO prometa Robux/itens fora do jogo que voce nao controla.",
    "Ofereca merch exclusivo a Premium, sem vantagem tactica de gameplay.",
    "Verifique MembershipType antes de disparar o modal (evite spam).",
]))
story.append(H2("4.2 Outros canais"))
story.append(bullets([
    "Catalogo UGC (itens de avatar): taxa de upload por item; e preciso vender o suficiente para liberar o ganho. Foque nicho + thumb de qualidade + SEO de palavras-chave.",
    "Game Passes / Developer Products / assinaturas dentro da experiencia IconHub.",
    "Servidores privados pagos.",
    "Modelos/plugins na Creator Store (Marketplace para criadores).",
]))

# ---------------------------------------------------------------- 5. MINECRAFT
story.append(H1("5. Minecraft Bedrock Marketplace - aprovacao"))
story.append(P("Requer conta Microsoft Partner Center (pessoa juridica / CNPJ), aprovacao, "
                "questionario IARC (classificacao etaria) e W-8BEN-E. Leva de dias a semanas - "
                "inicie cedo, em paralelo a producao de packs."))
story.append(bullets([
    "Aplicar via Partner Center / portal de parceiros Minecraft.",
    "Constituir CNPJ (a aprovacao Microsoft exige empresa).",
    "Gerar certificado IARC para cada pack (sem isso nao publica).",
    "W-8BEN-E no arquivo fiscal; conta de pagamento (Wise/PayPal).",
    "Pacotes no padrao: manifest.json valido, UUIDs v4 unicos, PNG 64x64 (skins) / 256x256 (icone), zero IP de terceiros.",
]))
story.append(P("Partilha de receita (estimativa - valores contratuais variam):"))
story.append(table([
    ["Camada", "Participacao"],
    ["Microsoft (plataforma/loja)", "~30%"],
    ["Parceiro de conteudo (voce/agencia)", "~70% do liquido, dividido por contrato"],
    ["Voce (apos agencia 30%)", "tipicamente ~50-70% do preco de venda apos taxas"],
], [70*mm, 100*mm]))


# ---------------------------------------------------------------- 6. AFILIADOS
story.append(H1("6. Programa de afiliados (escala sem headcount)"))
story.append(bullets([
    "Afiliados diretos: comissao 15% sobre a receita (affiliates/compute_payouts.py gera payouts.json). Cada afiliado traz trafego proprio.",
    "Agencias de skins: revenue share 30% (25% acima de 150 packs/mes). Entregam .mcpack prontos no padrao (manifest, UUIDs, PNG 64x64/256x256, zero IP).",
    "Fast-track: prioridade na fila + analise automatica + recebimento acelerado.",
    "Quando a Microsoft aprova, o dist/ ja esta cheio -> submissao em lote dias depois, nao semanas.",
]))
story.append(table([
    ["Fonte", "Estimativa / mes (projeto)"],
    ["Roblox UGC / DevEx", "~US$ 2.000"],
    ["Afiliados (15%)", "~US$ 4.800"],
    ["Minecraft (net)", "~US$ 1.300"],
    ["Agencias (extra)", "empurra o resto ate US$ 20.000"],
], [80*mm, 90*mm]))

# ---------------------------------------------------------------- 7. 90 DIAS
story.append(H1("7. Plano de 90 dias para US$ 20k"))
story.append(table([
    ["Janela", "Foco", "Acao concreta"],
    ["Dias 0-15", "KYC humano", "Contas Roblox + MS, 2FA, DevEx, W-8BEN, PayPal, API key; breve de padrao p/ agencias."],
    ["Dias 15-45", "Catalogo", "100 itens Roblox + 150-300 packs Bedrock (agencias); rodar certify ate 100%."],
    ["Dias 45-75", "Lancar + trafego", "Afiliados ativos, Premium modal na experiencia, SEO de itens, criar grupo Roblox."],
    ["Dias 75-90", "Escalar", "Submissao em lote pos-aprovacao MS; otimizar top sellers; recrutar +afiliados."],
], [28*mm, 32*mm, 110*mm]))

# ---------------------------------------------------------------- 8. AUTOMACAO
story.append(H1("8. Automacao no projeto IconGameDev"))
story.append(bullets([
    "certify.py: 6 gates (testes, Bedrock, site, Roblox, dominio, dry-run) -> meta 100% antes de enviar.",
    "submit/pipeline.py --dry-run: veredito GO/NO-GO sem enviar.",
    "submit/pipeline.py: envio idempotente (Bedrock + Roblox + dominio); rodar de novo e seguro.",
    "GitHub Actions: CI roda testes/build; 'Real submission' via workflow_dispatch (botao Run workflow).",
    "ACAO HUMANA obrigatoria: criar conta, KYC, W-8BEN, PayPal, clicar 'Submit for review'.",
]))

# ---------------------------------------------------------------- 9. COMPLIANCE
story.append(H1("9. Compliance e riscos"))
story.append(bullets([
    "NAO automatizar criacao de conta (ban + clawback de pagamentos).",
    "Zero IP de terceiros (anime, marcas) - o projeto ja isola em _ip_quarantine.",
    "IARC e politicas de conteudo obrigatorias em ambas as plataformas.",
    "Mantenha so ganhos legitimos: o DevEx e discricionario.",
    "Impostos: W-8BEN / W-8BEN-E; no BR, declarar receita internacional (Carnê-Leao / PJ).",
]))

# ---------------------------------------------------------------- 10. CHECKLIST
story.append(H1("10. Checklist final (antes do envio real)"))
story.append(bullets([
    "[ ] Conta Roblox criada e verificada (voce)",
    "[ ] DevEx habilitado + W-8BEN (CPF) + PayPal vinculado (voce)",
    "[ ] API key Open Cloud criada; ops/secrets.json preenchido",
    "[ ] Conta Microsoft Partner Center aprovada + IARC + W-8BEN-E",
    "[ ] python certify.py -> 100%",
    "[ ] python submit/pipeline.py --dry-run -> GO",
    "[ ] Secrets do repo GitHub cadastrados (para CI)",
    "[ ] submit.yml: bloco 'Real submission' descomentado",
    "[ ] Clicar 'Run workflow' -> envio automatico completo",
]))
story.append(Spacer(1, 10))
story.append(P("Fonte: documentacao oficial Roblox (DevEx, Creator Rewards) acessada em 2026; "
                "programa Minecraft Marketplace conforme conhecimento consolidado do Partner "
                "Center (valores contratuais sujeitos a alteracao). Este guia nao e aconselhamento "
                "fiscal ou juridico.", "Sub"))

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
    ("Central do Criador (Creator Hub)", "https://create.roblox.com/"),
    ("Documentacao do Criador (hub)", "https://create.roblox.com/docs"),
    ("Roblox DevEx (regras e taxas)", "https://create.roblox.com/docs/production/monetization/developer-exchange"),
    ("Grupos Roblox", "https://www.roblox.com/groups"),
    ("Ajuda Roblox (2FA, impostos)", "https://en.help.roblox.com/hc/pt-br"),
    ("Microsoft Partner Center", "https://partner.microsoft.com/"),
    ("Minecraft - Parceiros (Marketplace)", "https://www.minecraft.net/en-us/partners"),
    ("IARC (classificacao etaria)", "https://www.globalratings.com/"),
    ("PayPal", "https://www.paypal.com/"),
]
story.append(H1("Links uteis (clique para abrir)"))
story.append(P("Roblox muda as URLs de doc com frequencia. Se um link de doc estiver quebrado, "
                "use o hub https://create.roblox.com/docs e procure o topico no menu."))
story.append(_links_table(_LINKS))

# ---------------------------------------------------------------- BUILD
doc = SimpleDocTemplate(OUT, pagesize=A4,
                        leftMargin=18*mm, rightMargin=18*mm,
                        topMargin=16*mm, bottomMargin=16*mm,
                        title="Guia de Aprovacao e Receita - Roblox + Minecraft",
                        author="IconGameDev")
doc.build(story)
print("PDF escrito em:", OUT)

