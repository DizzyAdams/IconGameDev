"""Generate complete Marketplace website — catalog, pack pages, partner hub, admin."""
import os, json, shutil, math
from pathlib import Path

MC = Path(__file__).resolve().parent.parent  # marketplace-content/
ROOT = MC.parent                               # bedrock_minemods/
WEBSITE = ROOT / "website"
DIST = MC / "dist"
SKIN_DIR = MC / "skin-packs"
TEX_DIR = MC / "texture-packs"
WORLD_DIR = MC / "world-templates"
MASHUP_DIR = MC / "mashup-packs"
OUT = WEBSITE / "catalog"
ADMIN = WEBSITE / "admin"
PARTNER = WEBSITE / "partner"

def scan_packs():
    cat_path = MC / "catalog" / "PACK_CATALOG.json"
    data = json.loads(cat_path.read_text(encoding="utf-8"))
    packs = []
    for rec in data.get("packs", []):
        name = Path((rec.get("path") or "")).parent.name
        ptype = (rec.get("product_type") or "skin_pack").lower()
        ptype_map = {
            "skin_pack": "Skin Pack",
            "resources": "Texture Pack",
            "world_template": "World",
            "mashup": "Mashup",
        }
        cat = ptype_map.get(ptype, "Pack")
        icon = None  # Requires asset mapping; extend later when assets/3d-models are populated
        header_name = name.replace("-", " ").replace("_", " ").title()
        packs.append(
            {
                "dir": rec.get("dir", name),
                "name": header_name,
                "desc": rec.get("store_description", ""),
                "category": cat,
                "type": ptype,
                "icon": icon,
                "version": "1.0.0",
                "uuid": "",
            }
        )
    return packs

def cat_color(cat):
    return {"Skin Pack": "#6366f1", "Texture Pack": "#22c55e", "World": "#f59e0b", "Mashup": "#ec4899"}.get(cat, "#888")

def gen_index_html(packs):
    cat_counts = {}
    for p in packs:
        cat_counts[p["category"]] = cat_counts.get(p["category"], 0) + 1
    cats_html = ""
    for c, n in sorted(cat_counts.items()):
        color = cat_color(c)
        cats_html += f'<button class="cat-btn" data-cat="{c}" style="--cat:{color}" onclick="filterBy(\'{c}\')">{c} ({n})</button>'
    cats_html += f'<button class="cat-btn active" data-cat="all" style="--cat:#fff" onclick="filterBy(\'all\')">All ({len(packs)})</button>'
    cards_html = ""
    for p in packs:
        icon = p["icon"] or ""
        color = cat_color(p["category"])
        desc = (p.get("desc") or "").replace('"', '&quot;')
        cards_html += f'''<article class="card" data-cat="{p["category"]}">
    <a href="/catalog/{p["dir"]}/">
      <div class="card-icon" style="background:{color}22">{"<img src='"+icon+"' alt='' loading='lazy'>" if icon else f'<span class="cat-badge">{p["category"][0]}</span>'}</div>
      <div class="card-body">
        <span class="card-cat" style="color:{color}">{p["category"]}</span>
        <h3>{p["name"]}</h3>
        <p>{desc[:100]}{"..." if len(desc)>100 else ""}</p>
        <span class="card-version">v{p["version"]}</span>
      </div>
    </a>
  </article>'''
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Bedrock Minemods</title>
<meta name="description" content="Premium Minecraft Bedrock Marketplace content — {len(packs)} skin packs, texture packs, worlds, and mashups.">
<link rel="stylesheet" href="/style.css">
</head>
<body>
<header>
  <a href="/" class="logo">BM</a>
  <nav><a href="/catalog/">Catalog</a><a href="/partner/">Partner Program</a><a href="/admin/">Admin</a></nav>
