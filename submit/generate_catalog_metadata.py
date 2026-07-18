#!/usr/bin/env python3
"""Generate store metadata for all mass-skin packs.

Scans marketplace-content/output/mass-skins/ for pack directories,
reads each manifest.json, and produces a catalog metadata file at
marketplace-content/catalog/PACK_METADATA.json.

For each pack the script generates:
  - Store description in English and Brazilian Portuguese
  - SEO keywords (5-10)
  - Marketplace tags (5-10)
  - Suggested price ($2.99 / 490 MC for skin_pack)
"""

import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent  # IconGameDev
MASS_SKINS_DIR = ROOT / "marketplace-content" / "output" / "mass-skins"
CATALOG_DIR = ROOT / "marketplace-content" / "catalog"
OUTPUT_FILE = CATALOG_DIR / "PACK_METADATA.json"

# ── Theme metadata ──────────────────────────────────────────────────────────
# Each theme has: readable name, description (EN + PT), keywords, and tags.
# The dir pattern is: mass_{theme-id}_XXXXX

THEME_META = {
    "clay-bakery": {
        "theme_en": "Clay Bakery",
        "theme_pt": "Padaria de Argila",
        "desc_en": (
            "A charming clay-textured skin collection with warm browns, terracottas, "
            "and soft earth tones. Each skin brings a handcrafted, pottery-inspired "
            "look to your Minecraft adventures."
        ),
        "desc_pt": (
            "Uma coleção de skins com textura de argila, com tons quentes de marrom, "
            "terracota e terra suave. Cada skin traz um visual artesanal inspirado em "
            "cerâmica para suas aventuras no Minecraft."
        ),
        "keywords": ["clay bakery", "clay texture", "terracotta", "pottery", "earthy", "warm tones"],
        "tags": ["Skin", "Clay", "Pottery", "Terracotta", "Earth", "Warm"],
    },
    "royal-gold": {
        "theme_en": "Royal Gold",
        "theme_pt": "Ouro Real",
        "desc_en": (
            "Regal gold-accented skins with luxurious royal blues, purples, "
            "and gleaming gold trim. Fit for a king or queen in your Minecraft world."
        ),
        "desc_pt": (
            "Skins com detalhes dourados e luxuosos, combinando azuis reais, "
            "roxos e acabamentos dourados brilhantes. Adequado para um rei ou "
            "rainha no seu mundo Minecraft."
        ),
        "keywords": ["royal gold", "gold armor", "luxury", "royal", "regal", "premium", "king", "queen"],
        "tags": ["Skin", "Gold", "Royal", "Luxury", "Regal", "Premium", "Armor"],
    },
    "neon-mint": {
        "theme_en": "Neon Mint",
        "theme_pt": "Menta Neon",
        "desc_en": (
            "Vibrant neon green and mint-colored skins with a futuristic glow. "
            "Perfect for players who love bright, energetic styles that pop."
        ),
        "desc_pt": (
            "Skins vibrantes em verde neon e menta com um brilho futurista. "
            "Perfeito para jogadores que amam estilos brilhantes e energéticos "
            "que se destacam."
        ),
        "keywords": ["neon mint", "neon green", "mint", "glow", "futuristic", "bright", "vibrant"],
        "tags": ["Skin", "Neon", "Mint", "Green", "Futuristic", "Glow", "Bright"],
    },
    "ember-ash": {
        "theme_en": "Ember & Ash",
        "theme_pt": "Brasa e Cinzas",
        "desc_en": (
            "Dark, smoky skins with glowing ember-orange accents. Inspired by "
            "volcanic landscapes and the smoldering remains of a campfire."
        ),
        "desc_pt": (
            "Skins escuras e esfumaçadas com detalhes laranja-brasa brilhantes. "
            "Inspirado em paisagens vulcânicas e nos restos fumegantes de uma "
            "fogueira."
        ),
        "keywords": ["ember ash", "dark skin", "volcanic", "smoky", "fire", "orange glow", "campfire"],
        "tags": ["Skin", "Dark", "Ember", "Fire", "Volcanic", "Smoky", "Orange"],
    },
    "ocean-depths": {
        "theme_en": "Ocean Depths",
        "theme_pt": "Profundezas do Oceano",
        "desc_en": (
            "Deep blue and teal skins inspired by the mysterious depths of the ocean. "
            "Featuring aquatic patterns, wave motifs, and bioluminescent accents."
        ),
        "desc_pt": (
            "Skins em azul profundo e verde-azulado inspiradas nas misteriosas "
            "profundezas do oceano. Com padrões aquáticos, motivos de ondas e "
            "detalhes bioluminescentes."
        ),
        "keywords": ["ocean depths", "aquatic", "deep blue", "teal", "underwater", "sea", "bioluminescent"],
        "tags": ["Skin", "Ocean", "Aquatic", "Blue", "Underwater", "Sea", "Deep"],
    },
    "candy-summers": {
        "theme_en": "Candy Summers",
        "theme_pt": "Verão Doce",
        "desc_en": (
            "Sweet, colorful skins inspired by summer treats and candy. Bright pinks, "
            "yellows, and pastels create a fun, playful vibe for your character."
        ),
        "desc_pt": (
            "Skins doces e coloridas inspiradas em guloseimas de verão. Rosa vivo, "
            "amarelo e tons pastel criam uma vibe divertida e lúdica para seu "
            "personagem."
        ),
        "keywords": ["candy summer", "pastel", "sweet", "colorful", "summer", "playful", "bright", "pink"],
        "tags": ["Skin", "Candy", "Summer", "Pastel", "Colorful", "Sweet", "Playful"],
    },
    "toxic-waste": {
        "theme_en": "Toxic Waste",
        "theme_pt": "Lixo Tóxico",
        "desc_en": (
            "Hazardous green and yellow skins with a radioactive, post-apocalyptic "
            "style. Perfect for survivors of the wasteland."
        ),
        "desc_pt": (
            "Skins perigosas em verde e amarelo com estilo radioativo e "
            "pós-apocalíptico. Perfeito para sobreviventes do deserto."
        ),
        "keywords": ["toxic waste", "radioactive", "post-apocalyptic", "hazard", "green", "wasteland"],
        "tags": ["Skin", "Toxic", "Radioactive", "Apocalyptic", "Hazard", "Green", "Wasteland"],
    },
    "deep-space": {
        "theme_en": "Deep Space",
        "theme_pt": "Espaço Profundo",
        "desc_en": (
            "Cosmic skins with starry patterns, nebula gradients, and deep "
            "space blacks and purples. Explore the universe in style."
        ),
        "desc_pt": (
            "Skins cósmicas com padrões estrelados, gradientes de nebulosa e "
            "tons profundos de preto e roxo. Explore o universo com estilo."
        ),
        "keywords": ["deep space", "cosmic", "nebula", "stars", "galaxy", "purple", "astronaut"],
        "tags": ["Skin", "Space", "Cosmic", "Galaxy", "Stars", "Nebula", "Sci-Fi"],
    },
    "sunset-safari": {
        "theme_en": "Sunset Safari",
        "theme_pt": "Safari ao Pôr do Sol",
        "desc_en": (
            "Warm sunset-orange and savanna-inspired skins with animal patterns "
            "and tribal accents. Adventure awaits on the savanna."
        ),
        "desc_pt": (
            "Skins em laranja-pôr-do-sol inspiradas na savana, com padrões "
            "animais e detalhes tribais. A aventura espera na savana."
        ),
        "keywords": ["sunset safari", "savanna", "tribal", "animal print", "orange", "warm", "adventure"],
        "tags": ["Skin", "Safari", "Sunset", "Savanna", "Tribal", "Animal", "Adventure"],
    },
    "neon-streets": {
        "theme_en": "Neon Streets",
        "theme_pt": "Ruas de Neon",
        "desc_en": (
            "Cyberpunk-inspired skins with bright neon pink, blue, and purple "
            "strips against dark backgrounds. Light up the city streets."
        ),
        "desc_pt": (
            "Skins inspiradas no cyberpunk com faixas brilhantes em neon rosa, "
            "azul e roxo sobre fundos escuros. Ilumine as ruas da cidade."
        ),
        "keywords": ["neon streets", "cyberpunk", "neon", "city", "urban", "futuristic", "glow"],
        "tags": ["Skin", "Cyberpunk", "Neon", "Urban", "City", "Futuristic", "Street"],
    },
    "safari-dust": {
        "theme_en": "Safari Dust",
        "theme_pt": "Po de Safari",
        "desc_en": (
            "Dusty earth-tone skins with khaki, olive, and sand colors. "
            "Built for explorers trekking across deserts and dry savannas."
        ),
        "desc_pt": (
            "Skins em tons terrosos e empoeirados com cores cáqui, oliva e areia. "
            "Feito para exploradores atravessando desertos e savanas secas."
        ),
        "keywords": ["safari dust", "khaki", "olive", "sand", "desert", "earth tones", "explorer"],
        "tags": ["Skin", "Safari", "Desert", "Earth", "Khaki", "Explorer", "Camouflage"],
    },
    "midnight-jazz": {
        "theme_en": "Midnight Jazz",
        "theme_pt": "Jazz da Meia-Noite",
        "desc_en": (
            "Smooth midnight-blue and black skins with elegant jazz-inspired "
            "patterns. Channel the cool vibes of a late-night jazz club."
        ),
        "desc_pt": (
            "Skins elegantes em azul meia-noite e preto com padrões inspirados "
            "no jazz. Canalize as vibrações legais de um clube de jazz noturno."
        ),
        "keywords": ["midnight jazz", "midnight blue", "black", "elegant", "smooth", "jazz", "night"],
        "tags": ["Skin", "Midnight", "Jazz", "Elegant", "Night", "Blue", "Dark"],
    },
    "slime-caves": {
        "theme_en": "Slime Caves",
        "theme_pt": "Cavernas de Gosma",
        "desc_en": (
            "Gooey green and lime skins with a slimy, cave-dweller aesthetic. "
            "Perfect for players who love the underground and all things sticky."
        ),
        "desc_pt": (
            "Skins pegajosas em verde e limão com uma estética de morador de "
            "caverna. Perfeito para jogadores que amam o subterrâneo e tudo "
            "que é grudento."
        ),
        "keywords": ["slime caves", "slime", "green", "gooey", "cave", "sticky", "underground"],
        "tags": ["Skin", "Slime", "Green", "Cave", "Gooey", "Underground", "Sticky"],
    },
    "sakura-garden": {
        "theme_en": "Sakura Garden",
        "theme_pt": "Jardim de Sakura",
        "desc_en": (
            "Delicate pink and white skins inspired by cherry blossoms in bloom. "
            "Soft, floral patterns bring the beauty of spring to your character."
        ),
        "desc_pt": (
            "Skins delicadas em rosa e branco inspiradas nas flores de cerejeira. "
            "Padrões florais suaves trazem a beleza da primavera ao seu personagem."
        ),
        "keywords": ["sakura garden", "cherry blossom", "floral", "pink", "spring", "delicate", "japanese"],
        "tags": ["Skin", "Sakura", "Cherry Blossom", "Floral", "Pink", "Spring", "Japanese"],
    },
    "retro-arcade": {
        "theme_en": "Retro Arcade",
        "theme_pt": "Arcade Retrô",
        "desc_en": (
            "Pixel-perfect retro skins inspired by classic arcade games. "
            "Bold primary colors and 8-bit aesthetics for nostalgic gamers."
        ),
        "desc_pt": (
            "Skins retrô perfeitas em pixel inspiradas em jogos de arcade clássicos. "
            "Cores primárias ousadas e estética 8-bit para jogadores nostálgicos."
        ),
        "keywords": ["retro arcade", "8-bit", "pixel art", "retro", "classic games", "nostalgic", "arcade"],
        "tags": ["Skin", "Retro", "Arcade", "8-Bit", "Pixel", "Nostalgic", "Classic"],
    },
}

