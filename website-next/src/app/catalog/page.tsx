import Link from "next/link";
import { loadCatalog, TIER_LABEL, TYPE_LABEL } from "@/lib/catalog";

export const dynamic = "force-static";

export default function CatalogPage() {
  const packs = loadCatalog().slice(0, 600); // first page; full index via API
  return (
    <div className="space-y-6">
      <div className="flex items-end justify-between">
        <div>
          <h1 className="text-3xl font-bold">Catalog</h1>
          <p className="text-white/50">{loadCatalog().length.toLocaleString()} packs available</p>
        </div>
        <Link href="/membership" className="rounded-lg border border-accent px-4 py-2 text-sm text-accent hover:bg-accent/10">
          Get All-Access
        </Link>
      </div>
      <div className="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-4">
        {packs.map((p) => (
          <Link key={p.dir} href={`/pack/${p.dir}`} className="group rounded-xl border border-white/10 bg-surface p-4 transition hover:border-accent/60">
            <div className="mb-3 aspect-square w-full rounded-lg bg-gradient-to-br from-accent/30 to-yes/20" />
            <div className="truncate font-medium group-hover:text-accent">{p.name}</div>
            <div className="mt-1 flex items-center justify-between text-xs text-white/50">
              <span>{TYPE_LABEL[p.type] || p.type}</span>
              <span className="font-semibold text-white">${p.price_usd.toFixed(2)}</span>
            </div>
          </Link>
        ))}
      </div>
      <p className="text-center text-sm text-white/40">
        Showing 600 of {loadCatalog().length.toLocaleString()} — full catalog browse & search available via API.
      </p>
    </div>
  );
}
