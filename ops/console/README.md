# IconMineMods — Console Interno (backend)

Backend Python puro (stdlib, sem pip) que é o hub operacional da IconMineMods.
Roda no Coolify e é acessado pelo frontend interno em `website-next/src/app/console`.

## O que faz
- Upload de skins UGC (PNG + nome/tipo) → gera item **100% Roblox-ToS-compliant**
  (regras espelhadas de `compliance/checkers/roblox_check.py`: nomes originais,
  sem IP de terceiros/NSFW/red-flags, preço 1–10000 Robux, descrição obrigatória,
  math de creator-share correta).
- Compliance ao vivo (mesmo scanner) antes de enviar.
- Monta `batch_eligible.json` (itens com imagem) para o `submit/submit_roblox.py`.
- Dispara o envio real via Roblox Open Cloud API (API key only — sem login).

## Rodar localmente
```
cd ops/console
python server.py --host 0.0.0.0 --port 8000
```
No frontend `/console`, cole a URL do túnel (ex: `https://seu-tunnel.exemplo.com`)
no campo "Conectar".

## Coolify
- Tipo: `Python` (ou `Docker` com o Dockerfile ao lado).
- Start command: `python ops/console/server.py --host 0.0.0.0 --port $PORT`
- Exponha a porta e use Cloudflare Tunnel / Flare Tunnel para acesso externo.
- Credenciais Roblox: salve pelo próprio console (`/console` → Configuração),
  ou defina env vars `ROBLOX_API_KEY`, `ROBLOX_GROUP_ID`, `ROBLOX_EXPERIENCE_ID`.
- `ops/secrets.json` já está no `.gitignore` raiz — nunca vai para o repo.

## Endpoints
GET  /api/health · /api/catalog · /api/compliance · /api/secrets · /api/platforms
POST /api/catalog (multipart: name,type,price_robux,image) · /api/build-batch
     /api/submit {test_one:bool} · /api/secrets {api_key,group_id,experience_id}
