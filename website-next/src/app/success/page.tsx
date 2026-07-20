import Link from "next/link";

export default function SuccessPage({
  searchParams,
}: {
  searchParams: { demo?: string; mode?: string; item?: string; session_id?: string; pack?: string };
}) {
  return (
    <div className="mx-auto max-w-lg space-y-6 rounded-2xl border border-white/10 bg-surface p-10 text-center">
      <div className="text-5xl">✅</div>
      <h1 className="text-2xl font-bold">Order confirmed</h1>
      {searchParams.demo ? (
        <p className="text-white/60">
          Demo mode — no real payment was processed. Configure <code className="text-accent">STRIPE_SECRET_KEY</code> in
          <code className="text-accent"> .env.local</code> to enable live checkout.
        </p>
      ) : (
        <p className="text-white/60">Your Stripe session was successful.</p>
      )}

      {searchParams.pack && (
        <a
          href={`/api/deliver/${searchParams.pack}`}
          className="inline-block rounded-lg bg-accent px-5 py-2.5 font-medium hover:opacity-90"
        >
          Download .mcpack
        </a>
      )}
      {searchParams.mode === "subscription" && (
        <p className="text-white/60">Your All-Access membership is active. Browse and download any pack.</p>
      )}

      <div>
        <Link href="/catalog" className="text-accent hover:underline">Continue to catalog</Link>
      </div>
    </div>
  );
}
