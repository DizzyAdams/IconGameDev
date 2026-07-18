#!/usr/bin/env python3
"""Gera GUIA_ENVIO_ROBLOX_UGC.pdf no Desktop via Pillow (sem deps externas)."""
import os
from PIL import Image, ImageDraw, ImageFont

DESKTOP = os.path.join(os.environ["USERPROFILE"], "Desktop")
OUT = os.path.join(DESKTOP, "GUIA_ENVIO_ROBLOX_UGC.pdf")

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
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines

def page(title, blocks, footer):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    # header bar
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
        elif b[0] == "b":  # bullet
            d.text((72, y), "•", font=font(20, True), fill=ACCENT2)
            for i, ln in enumerate(wrap(d, b[1], font(20), W - 160)):
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

pages = []

pages.append(page("GUIA PRATICO — ENVIO ROBLOX UGC (IconHub)", [
    ("p", "Este guia explica como as 10.750 skins do catalogo foram deixadas 100% prontas para aprovacao e como enviar tudo de maneira automatica via Open Cloud API. Nada de login/senha: o envio usa a API key do grupo, que e legitimo e permitido pela Roblox."),
    ("sep", ""),
    ("h", "STATUS ATUAL (conferido)"),
    ("b", "10.750 / 10.750 itens com imagem gerada (PNG 512x512, mono-dark + neon)."),
    ("b", "submit_roblox.py corrigido: creationContext usa groupId (resolvido 403) + find_image normaliza espaco/underscore."),
    ("b", "batch_eligible.json contem as 10.750 skins prontas."),
    ("b", ".gitignore cobre os 3 arquivos de credencial (sem vazamento de API key)."),
    ("warn", "PENDENTE DE VOCE (acao humana):\n1) API key NOVA valida no ops/secrets.json (a atual retorna 403).\n2) universe_id real da experience (hoje '0' -> game_passes quebram).\nSem esses dois, 0 envios acontecem."),
], "IconHub UGC — pagina 1/6"))

pages.append(page("1. POR QUE SO 1.240 FUNCIONAVAM (e como resolvemos)", [
    ("p", "O relatorio mostrava 1.240 de 10.750 com imagem. Investigacao no disco revelou DOIS bugs, nao falta de arte:"),
    ("h", "Bug A — imagens nao geradas"),
    ("b", "roblox-ugc/assets/ tinha so 720 arquivos. O gerador (tools/generate_missing_assets.py) nao tinha rodado para as 9.510 restantes."),
    ("b", "Correcao: rodamos o gerador -> criou 6.703 novas imagens. Agora 7.423 arquivos (nomes repetidos reduzem o total unico)."),
    ("h", "Bug B — find_image nao casava o nome"),
    ("p", "O gerador salva 'Crimson_Shirt.png' (espaco vira underscore). Mas find_image procurava 'Crimson Shirt.png' (com espaco). Resultado: mesmo as imagens existentes nao eram encontradas pelo uploader."),
    ("b", "Correcao em submit_roblox.py: find_image agora testa ambos os formatos (com e sem underscore)."),
    ("sep", ""),
    ("p", "Apos os dois fixes: 10.750 / 10.750 skins tem imagem validada. Esse era o 'porque so 1240' — era bug de pipeline, nao de conteudo."),
], "IconHub UGC — pagina 2/6"))

pages.append(page("2. COMO FUNCIONA O PIPELINE (100% automatico, sem login)", [
    ("h", "Fluxo"),
    ("b", "Catalogo: roblox-ugc/catalog/roblox_catalog.json (10.750 itens: name, type, price)."),
    ("b", "Imagens: roblox-ugc/assets/<Nome>.png (geradas pelo script de missing assets)."),
    ("b", "Credenciais: ops/secrets.json -> roblox.api_key / group_id / experience_id (gitignored)."),
    ("b", "Upload: submit_roblox.py faz POST multipart na Open Cloud API (assets/v1/.../create-request) com x-api-key."),
    ("b", "Executor: submit/run_all.py percorre o lote, envia 1 por 1, salva progresso em state_roblox.json (idempotente) e escreve last_run_report.json."),
    ("h", "O que e enviado por tipo"),
    ("b", "classic_shirt / classic_pants / avatar_accessory: upload binario da imagem + metadata."),
    ("b", "game_pass (2.100): criado via API com displayName+descricao; icone depois manual no Creator Hub. Exige universe_id valido."),
    ("sep", ""),
    ("code", "python submit/run_all.py            # envia o lote\npython submit/run_all.py --resume   # continua de onde parou"),
], "IconHub UGC — pagina 3/6"))

