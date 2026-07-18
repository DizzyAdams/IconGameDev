# Recruitment Playbook — IconMineMods Affiliate + Agency Engine

Status: DRAFT, pronto para aprovação. Nada aqui é enviado automaticamente.
O agente só dispara mensagens após o usuário aprovar explicitamente (gated).

## Objetivo
Tornar IconMineMods a maior plataforma de skins Roblox + Minecraft Bedrock do
mercado via (1) volume de catálogo compliant e (2) rede de afiliados/agências
que geram as vendas que levam a $1M em skins.

## 1. Público-alvo

### Afiliados (comissão 15%, pagamento Pix/PayPal)
- Criadores de conteúdo Roblox/Bedrock (YouTube, TikTok, Twitch, Discord).
- Donos de servidor Discord / comunidades de Minecraft.
- Páginas de dicas/skins (blog, Pinterest, Instagram).

### Agências (revshare 30%, fast-track de aprovação)
- Estúdios pequenos de skin/texture pack.
- Freelancers de modelagem 3D/Minecraft.
- Produtores de conteúdo que já vendem packs próprios em outro marketplace.

## 2. Proposta de valor (copy base — adaptar por canal)
- "Maior catálogo compliant do mercado, aprovado Roblox + Bedrock."
- "Comissão 15% transparente, ledger público, pagamento Pix/PayPal."
- "Agências: 30% revshare + fast-track (aprovação acelerada, menos retrabalho)."
- "Você divulga, a gente cuida de compliance, submissão e pagamento."

## 3. Canais de outreach (todos travados — aprovar antes de enviar)
- E-mail (contato@icongamedev.com como remetente; responder cure do /partner).
- Discord de criadores Roblox/Bedrock (mensagem direta, não spam em canal).
- Reddit r/Roblox, r/Minecraft (post útil, não promo crua).
- Direct no TikTok/YouTube para canais de skin packs.

## 4. Sequência (cadência sugerida, após aprovação)
1. Apresentação (1 msg): quem somos + proposta.
2. Follow-up (após 3 dias, só se sem resposta): link de inscrição + ledger público.
3. Ativação: enviar link /afiliados?ref=CODE ou criar agência via /api/agencies.
4. Nunca mais de 1 msg/semana. Opt-out imediato.

## 5. Como o agente registra
- Afiliado novo → editar affiliates/affiliates.csv (handle, referrals, revenue_usd)
  e rodar python affiliates/compute_payouts.py.
- Agência nova → POST /api/agencies (name, email, terms='revshare 30%', fast_track=true).
- Sempre registrar em .loops/funnel.md e .loops/agency.md.

## 6. Guardrails
- IP_BLOCKED (anime/kawaii/franchise) nunca é tema de pack promovido.
- Sem prometer receita garantida. Sem spam. LGPD: dados de contato só com base
  em interesse legítimo + opt-out.
- Pagamentos só após aprovação humana (loop affiliate-payout-integrity apenas valida math).

## 7. Próximo passo
Usuário aprova o envio → ativar outreach_loop (cron, gated) que executa a
sequência acima e registra resultados. Até lá, este arquivo é only-planning.
