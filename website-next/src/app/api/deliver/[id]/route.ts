import { NextRequest, NextResponse } from "next/server";
import { getPack, packSourceDir } from "@/lib/catalog";
import { buildMcpack } from "@/lib/mcpack";
import * as fs from "fs";

export const dynamic = "force-dynamic";

// Delivers a built .mcpack for a purchased pack.
// In production, gate this behind a Stripe session / license check.
export async function GET(req: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const pack = getPack(id);
  if (!pack) return NextResponse.json({ error: "not found" }, { status: 404 });

  // ownership check (demo: allow). Real impl: verify session_id or license cookie.
  const buf = buildMcpack(pack);
  const safeName = pack.dir.replace(/[^a-z0-9_-]/gi, "_");
  return new NextResponse(new Uint8Array(buf), {
    status: 200,
    headers: {
      "Content-Type": "application/octet-stream",
      "Content-Disposition": `attachment; filename="${safeName}.mcpack"`,
      "Content-Length": String(buf.length),
    },
  });
}

// expose a build sanity endpoint (used by tests)
export async function POST() {
  const sample = getPack("african-tribes") || getPack("");
  if (!sample) return NextResponse.json({ ok: false, reason: "no packs" });
  const buf = buildMcpack(sample);
  return NextResponse.json({ ok: true, bytes: buf.length, name: sample.dir });
}
