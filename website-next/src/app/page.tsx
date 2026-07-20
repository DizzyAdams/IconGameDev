import Link from "next/link";
import { loadCatalog, TIER_LABEL, TYPE_LABEL } from "@/lib/catalog";

export default function Home() {
  const packs = loadCatalog();
  const total = packs.length;
  const byType: Record<string, number> = {};
  for (const p of packs) byType[p.type] = (byType[p.type] || 0) + 1;

  return (
    <div className="space-y-12">
      <section className="rounded-2xl border border-white/10 bg-surface p-10 text-center">
        <p className="mb-2 text-sm uppercase tracking-widest text-accent">Bedrock content store</p>
        <h1 className="text-4xl font-bold md:text-5xl">
          {total.toLocaleString()} Minecraft Bedrock packs.
          <br /> Buy once. Own forever.
        </h1>
        <p className="mx-auto mt-4 max-w-2xl text-white/60">
          Skin packs, texture packs and worlds for Minecraft Bedrock Edition.
          Instant .mcpack download after checkout. No subscriptions required.
        </p>
        <div className="mt-6 flex justify-center gap-3">
          <Link href="/catalog" className="rounded-lg bg-accent px-5 py-2.5 font-medium hover:opacity-90">
            Browse catalog
          </Link>
          <Link href="/membership" className="rounded-lg border border-white/20 px-5 py-2.5 hover:bg-white/5">
            All-Access $9.99/mo
          </Link>
        </div>
      </section>

      <section className="grid grid-cols-2 gap-4 md:grid-cols-4">
        {(Object.entries(byType)).map(([t, n]) => (
          <div key={t} className="rounded-xl border border-white/10 bg-surface p-5">
            <div className="text-3xl font-bold">{n.toLocaleString()}</div>
            <div className="text-sm text-white/50">{TYPE_LABEL[t] || t}</div>
          </div>
        ))}
      </section>

      <section className="rounded-2xl border border-white/10 bg-surface p-8">
        <h2 className="mb-4 text-2xl font-bold">Three ways to buy</h2>
        <div className="grid gap-4 md:grid-cols-3">
          <Plan title="Single pack" price="$1.99+" desc="Buy any pack à la carte. Instant .mcpack download." href="/catalog" cta="Shop" />
          <Plan title="All-Access" price="$9.99/mo" desc="Unlimited downloads of every pack. Cancel anytime." href="/membership" cta="Subscribe" highlight />
          <Plan title="B2B license" price="Custom" desc="Bulk licensing, white-label, YouTube creators." href="/b2b" cta="Contact" />
        </div>
      </section>
    </div>
  );
}

function Plan(p: { title: string; price: string; desc: string; href: string; cta: string; highlight?: boolean }) {
  return (
    <div className={`rounded-xl border p-6 ${p.highlight ? "border-accent bg-accent/10" : "border-white/10 bg-bg"}`}>
      <div className="text-sm text-white/50">{p.title}</div>
      <div className="my-2 text-2xl font-bold">{p.price}</div>
      <p className="mb-4 text-sm text-white/60">{p.desc}</p>
      <Link href={p.href} className="inline-block rounded-lg bg-accent px-4 py-2 text-sm font-medium hover:opacity-90">
        {p.cta}
      </Link>
    </div>
  );
}
