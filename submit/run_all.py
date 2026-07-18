#!/usr/bin/env python3
"""run_all.py -- executor automatico do envio Roblox UGC via Open Cloud API.

100% automatizado APOS a API key estar valida em ops/secrets.json.
NAO faz login, NAO raspa senha, NAO clica "Submit for review" (acao humana).

Fluxo:
  1. Le batch_eligible.json (itens com imagem + tipo suportado).
  2. Para cada item: chama submit_roblox.upload_item (idempotente por nome).
  3. Respeita MAX_ITEMS do submit_roblox (hard cap por run).
  4. Escreve last_run_report.json com sucesso/erro por item.

Uso:
  python submit/run_all.py            # envia o lote elegivel
  python submit/run_all.py --resume   # continua de onde parou (state_roblox.json)
"""
import os
import sys
import json
import argparse

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import submit_roblox as sr  # reutiliza load_creds, upload_item, find_image, TYPE_MAP


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--resume", action="store_true", help="pula itens ja enviados (state)")
    args = ap.parse_args()

    api, gid, uid = sr.load_creds()
    if not (api and gid and uid):
        print("CREDS INCOMPLETAS em ops/secrets.json (api_key, group_id, experience_id).")
        print("Gere a API key no Creator Hub e cole AQUI (nunca a senha da conta).")
        sys.exit(2)
    if str(uid).strip() in ("0", "", "<experience_id>"):
        print("experience_id INVALIDO em ops/secrets.json ('%s')." % uid)
        print("Informe o universe ID real da experience (URL roblox.com/games/XXXX/Nome).")
        sys.exit(2)

    batch = json.load(open(os.path.join(HERE, "batch_eligible.json"), encoding="utf-8"))
    items = batch.get("items", [])
    print("lote elegivel: %d itens" % len(items))

    done = set()
    if args.resume and os.path.isfile(sr.STATE_FILE):
        try:
            done = set(json.load(open(sr.STATE_FILE, encoding="utf-8")).get("uploaded", []))
        except Exception:
            done = set()
    if done:
        print("retomando: %d ja enviados, pulando." % len(done))

    report = {"uploaded": [], "skipped": [], "errors": []}
    sent = len(done)
    for it in items:
        name = it.get("name")
        if name in done:
            continue
        ok, msg = sr.upload_item(api, gid, uid, it)
        if ok:
            report["uploaded"].append(name)
            done.add(name)
            sent += 1
            print("  OK   %s" % name)
        else:
            report["errors"].append({"name": name, "msg": msg})
            print("  ERR  %s -> %s" % (name, msg[:120]))
        # persist state a cada item (crash-safe / idempotente)
        json.dump({"uploaded": sorted(done)}, open(sr.STATE_FILE, "w", encoding="utf-8"), indent=2)
        if sent >= sr.MAX_ITEMS:
            print("MAX_ITEMS (%d) atingido neste run. Rode --resume para continuar." % sr.MAX_ITEMS)
            break

    json.dump(report, open(sr.REPORT_FILE, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    print("\nRESUMO: uploaded=%d skipped=%d errors=%d" % (
        len(report["uploaded"]), len(report["skipped"]), len(report["errors"])))
    print("relatorio: %s" % sr.REPORT_FILE)


if __name__ == "__main__":
    main()