# Default metadata for unknown themes
DEFAULT_META = {
    "theme_en": "Custom",
    "theme_pt": "Personalizado",
    "desc_en": "A unique skin pack with custom designs for your Minecraft character.",
    "desc_pt": "Um pacote de skins único com designs personalizados para seu personagem Minecraft.",
    "keywords": ["minecraft skin", "custom skin", "character", "bedrock"],
    "tags": ["Skin", "Custom", "Character"],
}

PRICE_SKIN = 2.99   # $2.99 / 490 MC
PRICE_SKIN_MC = 490


def extract_theme_id(dirname: str) -> str:
    """Extract theme id from a directory name like 'mass_clay-bakery_01600'.

    Returns 'clay-bakery' or None if pattern doesn't match.
    """
    m = re.match(r"mass_(.+?)_\d+$", dirname)
    return m.group(1) if m else None


def make_pretty_name(theme_id: str, number: str) -> tuple[str, str]:
    """Generate the display name for a pack from theme id and number."""
    meta = THEME_META.get(theme_id, DEFAULT_META)
    return (f"{meta['theme_en']} #{number}", f"{meta['theme_pt']} #{number}")


def build_description(manifest_name: str, theme_id: str) -> tuple[str, str]:
    """Build full store descriptions in EN and PT."""
    meta = THEME_META.get(theme_id, DEFAULT_META)
    number_match = re.search(r"#(\d+)", manifest_name)
    number_str = f"#{number_match.group(1)}" if number_match else ""

    en = (
        f"{manifest_name}\n\n"
        f"{meta['desc_en']}\n\n"
        "Includes 8 unique skin designs! Each skin is carefully crafted to give "
        "your character a fresh new look in Minecraft Bedrock Edition.\n\n"
        "Features:\n"
        "✦ 8 high-quality custom skins\n"
        "✦ HD 64x64 resolution\n"
        "✦ Compatible with Minecraft Bedrock Edition\n"
        "✦ Easy one-click installation\n"
        "✦ Works on all platforms (Windows, Xbox, Mobile, Nintendo Switch)"
    )
    pt = (
        f"{manifest_name}\n\n"
        f"{meta['desc_pt']}\n\n"
        "Inclui 8 designs de skin exclusivos! Cada skin é cuidadosamente criada "
        "para dar ao seu personagem uma aparência nova no Minecraft Bedrock Edition.\n\n"
        "Recursos:\n"
        "✦ 8 skins personalizadas de alta qualidade\n"
        "✦ Resolução HD 64x64\n"
        "✦ Compatível com Minecraft Bedrock Edition\n"
        "✦ Instalação fácil com um clique\n"
        "✦ Funciona em todas as plataformas (Windows, Xbox, Mobile, Nintendo Switch)"
    )
    return en, pt


