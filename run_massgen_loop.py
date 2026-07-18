#!/usr/bin/env python3
"""Loop de geracao mass-skins em lotes pequenos, sem bloquear.
Escreve progresso em massgen_progress.log (append).
Roda via: python run_massgen_loop.py
"""
import os, re, subprocess, sys, time

ROOT = r"C:\Users\forrydev\Desktop\IconGameDev"
os.chdir(ROOT)
SCRIPT = os.path.join(ROOT, "marketplace-content", "scripts", "generate-mass-skins-v2.py")
MASS_DIR = os.path.join(ROOT, "marketplace-content", "output", "mass-skins")
LOG = os.path.join(ROOT, "massgen_progress.log")
TARGET = 10000

def status():
    packs = [d for d in os.listdir(MASS_DIR) if d.startswith("mass_") and os.path.isdir(os.path.join(MASS_DIR, d))]
    indices = [int(re.search(r'_(\d+)$', p).group(1)) for p in packs if re.search(r'_(\d+)$', p)]
    return len(packs), (max(indices) if indices else 0)

# Append-mode log
with open(LOG, "a") as f:
    f.write(f"\n=== START {time.strftime('%H:%M:%S')} ===\n")

count, max_i = status()
print(f"Inicial: {count} packs")

while count < TARGET:
    start_idx = max_i + 1
    # 10/tema = 160 packs por lote
    proc = subprocess.Popen(
        [sys.executable, SCRIPT, "--start-index", str(start_idx), "--theme-count", "10"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    # Wait up to 150s for this batch
    try:
        proc.wait(timeout=150)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()
        with open(LOG, "a") as f:
            f.write(f"  [timeout at idx {start_idx}]\n")
    
    count, max_i = status()
    msg = f"  {time.strftime('%H:%M:%S')} idx {start_idx} -> {count} packs ({count*8} skins)"
    print(msg)
    with open(LOG, "a") as f:
        f.write(msg + "\n")
    
    if count >= TARGET:
        break

print(f"\nFINAL: {count} packs | {count*8} skins")
with open(LOG, "a") as f:
    f.write(f"=== DONE {count} packs ===\n")
