import Link from "next/link";

export const dynamic = "force-dynamic";

export default function MembershipPage() {
  const tiers = [
    { name: "Monthly", price: "$9.99", period: "/mo", note: "Cancel anytime" },
    { name: "Yearly", price: "$99", period: "/yr", note: "2 months free", best: true },
  ];
  return (
    <div className="space-y-8">
      <div className="text-center">
        <h1 className="text-3xl font-bold">All-Access Membership</h1>
        <p className="mt-2 text-white/60">Unlimited downloads of all {14600} packs.</p>
      </div>
      <div className="mx-auto grid max-w-3xl gap-4 md:grid-cols-2">
        {tiers.map((t) => (
          <div key={t.name} className={`rounded-2xl border p-6 ${t.best ? "border-accent bg-accent/10" : "border-white/10 bg-surface"}`}>
            <div className="text-sm text-white/50">{t.name}</div>
            <div className="my-2 text-4xl font-bold">{t.price}<span className="text-lg text-white/50">{t.period}</span></div>
            <p className="mb-4 text-sm text-white/60">{t.note}</p>
            <form action="/api/checkout" method="post">
              <input type="hidden" name="mode" value="subscription" />
              <input type="hidden" name="plan" value={t.name.toLowerCase()} />
              <button className="w-full rounded-lg bg-accent px-4 py-2.5 font-medium hover:opacity-90">Subscribe</button>
            </form>
          </div>
        ))}
      </div>
      <p className="text-center text-xs text-white/40">
        Powered by Stripe. Works without keys in demo mode (no real charge).
      </p>
    </div>
  );
}
