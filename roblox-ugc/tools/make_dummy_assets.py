#!/usr/bin/env python3
"""Gera imagens PNG placeholder em roblox-ugc/assets/ para destravar o dry-run.

SO PARA TESTE DE PIPELINE (--test-one). Nao use em upload real: Roblox exige
arte real nos templates de shirt/pants/accessory ou rejeita na moderacao.
Substitua pelos PNGs de arte reais antes de publicar para venda.

Gera <name>.png (512x512, cor deterministica) para itens sem imagem.
"""
import json
import os
import struct
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
RUG = os.path.join(ROOT, "roblox-ugc")
CATALOG = os.path.join(RUG, "catalog", "roblox_catalog.json")
ASSETS = os.path.join(RUG, "assets")


def write_png(path, r, g, b):
    w = h = 512
    raw = b"".join(b"\x00" + struct.pack(">BBB", r, g, b) * w for _ in range(h))

    def chunk(typ, data):
        c = typ + data
        return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)

    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n")
        f.write(chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)))
        f.write(chunk(b"IDAT", zlib.compress(raw)))
        f.write(chunk(b"IEND", b""))


def main():
    data = json.load(open(CATALOG, encoding="utf-8"))
    os.makedirs(ASSETS, exist_ok=True)
    made = 0
    for x in data["items"]:
        if x.get("type") == "game_pass":
            continue
        name = x["name"]
        if any(os.path.exists(os.path.join(ASSETS, name + ext))
               for ext in (".png", ".jpg", ".jpeg")):
            continue
        h = abs(hash(name)) % 360
        r = (h * 123) % 256
        g = (h * 211) % 256
        b = (h * 337) % 256
        write_png(os.path.join(ASSETS, name + ".png"), r, g, b)
        made += 1
    print(f"placeholders gerados: {made}  (em {ASSETS})")
    print("AVISO: substitua por arte real antes de qualquer upload para venda.")


if __name__ == "__main__":
    main()