pages.append(page("3. UNIVERSE ID — O QUE E E ONDE ACHAR", [
    ("p", "universe_id e o numero da sua EXPERIENCE (jogo) na Roblox. Aparece na URL:"),
    ("code", "https://www.roblox.com/games/XXXXXX/Nome-Da-Experience\n                         ^^^^^^  <-- este numero e o universe_id"),
    ("h", "Por que importa"),
    ("b", "So e obrigatorio para criar GAME PASSES (2.100 itens). Eles sao vinculados a uma experience."),
    ("b", "Shirts / pants / accessories usam so a API key + group_id. Nao precisam de universe_id."),
    ("warn", "Hoje experience_id = '0' (placeholder). Enquanto estiver assim, os 2.100 game_passes falham em 'INVALID'. As outras 8.650 skins enviam normalmente."),
    ("h", "Como preencher"),
    ("b", "No Creator Hub, abra a experience -> copie o numero da URL."),
    ("b", "Cole em ops/secrets.json:  \"experience_id\": \"1234567890\"  (numero real, sem aspas de placeholder)."),
], "IconHub UGC — pagina 4/6"))

pages.append(page("4. PASSOS PARA ENVIAR TUDO (voce faz o minimo, eu rodo)", [
    ("h", "Passo 1 — API key (voce, 1x no Creator Hub)"),
    ("b", "Creator Hub -> Develop -> API Keys -> New Key. Copie a key que aparece UMA vez."),
    ("b", "NUNCA mande a SENHA da conta. So a API key. Ela e diferente do login."),
    ("h", "Passo 2 — cole aqui no chat"),
    ("code", "api_key: <cole a key aqui>\nexperience_id: <numero da URL do jogo>"),
    ("h", "Passo 3 — eu executo (automatico)"),
    ("b", "Gravo em ops/secrets.json (ja gitignored)."),
    ("b", "Rodo: python submit/run_all.py  (envia 8.650 nao-gamepass + 2.100 se universe_id ok)."),
    ("b", "Se bater o MAX_ITEMS por run, rodo --resume ate acabar. Relatorio em last_run_report.json."),
    ("warn", "NAO AUTOMATIZO: login/senha no portal (ToS -> ban + clawback) nem o clique final 'Submit for review' (acao humana). O bot para no human_gate e VOCE revisa/clica."),
], "IconHub UGC — pagina 5/6"))

pages.append(page("5. LIMITES, ToS E CHECKLIST FINAL", [
    ("h", "Limites tecnicos (reais)"),
    ("b", "MAX_ITEMS por run = 500 (hard cap em submit_roblox.py). Use --resume para o resto."),
    ("b", "Imagem <= 10MB e >= 1px. As geradas sao 512x512 PNG, ok."),
    ("b", "Open Cloud tem rate limit: o script ja tem retry/backoff."),
    ("h", "ToS / seguranca"),
    ("b", "Envio via API key de grupo = permitido. Login botado com senha = PROIBIDO (ban + clawback)."),
    ("b", "A senha que voce colou no chat esta exposta: troque-a na conta."),
    ("b", "Submit final de aprovacao e humano (ToS + clawback). Bot para no gate."),
    ("h", "Checklist antes de mandar a key"),
    ("b", "[ ] API key nova gerada no Creator Hub."),
    ("b", "[ ] universe_id real preenchido (ou aceite que game_passes falham por ora)."),
    ("b", "[ ] ops/secrets.json nao esta no git (gitignore confere)."),
    ("sep", ""),
    ("p", "Pronto. Assim que a key + universe_id chegarem, rodo o envio das 10.750 skins 100% automatico."),
], "IconHub UGC — pagina 6/6"))

# save as PDF (one image per page)
pages[0].save(OUT, "PDF", save_all=True, append_images=pages[1:])
print("PDF gerado:", OUT)
print("paginas:", len(pages), "tamanho:", os.path.getsize(OUT), "bytes")