</header>
<main>
  <section class="hero">
    <h1>Marketplace <span>Catalog</span></h1>
    <p>{len(packs)} premium packs for Minecraft Bedrock.</p>
    <div class="stats">
      <span><strong>{sum(1 for p in packs if p["type"]=="skin_pack")}</strong> Skin Packs</span>
      <span><strong>{sum(1 for p in packs if p["type"]=="resources")}</strong> Texture Packs</span>
      <span><strong>{sum(1 for p in packs if p["type"]=="world_template")}</strong> Worlds</span>
      <span><strong>{sum(1 for p in packs if p["type"]=="mashup")}</strong> Mashups</span>
    </div>
  </section>
  <section id="catalog">
    <div class="filters">{cats_html}</div>
    <div class="grid" id="pack-grid">{cards_html}</div>
  </section>
</main>
<footer>
  <span>Bedrock Minemods — not affiliated with Mojang or Microsoft.</span>
  <a href="https://github.com/forrydev/bedrock_minemods">GitHub</a>
</footer>
<script>
function filterBy(cat){{
  document.querySelectorAll('.cat-btn').forEach(b=>b.classList.toggle('active',b.dataset.cat===cat));
  document.querySelectorAll('.card').forEach(c=>c.style.display=cat==='all'||c.dataset.cat===cat?'':'none');
}}
</script>
</body>
</html>'''

def gen_pack_page(p):
    color = cat_color(p["category"])
    icon = p["icon"] or ""
    name = p["name"]
    desc = (p.get("desc") or "").replace('"', '&quot;')
    version = p["version"]
    filename = Path((p.get("manifest") or p.get("path") or "")).name or (p.get("dir", "") + ".mcpack")
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{name} — Bedrock Minemods</title>
<meta name="description" content="{desc[:150]}">
<link rel="stylesheet" href="/style.css">
</head>
<body>
<header>
  <a href="/" class="logo">BM</a>
  <nav><a href="/catalog/">Catalog</a><a href="/partner/">Partner Program</a><a href="/admin/">Admin</a></nav>
</header>
<main>
  <a href="/catalog/" class="back">&larr; Back to catalog</a>
  <section class="pack-detail">
    <div class="pack-header">
      <div class="pack-icon-large" style="background:{color}22">{"<img src='"+icon+"' alt=''>" if icon else ""}</div>
      <div>
        <span class="card-cat" style="color:{color}">{p["category"]}</span>
        <h1>{name}</h1>
        <p class="pack-desc">{desc}</p>
        <div class="pack-meta">
          <span>Version: <strong>v{version}</strong></span>
          <span>File: <strong>{filename}</strong></span>
        </div>
      </div>
    </div>
  </section>
</main>
<footer>
  <span>Bedrock Minemods — not affiliated with Mojang or Microsoft.</span>
  <a href="https://github.com/forrydev/bedrock_minemods">GitHub</a>
</footer>
</body>
</html>'''
  
def gen_partner_html():
    return '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Partner Program — Bedrock Minemods</title>
<meta name="description" content="Minecraft Partner Program application guide and checklist.">
<link rel="stylesheet" href="/style.css">
</head>
<body>
<header>
  <a href="/" class="logo">BM</a>
  <nav><a href="/catalog/">Catalog</a><a href="/partner/">Partner Program</a><a href="/admin/">Admin</a></nav>
