import { NextRequest, NextResponse } from "next/server";
import Stripe from "stripe";
import { getPack } from "@/lib/catalog";

export const dynamic = "force-dynamic";

const STRIPE_KEY = process.env.STRIPE_SECRET_KEY;
const DEMO = !STRIPE_KEY;

export async function POST(req: NextRequest) {
  const form = await req.formData().catch(() => null);
  const body = form ? Object.fromEntries(form.entries()) : await req.json().catch(() => ({}));
  const mode = (body.mode as string) || "single";
  const origin = new URL(req.url).origin;

  // DEMO MODE: no Stripe key configured -> return a fake success url
  if (DEMO) {
    const params = new URLSearchParams({
      demo: "1",
      mode,
      item: String(body.pack || body.plan || "all-access"),
    });
    return NextResponse.redirect(`${origin}/success?${params.toString()}`, { status: 303 });
  }

  const stripe = new Stripe(STRIPE_KEY!);
  try {
    if (mode === "subscription") {
      const plan = body.plan === "yearly" ? "price_yearly" : "price_monthly";
      const session = await stripe.checkout.sessions.create({
        mode: "subscription",
        line_items: [{ price: plan, quantity: 1 }],
        success_url: `${origin}/success?session_id={CHECKOUT_SESSION_ID}`,
        cancel_url: `${origin}/membership`,
      });
      return NextResponse.redirect(session.url!, { status: 303 });
    }
    const pack = getPack(String(body.pack));
    if (!pack) return NextResponse.json({ error: "pack not found" }, { status: 404 });
    const session = await stripe.checkout.sessions.create({
      mode: "payment",
      line_items: [
        {
          price_data: {
            currency: "usd",
            product_data: { name: pack.name, description: `Bedrock ${pack.type} pack` },
            unit_amount: Math.round(pack.price_usd * 100),
          },
          quantity: 1,
        },
      ],
      success_url: `${origin}/success?session_id={CHECKOUT_SESSION_ID}&pack=${pack.dir}`,
      cancel_url: `${origin}/pack/${pack.dir}`,
    });
    return NextResponse.redirect(session.url!, { status: 303 });
  } catch (e: any) {
    return NextResponse.json({ error: e.message }, { status: 500 });
  }
}
