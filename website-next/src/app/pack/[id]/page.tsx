import Link from "next/link";
import { getPack } from "@/lib/catalog";

export default async function PackPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const pack = getPack(id);
  if (!pack) {
    return (
      <div className="space-y-4">
        <p className="text-white/60">Pack not found.</p>
        <Link href="/catalog" className="text-accent hover:underline">Back to catalog</Link>
      </div>
    );
  }
  return (
    <div className="grid gap-8 md:grid-cols-2">
      <div className="aspect-square w-full rounded-2xl bg-gradient-to-br from-accent/40 to-yes/20" />
      <div className="space-y-4">
        <div>
          <p className="text-sm uppercase tracking-widest text-accent">{pack.type}</p>
          <h1 className="text-3xl font-bold">{pack.name}</h1>
        </div>
        <p className="text-white/60">
          Ready-to-install Bedrock {pack.type} pack. Includes valid manifest and textures.
          Delivered as a .mcpack file after purchase.
        </p>
        <div className="flex items-center gap-4">
          <span className="text-3xl font-bold">${pack.price_usd.toFixed(2)}</span>
          <span className="rounded-full bg-white/10 px-3 py-1 text-xs">{pack.tier}</span>
        </div>
        <button
          className="w-full rounded-lg bg-accent px-5 py-3 font-medium hover:opacity-90"
          onClick={() => alert("Checkout demo: wire Stripe key in .env.local (see /api/checkout)")}
        >
          Buy now
        </button>
        <Link href="/catalog" className="block text-center text-sm text-white/50 hover:text-white">
          Back to catalog
        </Link>
      </div>
    </div>
  );
}