def generate_tags_and_keywords(theme_id: str) -> tuple[list[str], list[str]]:
    """Return (keywords, tags) for the given theme."""
    meta = THEME_META.get(theme_id, DEFAULT_META)
    base = ["minecraft", "skin pack", "bedrock", "marketplace", "character", "customization"]
    keywords = list(dict.fromkeys(base + meta["keywords"]))  # dedup, preserve order
    tags = list(dict.fromkeys(meta["tags"]))
    return keywords, tags


def main() -> None:
    if not MASS_SKINS_DIR.is_dir():
        print(f"ERROR: mass-skins dir not found at {MASS_SKINS_DIR}", file=sys.stderr)
        sys.exit(1)

    # Collect all pack directories
    pack_dirs = sorted(
        d for d in MASS_SKINS_DIR.iterdir()
        if d.is_dir() and d.name.startswith("mass_")
    )
    print(f"Found {len(pack_dirs)} pack directories.")

    packs = []
    errors = []

    for pack_dir in pack_dirs:
        manifest_path = pack_dir / "manifest.json"
        if not manifest_path.is_file():
            errors.append(f"{pack_dir.name}: missing manifest.json")
            continue

        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            errors.append(f"{pack_dir.name}: failed to read manifest: {e}")
            continue

        manifest_name = manifest.get("header", {}).get("name", pack_dir.name)
        module_type = "skin_pack"
        modules = manifest.get("modules", [])
        if modules:
            module_type = modules[0].get("type", "skin_pack")

        # Extract theme id from directory name
        theme_id = extract_theme_id(pack_dir.name)
        if not theme_id:
            # Fallback: try to parse from manifest name
            theme_id = "custom"

        # Extract number from dir name
        num_match = re.search(r"_(\d+)$", pack_dir.name)
        number = num_match.group(1) if num_match else "0000"

        # Build metadata
        desc_en, desc_pt = build_description(manifest_name, theme_id)
        keywords, tags = generate_tags_and_keywords(theme_id)

        suggested_price = PRICE_SKIN

        pack_entry = {
            "dir": pack_dir.name,
            "name": manifest_name,
            "description_en": desc_en,
            "description_pt": desc_pt,
            "keywords": keywords,
            "tags": tags,
            "suggested_price": suggested_price,
            "suggested_minecoins": PRICE_SKIN_MC,
        }
        packs.append(pack_entry)

    # Sort packs by directory name for consistent output
    packs.sort(key=lambda p: p["dir"])

    output = {"packs": packs, "total_packs": len(packs)}
    CATALOG_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(
        json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print(f"\n✓ Generated metadata for {len(packs)} packs.")
    print(f"  Output: {OUTPUT_FILE}")
    if errors:
        print(f"  Warnings/errors: {len(errors)}")
        for err in errors[:5]:
            print(f"    ⚠ {err}")
        if len(errors) > 5:
            print(f"    ... and {len(errors) - 5} more")
    print(f"\nSample pack: {packs[0]['dir']}")
    print(f"  Name: {packs[0]['name']}")
    print(f"  Theme: {extract_theme_id(packs[0]['dir'])}")
    print(f"  Price: ${packs[0]['suggested_price']:.2f} / {packs[0]['suggested_minecoins']} MC")


if __name__ == "__main__":
    main()
