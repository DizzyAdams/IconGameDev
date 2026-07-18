#!/usr/bin/env python3
"""Orquestrador diario do pipeline IconGameDev (idempotente, stdlib only).

Sequencia:
  a. scale-products.py     -> incremento diario de packs (batch configuravel)
  b. package_incremental.py-> empacota dirs novos em submission_mcpacks/
  c. quarantine_ip.py      -> move packs com IP bloqueado p/ _ip_quarantine/
  d. submit_gate.py --audit-> gate GO/NO-GO (ABORTA se NO-GO, exit 2)
  e. compute_payouts.py    -> comissoes de afiliados -> affiliates/payouts.json
  f. certify.py            -> suite completa de certificacao (6 gates)
  g. out/inventory_report.json -> atualiza contagens + entrada em history

Uso:
  python ops/run_daily.py                 # batch padrao (500)
  python ops/run_daily.py --batch 1000
  python ops/run_daily.py --dry-run       # so mostra os passos, nao executa
  python ops/run_daily.py --skip-certify  # pula certify.py (rapido p/ teste)

Agendamento:
  Windows (Task Scheduler, uma vez):
    schtasks /create /tn "IconGameDev-Daily" /sc daily /st 06:00 ^
      /tr "\"C:\\Python313\\python.exe\" C:\\Users\\forrydev\\Desktop\\IconGameDev\\ops\\run_daily.py"
  (ajuste o caminho do python; `where python` mostra o seu)
  Linux/macOS (cron):
    0 6 * * * cd /caminho/IconGameDev && python ops/run_daily.py >> ops/run_daily.log 2>&1

Exit code: 0 so se TODOS os passos passarem; 2 se o submit_gate der NO-GO;
1 para qualquer outra falha.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MC = ROOT / "marketplace-content"
INVENTORY = ROOT / "out" / "inventory_report.json"
EXTS = (".mcpack", ".mctemplate", ".mcworld")


def ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def log(msg: str) -> None:
    print(f"[{ts()}] {msg}", flush=True)


def run_step(label: str, cmd: list[str], cwd: Path) -> bool:
    log(f">>> {label}: {' '.join(cmd)}")
    r = subprocess.run(cmd, cwd=str(cwd))
    if r.returncode != 0:
        log(f"!!! {label} FALHOU (exit {r.returncode})")
        return False
    log(f"OK  {label}")
    return True


def count_packs() -> dict[str, int]:
    d = ROOT / "submission_mcpacks"
    mcpack = sum(1 for p in d.glob("*.mcpack"))
    mctemplate = sum(1 for p in d.glob("*.mctemplate"))
    return {"mcpack": mcpack, "mctemplate": mctemplate, "total": mcpack + mctemplate}


def update_inventory(after: dict[str, int], gates: dict[str, str], created: int,
                     packaged: int, quarantined: int) -> None:
    data: dict = {}
    if INVENTORY.exists():
        try:
            data = json.loads(INVENTORY.read_text(encoding="utf-8"))
        except Exception:
            data = {}
    before = data.get("after") or count_packs()
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "before": before,
        "after": after,
        "delta": {k: after[k] - before.get(k, 0) for k in after},
        "created_by_scale_products": created,
        "packaged_this_round": packaged,
        "quarantined_this_round": quarantined,
        "gates": gates,
    }
    data.update({
        "timestamp": entry["timestamp"],
        "before": before,
        "after": after,
        "delta": entry["delta"],
        "gates": gates,
        "quarantined_this_round": quarantined,
    })
    history = data.get("history") or []
    history.append(entry)
    data["history"] = history[-100:]  # keep last 100 runs
    INVENTORY.parent.mkdir(exist_ok=True)
    INVENTORY.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    log(f"inventario atualizado: {INVENTORY} (history={len(data['history'])})")


def parse_created(stdout_text: str) -> int:
    try:
        return int(json.loads(stdout_text.strip().splitlines()[-1]).get("created", 0))
    except Exception:
        return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Orquestrador diario IconGameDev")
    ap.add_argument("--batch", type=int, default=500, help="packs novos por dia (default 500)")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--dry-run", action="store_true", help="mostra passos sem executar")
    ap.add_argument("--skip-certify", action="store_true", help="pula certify.py")
    args = ap.parse_args()

    py = sys.executable
    steps = [
        ("scale-products", [py, "scripts/scale-products.py", "--target", "999999",
                            "--batch", str(args.batch), "--seed", str(args.seed)], MC),
        ("package_incremental", [py, "package_incremental.py"], ROOT),
        ("quarantine_ip", [py, "marketplace-content/scripts/quarantine_ip.py"], ROOT),
        ("submit_gate --audit", [py, "compliance/checks/submit_gate.py", "--audit"], ROOT),
        ("compute_payouts", [py, "affiliates/compute_payouts.py"], ROOT),
    ]
    if not args.skip_certify:
        steps.append(("certify", [py, "certify.py"], ROOT))

    if args.dry_run:
        log("DRY-RUN -- passos que seriam executados:")
        for label, cmd, cwd in steps:
            print(f"  [{cwd}] {' '.join(cmd)}")
        log("fim do dry-run (nada executado)")
        return 0

    log(f"=== run_daily iniciado (batch={args.batch}) ===")
    before = count_packs()
    created = 0
    gates: dict[str, str] = {}

    # a. scale-products (captura stdout p/ saber quantos criou)
    label, cmd, cwd = steps[0]
    log(f">>> {label}: {' '.join(cmd)}")
    r = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True)
    sys.stdout.write(r.stdout)
    if r.returncode != 0:
        sys.stderr.write(r.stderr)
        log(f"!!! {label} FALHOU (exit {r.returncode})")
        return 1
    created = parse_created(r.stdout)
    log(f"OK  {label} (created={created})")

    # b + c. empacotar e quarentenar
    for label, cmd, cwd in steps[1:3]:
        if not run_step(label, cmd, cwd):
            return 1
    mid = count_packs()
    packaged = max(0, mid["total"] - before["total"])

    # d. submit_gate --audit -- ABORTA se NO-GO
    label, cmd, cwd = steps[3]
    log(f">>> {label}: {' '.join(cmd)}")
    r = subprocess.run(cmd, cwd=str(cwd))
    if r.returncode != 0:
        gates["submit_gate_audit"] = "NO-GO"
        after = count_packs()
        quarantined = max(0, before["total"] + packaged - after["total"])
        update_inventory(after, gates, created, packaged, quarantined)
        log("!!! submit_gate NO-GO -- abortando. Verifique o output acima.")
        return 2
    gates["submit_gate_audit"] = "GO"
    log("OK  submit_gate --audit (GO)")

    after_gate = count_packs()
    quarantined = max(0, mid["total"] - after_gate["total"])

    # e. payouts
    label, cmd, cwd = steps[4]
    if not run_step(label, cmd, cwd):
        return 1

    # f. certify
    if not args.skip_certify:
        label, cmd, cwd = steps[5]
        if not run_step(label, cmd, cwd):
            gates["certify"] = "FAIL"
            update_inventory(count_packs(), gates, created, packaged, quarantined)
            return 1
        gates["certify"] = "PASS"

    # g. inventario
    update_inventory(count_packs(), gates, created, packaged, quarantined)
    log("=== run_daily concluido com sucesso ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