</header>
<main>
  <section class="hero">
    <h1>Partner <span>Program</span></h1>
    <p>Complete application kit for the Minecraft Marketplace Partner Program.</p>
  </section>
  <section>
    <h2>Submission Checklist</h2>
    <ul class="checklist">
      <li><label><input type="checkbox" checked> 144 polished .mcpacks in dist/</label></li>
      <li><label><input type="checkbox" checked> All packs validated (Bedrock Validator)</label></li>
      <li><label><input type="checkbox"> CNPJ registered (in progress)</label></li>
      <li><label><input type="checkbox"> Microsoft Creator account created</label></li>
      <li><label><input type="checkbox"> Tax info submitted</label></li>
      <li><label><input type="checkbox"> Payment method configured</label></li>
      <li><label><input type="checkbox"> Store descriptions written (EN + PT + ES)</label></li>
      <li><label><input type="checkbox"> Screenshots captured (4-6 per pack)</label></li>
      <li><label><input type="checkbox"> Video trailers (30s per featured pack)</label></li>
    </ul>
  </section>
  <section>
    <h2>Revenue Projection</h2>
    <div class="revenue-card">
      <div class="rev-item"><span>80 Skin Packs</span><strong>$7,534/mo</strong></div>
      <div class="rev-item"><span>24 Texture Packs</span><strong>$2,010/mo</strong></div>
      <div class="rev-item"><span>24 World Templates</span><strong>$1,676/mo</strong></div>
      <div class="rev-item"><span>16 Mashup Packs</span><strong>$1,006/mo</strong></div>
      <div class="rev-total"><span>Total</span><strong>$13,153/mo</strong></div>
    </div>
  </section>
</main>
<footer>
  <span>Bedrock Minemods — not affiliated with Mojang or Microsoft.</span>
  <a href="https://github.com/forrydev/bedrock_minemods">GitHub</a>
</footer>
</body>
</html>'''

def gen_admin_html(packs):
    rows = ""
    for p in packs:
        rows += f"<tr><td>{p['name']}</td><td>{p['category']}</td><td>v{p['version']}</td><td><a href='/catalog/{p['dir']}/'>View</a></td></tr>"
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Admin — Bedrock Minemods</title>
<link rel="stylesheet" href="/style.css">
</head>
<body>
<header>
  <a href="/" class="logo">BM</a>
  <nav><a href="/catalog/">Catalog</a><a href="/partner/">Partner Program</a><a href="/admin/">Admin</a></nav>
</header>
<main>
  <section class="hero">
    <h1>Admin <span>Dashboard</span></h1>
    <p>{len(packs)} packs total</p>
  </section>
  <section>
    <table>
      <thead><tr><th>Name</th><th>Category</th><th>Version</th><th>Link</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>
  </section>
</main>
<footer><span>Bedrock Minemods</span></footer>
</body>
</html>'''

