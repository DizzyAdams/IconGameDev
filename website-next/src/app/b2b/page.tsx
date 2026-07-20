export const dynamic = "force-static";

const B2B = [
  {
    title: "Bulk license",
    price: "from $499",
    desc: "License the full 14,600-pack catalog for your server, classroom or studio. Single invoice, royalty-free use in your community.",
  },
  {
    title: "White-label",
    price: "from $2,500",
    desc: "Rebrand the storefront as your own. We provide the catalog, generation engine and delivery API under your domain.",
  },
  {
    title: "Creator pack",
    price: "from $99",
    desc: "YouTube / Twitch creators: bundle packs into giveaways and sponsor codes for your audience.",
  },
];

export default function B2BPage() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold">B2B & Licensing</h1>
        <p className="mt-2 text-white/60">
          Scale Bedrock content across your organization. Flat licenses, no per-download fees.
        </p>
      </div>
      <div className="grid gap-4 md:grid-cols-3">
        {B2B.map((b) => (
          <div key={b.title} className="rounded-2xl border border-white/10 bg-surface p-6">
            <div className="text-sm text-white/50">{b.title}</div>
            <div className="my-2 text-2xl font-bold">{b.price}</div>
            <p className="text-sm text-white/60">{b.desc}</p>
            <a
              href="mailto:bussins@iconmine.tech?subject=B2B%20license"
              className="mt-4 inline-block rounded-lg border border-accent px-4 py-2 text-sm text-accent hover:bg-accent/10"
            >
              Request quote
            </a>
          </div>
        ))}
      </div>
      <div className="rounded-2xl border border-white/10 bg-surface p-6 text-sm text-white/60">
        <p className="font-medium text-white">Revenue math (why B2B scales to $1M/mo)</p>
        <ul className="mt-2 list-disc space-y-1 pl-5">
          <li>100k All-Access subscribers × $9.99 = $999,000/mo</li>
          <li>or 1,000 bulk licenses × $999 = $999,000/mo</li>
          <li>or 14,600 packs × 70 sales/mo × $1.99 = $2.0M/mo at full velocity</li>
        </ul>
      </div>
    </div>
  );
}
