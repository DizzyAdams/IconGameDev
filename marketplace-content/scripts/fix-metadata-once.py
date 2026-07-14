# Script simples/corrigido: regenera metadata usando a função boa de improve_store_copy
import json, os, re, sys
from pathlib import Path

mc = Path('/c/Users/forrydev/Desktop/bedrock_minemods/marketplace-content')
sys.path.insert(0, str(mc))
from src.catalog.manifest_upgrader import improve_store_copy  # noqa: E402

def read_description(pack_root: Path, pack_dir: str) -> str:
    for rel in ('description.txt','description_en.txt','description_pt.txt'):
        p = pack_root.parent.parent / 'descriptions' / pack_dir / rel
        if p.exists():
            text = p.read_text(encoding='utf-8', errors='ignore')
            break
    else:
        return ''
    text = re.sub(r'§[0-9a-fk-or]', '', text, flags=re.IGNORECASE)
    text = re.sub(r'©.*$', '', text, flags=re.MULTILINE).strip()
    text = re.sub(r'\r\n?', '\n', text)
    text = re.sub(r'\n{2,}', '\n', text).strip()
    return text

ranges = {
    'skin-packs': (1.99,3.99),
    'texture-packs': (2.99,5.99),
    'world-templates': (3.99,5.99),
    'mashup-packs': (5.99,7.99),
}
count = 0
for sub, (lo, hi) in ranges.items():
    base = mc / sub
    if not base.exists():
        continue
    for d in sorted(base.iterdir()):
        if not d.is_dir() or (d/'manifest.json').exists() is False:
            continue
        mf = d/'manifest.json'
        m = json.loads(mf.read_text(encoding='utf-8'))
        md = m.setdefault('metadata', {})
        md['product_type'] = m.get('metadata', {}).get('product_type', sub.replace('-s','s'))
        # price same
        price = (lo + hi) / 2
        md['price_usd'] = round(price, 2)
        mc_coins = max(1, int(round((price*160)/10.0)*10))
        md['price'] = f'${price:.2f} ({mc_coins} MC)'
        md['price_mc'] = mc_coins
        md['tier'] = 'premium'
        md.setdefault('status','pending_premium_review')
        # description
        desc = read_description(d, d.name)
        improved = improve_store_copy(desc)
        if improved:
            md['store_description'] = improved
            m['header']['description'] = improved
        mf.write_text(json.dumps(m, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
        count += 1
print('UPGRADED', count)