def gen_style_css():
    return '''*{box-sizing:border-box;margin:0;padding:0}
:root{--bg:#0a0a0b;--fg:#e4e4e7;--fg-dim:#a1a1aa;--accent:#6366f1;--border:#27272a;--card:#18181b;--font:system-ui,-apple-system,'Segoe UI',Roboto,Helvetica,Arial,sans-serif}
@media(prefers-color-scheme:light){:root{--bg:#fafafa;--fg:#18181b;--fg-dim:#52525b;--border:#e4e4e7;--card:#fff}}
html{scroll-behavior:smooth}
body{font-family:var(--font);background:var(--bg);color:var(--fg);line-height:1.6;padding:2rem;max-width:90rem;margin:0 auto}
a{color:inherit;text-decoration:none}
::selection{background:var(--accent);color:#fff}
header{display:flex;justify-content:space-between;align-items:center;padding-bottom:1.5rem;border-bottom:1px solid var(--border);margin-bottom:3rem}
.logo{font-size:1.5rem;font-weight:800;letter-spacing:-2px;color:var(--accent)}
nav{display:flex;gap:1.5rem}
nav a{color:var(--fg-dim);font-size:.875rem;transition:color .15s}
nav a:hover{color:var(--accent)}
.hero{margin-bottom:3rem;max-width:48rem}
.hero h1{font-size:clamp(2rem,5vw,3.75rem);font-weight:800;letter-spacing:-.03em;line-height:1.05;margin-bottom:.75rem}
.hero h1 span{color:var(--accent)}
.hero p{font-size:clamp(1rem,2vw,1.25rem);color:var(--fg-dim);max-width:40rem;line-height:1.65}
.stats{display:flex;gap:2rem;margin-top:1rem;flex-wrap:wrap}
.stats strong{display:block;font-size:1.5rem;color:var(--accent)}
section{margin-bottom:4rem}
section h2{font-size:1.5rem;font-weight:700;margin-bottom:1.5rem;letter-spacing:-.02em}
.filters{display:flex;gap:.5rem;flex-wrap:wrap;margin-bottom:1.5rem}
.cat-btn{padding:.5rem 1rem;border:1px solid var(--border);border-radius:2rem;background:var(--card);color:var(--fg-dim);cursor:pointer;font-size:.875rem;transition:all .15s}
.cat-btn:hover,.cat-btn.active{border-color:var(--cat,var(--accent));color:var(--cat,var(--fg));background:color-mix(in srgb,var(--cat,var(--accent)) 10%,transparent)}
.grid{display:grid;gap:1rem;grid-template-columns:repeat(auto-fill,minmax(280px,1fr))}
.card{background:var(--card);border:1px solid var(--border);border-radius:.75rem;overflow:hidden;transition:border-color .15s}
.card:hover{border-color:var(--accent)}
.card a{display:block;padding:1.25rem;height:100%}
.card-icon{width:100%;aspect-ratio:16/9;border-radius:.5rem;margin-bottom:.75rem;display:flex;align-items:center;justify-content:center;overflow:hidden}
.card-icon img{width:100%;height:100%;object-fit:cover}
.card-icon .cat-badge{font-size:3rem;font-weight:800;color:var(--accent);opacity:.5}
.card-cat{font-size:.75rem;font-weight:600;text-transform:uppercase;letter-spacing:.05em}
.card-body h3{font-size:1.125rem;font-weight:700;margin:.25rem 0 .5rem}
.card-body p{font-size:.875rem;color:var(--fg-dim);line-height:1.5}
.card-version{font-size:.75rem;color:var(--fg-dim)}
.back{display:inline-block;margin-bottom:2rem;color:var(--accent);font-size:.875rem}
.pack-header{display:flex;gap:2rem;flex-wrap:wrap}
.pack-icon-large{width:200px;height:200px;border-radius:1rem;display:flex;align-items:center;justify-content:center;overflow:hidden}
.pack-icon-large img{width:100%;height:100%;object-fit:cover}
.pack-desc{font-size:1.125rem;color:var(--fg-dim);max-width:40rem;margin:.75rem 0}
.pack-meta{display:flex;gap:1.5rem;flex-wrap:wrap;font-size:.875rem;color:var(--fg-dim)}
.checklist{list-style:none}
.checklist li{margin-bottom:.75rem}
.checklist label{display:flex;align-items:center;gap:.75rem;cursor:pointer;font-size:1rem}
.checklist input[type=checkbox]{width:1.25rem;height:1.25rem;accent-color:var(--accent)}
.revenue-card{background:var(--card);border:1px solid var(--border);border-radius:.75rem;padding:1.5rem;max-width:400px}
.rev-item,.rev-total{display:flex;justify-content:space-between;padding:.5rem 0}
.rev-item{border-bottom:1px solid var(--border)}
.rev-total{font-size:1.25rem;font-weight:700;padding-top:1rem}
table{width:100%;border-collapse:collapse;font-size:.875rem}
th,td{text-align:left;padding:.75rem;border-bottom:1px solid var(--border)}
th{color:var(--fg-dim);font-weight:600;text-transform:uppercase;font-size:.75rem;letter-spacing:.05em}
td a{color:var(--accent)}
footer{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:.5rem;border-top:1px solid var(--border);padding-top:1.5rem;font-size:.875rem;color:var(--fg-dim)}
footer a{color:var(--fg-dim);transition:color .15s}
footer a:hover{color:var(--accent)}'''

