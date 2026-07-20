import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "IconMineMods — Minecraft Bedrock Skins, Textures & Worlds",
  description:
    "14,600+ Bedrock skin packs, texture packs and worlds. Buy once, own forever. All-Access membership and B2B licensing available.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-bg text-[#e7e9ee]">
        <header className="border-b border-white/10">
          <nav className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
            <Link href="/" className="text-lg font-bold tracking-tight">
              Icon<span className="text-accent">Mine</span>Mods
            </Link>
            <div className="flex gap-5 text-sm text-white/70">
              <Link href="/catalog" className="hover:text-white">Catalog</Link>
              <Link href="/membership" className="hover:text-white">All-Access</Link>
              <Link href="/b2b" className="hover:text-white">B2B</Link>
              <Link href="/cart" className="hover:text-white">Cart</Link>
            </div>
          </nav>
        </header>
        <main className="mx-auto max-w-6xl px-4 py-8">{children}</main>
        <footer className="border-t border-white/10 py-6 text-center text-xs text-white/40">
          IconMineMods · Bedrock content for Minecraft. Not affiliated with Mojang or Microsoft.
        </footer>
      </body>
    </html>
  );
}
