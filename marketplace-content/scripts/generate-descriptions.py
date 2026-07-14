"""Generate EN + PT store descriptions for all packs."""
import json, os
from pathlib import Path

MC = Path(__file__).resolve().parent.parent
OUT = MC / "descriptions"
OUT.mkdir(exist_ok=True)

SOURCE_DIRS = {"skin-packs": "skin_pack", "texture-packs": "resources", "world-templates": "world_template", "mashup-packs": "mashup"}
CAT_NAMES = {"skin_pack": "Skin Pack", "resources": "Texture Pack", "world_template": "World", "mashup": "Mashup"}
CAT_PT = {"skin_pack": "Pacote de Skins", "resources": "Pacote de Texturas", "world_template": "Mundo", "mashup": "Pacote Mashup"}

FEATURES_EN = {
    "skin_pack": ["✓ 8 unique skins with custom designs", "✓ High-resolution 64x64 textures", "✓ Easy to apply in-game", "✓ Works on all Bedrock platforms", "✓ Regular updates"],
    "resources": ["✓ Custom block textures", "✓ Optimized for performance", "✓ Works on mobile, console & PC", "✓ Easy installation", "✓ Compatible with latest Minecraft version"],
    "world_template": ["✓ Ready-to-play world", "✓ Custom-built terrain and structures", "✓ Game rules pre-configured", "✓ Great for multiplayer servers", "✓ Fully survival-compatible"],
    "mashup": ["✓ Complete world + texture transformation", "✓ Custom-built terrain", "✓ Matching texture pack included", "✓ Ready to play instantly", "✓ Immersive themed experience"],
}

FEATURES_PT = {
    "skin_pack": ["✓ 8 skins únicas com designs personalizados", "✓ Texturas de alta resolução 64x64", "✓ Fácil de aplicar no jogo", "✓ Funciona em todas plataformas Bedrock", "✓ Atualizações regulares"],
    "resources": ["✓ Texturas de blocos personalizadas", "✓ Otimizado para performance", "✓ Funciona em celular, console e PC", "✓ Instalação fácil", "✓ Compatível com a versão mais recente"],
    "world_template": ["✓ Mundo pronto para jogar", "✓ Terreno e estruturas personalizados", "✓ Regras de jogo pré-configuradas", "✓ Ótimo para servidores multiplayer", "✓ Totalmente compatível com survival"],
    "mashup": ["✓ Transformação completa de mundo + texturas", "✓ Terreno personalizado", "✓ Pacote de texturas combinando incluso", "✓ Pronto para jogar instantaneamente", "✓ Experiência temática imersiva"],
}

def gen_desc_en(pack, ptype, name, desc):
    cat = CAT_NAMES[ptype]
    features = "\n".join(FEATURES_EN[ptype])
    return f"""§n{name}§r

{desc}

§nFeatures:§r
{features}

§nTags:§r {cat.lower()}, minecraft {cat.lower()}, bedrock edition, {name.lower()}

© Bedrock Minemods — All rights reserved"""

def gen_desc_pt(pack, ptype, name, desc):
    cat_pt = CAT_PT[ptype]
    features = "\n".join(FEATURES_PT[ptype])
    return f"""§n{name}§r

{desc}

§nRecursos:§r
{features}

§nTags:§r {cat_pt.lower()}, minecraft bedrock, {name.lower()}

© Bedrock Minemods — Todos os direitos reservados"""

def main():
    for sd, ptype in SOURCE_DIRS.items():
        src = MC / sd
        if not src.exists():
            continue
        for pd in sorted(src.iterdir()):
            if not pd.is_dir() or pd.name.startswith("."):
                continue
            mf = pd / "manifest.json"
            if not mf.exists():
                continue
            data = json.loads(mf.read_text())
            header = data.get("header", {})
            name = header.get("name", pd.name)
            desc = header.get("description", f"A {CAT_NAMES[ptype].lower()} for Minecraft Bedrock Edition.")
            
            desc_en = gen_desc_en(pd.name, ptype, name, desc)
            desc_pt = gen_desc_pt(pd.name, ptype, name, desc)
            
            pack_out = OUT / pd.name
            pack_out.mkdir(exist_ok=True)
            (pack_out / "description_en.txt").write_text(desc_en, encoding="utf-8")
            (pack_out / "description_pt.txt").write_text(desc_pt, encoding="utf-8")
    
    # Generate master index
    index = {"generated": [], "count": 0}
    for pd in sorted(OUT.iterdir()):
        if pd.is_dir() and (pd / "description_en.txt").exists():
            en = (pd / "description_en.txt").read_text(encoding="utf-8")
            pt = (pd / "description_pt.txt").read_text(encoding="utf-8")
            index["generated"].append({"pack": pd.name, "en_preview": en[:80], "pt_preview": pt[:80]})
            index["count"] += 1
    
    with open(OUT / "_index.json", "w") as f:
        json.dump(index, f, indent=2)
    
    print(f"=== DESCRIPTIONS GENERATED ===")
    print(f"  Total packs: {index['count']}")
    print(f"  Output: {OUT}")

if __name__ == "__main__":
    main()
