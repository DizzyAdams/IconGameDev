import { NextRequest, NextResponse } from "next/server";
import { loadCatalog } from "@/lib/catalog";

export const dynamic = "force-static";

export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const q = (searchParams.get("q") || "").toLowerCase();
  const type = searchParams.get("type") || "";
  const limit = Math.min(parseInt(searchParams.get("limit") || "100", 10), 1000);

  let packs = loadCatalog();
  if (q) packs = packs.filter((p) => p.name.toLowerCase().includes(q));
  if (type) packs = packs.filter((p) => p.type === type);

  return NextResponse.json({
    total: loadCatalog().length,
    count: packs.slice(0, limit).length,
    packs: packs.slice(0, limit).map((p) => ({
      id: p.dir,
      name: p.name,
      type: p.type,
      tier: p.tier,
      price_usd: p.price_usd,
    })),
  });
}
