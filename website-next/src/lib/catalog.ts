import * as fs from "fs";
import * as path from "path";

export const REPO_ROOT = path.resolve(process.cwd(), "..");
export const CATALOG_JSON = path.join(
  REPO_ROOT,
  "marketplace-content",
  "catalog",
  "PACK_CATALOG.real.json"
);

export type Pack = {
  dir: string;
  folder: string;
  name: string;
  type: string;
  tier: string;
  price_usd: number;
  path: string; // absolute path to manifest.json in sources
};

let _cache: Pack[] | null = null;

export function loadCatalog(): Pack[] {
  if (_cache) return _cache;
  if (!fs.existsSync(CATALOG_JSON)) return [];
  const data = JSON.parse(fs.readFileSync(CATALOG_JSON, "utf8"));
  _cache = (data.packs || []) as Pack[];
  return _cache;
}

export function getPack(id: string): Pack | undefined {
  return loadCatalog().find((p) => p.dir === id);
}

export function packSourceDir(pack: Pack): string {
  return path.dirname(pack.path);
}

export const TIER_LABEL: Record<string, string> = {
  economy: "Economy",
  standard: "Standard",
  premium: "Premium",
  deluxe: "Deluxe",
};

export const TYPE_LABEL: Record<string, string> = {
  skins: "Skin Pack",
  textures: "Texture Pack",
  worlds: "World Template",
  mashup: "Mashup Pack",
};