def main():
    packs = scan_packs()
    for d in [OUT, ADMIN, PARTNER]:
        d.mkdir(parents=True, exist_ok=True)
    (OUT / "index.html").write_text(gen_index_html(packs))
    for p in packs:
        pdir = OUT / p["dir"]
        pdir.mkdir(exist_ok=True)
        (pdir / "index.html").write_text(gen_pack_page(p))
    (PARTNER / "index.html").write_text(gen_partner_html())
    (ADMIN / "index.html").write_text(gen_admin_html(packs))
    (WEBSITE / "style.css").write_text(gen_style_css())
    total = len(packs)
    (WEBSITE / "index.html").write_text(f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Bedrock Minemods</title>
<meta name="description" content="Premium Minecraft Bedrock Marketplace content — {total} packs. Open source, 70% revenue share.">
<link rel="stylesheet" href="style.css">
</head>
<body>
<header>
  <a href="/" class="logo" aria-label="Bedrock Minemods">BM</a>
  <nav><a href="catalog/">Catalog</a><a href="partner/">Partner Program</a><a href="admin/">Admin</a></nav>
</header>
<main>
  <section class="hero">
    <h1>Bedrock <span>Minemods</span></h1>
    <p><strong>{total} premium packs</strong> for Minecraft Bedrock Marketplace — skins, textures, worlds, and mashups. Open source, 70% revenue share, built for 212M players.</p>
    <div class="stats">
      <span><strong>{sum(1 for p in packs if p["type"]=="skin_pack")}</strong> Skin Packs</span>
      <span><strong>{sum(1 for p in packs if p["type"]=="resources")}</strong> Texture Packs</span>
      <span><strong>{sum(1 for p in packs if p["type"]=="world_template")}</strong> Worlds</span>
      <span><strong>{sum(1 for p in packs if p["type"]=="mashup")}</strong> Mashups</span>
    </div>
  </section>
  <section id="products">
    <h2>Products</h2>
    <div class="grid">
      <article class="card"><div class="card-icon" style="background:#6366f122"><span class="cat-badge" style="color:#6366f1">S</span></div><h3>Skin Packs</h3><p>{sum(1 for p in packs if p["type"]=="skin_pack")} packs — anime, fantasy, PVP, fashion, and more.</p></article>
      <article class="card"><div class="card-icon" style="background:#22c55e22"><span class="cat-badge" style="color:#22c55e">T</span></div><h3>Texture Packs</h3><p>{sum(1 for p in packs if p["type"]=="resources")} packs — 8-bit, realistic, PVP-optimized, anime style.</p></article>
      <article class="card"><div class="card-icon" style="background:#f59e0b22"><span class="cat-badge" style="color:#f59e0b">W</span></div><h3>World Templates</h3><p>{sum(1 for p in packs if p["type"]=="world_template")} worlds — survival, PVP, minigames, roleplay.</p></article>
      <article class="card"><div class="card-icon" style="background:#ec489922"><span class="cat-badge" style="color:#ec4899">M</span></div><h3>Mashup Packs</h3><p>{sum(1 for p in packs if p["type"]=="mashup")} bundles — anime, cyberpunk, fantasy, horror and more.</p></article>
    </div>
  </section>
  <section id="features">
    <h2>Why Bedrock Minemods</h2>
    <div class="features">
      <div class="feature"><span class="num">70%</span><span class="label">revenue share for creators</span></div>
      <div class="feature"><span class="num">212M</span><span class="label">monthly active players</span></div>
      <div class="feature"><span class="num">{total}</span><span class="label">premium packs ready</span></div>
    </div>
  </section>
</main>
<footer>
  <span>Bedrock Minemods &mdash; not affiliated with Mojang or Microsoft.</span>
  <a href="https://github.com/forrydev/bedrock_minemods">GitHub</a>
</footer>
</body>
</html>''')
    print(f"=== Site generated to {WEBSITE} ===")
    print(f"  {total} pack pages + catalog + partner + admin + home")

if __name__ == "__main__":
    main()
