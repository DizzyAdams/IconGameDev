import './globals.css';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'IconMyBedrockMods',
  description: 'Marketplace de skins, chunks e mods para Minecraft Bedrock.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR">
      <body className="bg-neutral-950 text-white">
        <header className="border-b border-neutral-800">
          <div className="mx-auto max-w-6xl px-4 py-4 flex items-center justify-between">
            <h1 className="text-xl font-bold tracking-tight">IconMyBedrockMods</h1>
            <nav className="space-x-6 text-sm text-neutral-300">
              <a href="/" className="hover:text-white">Início</a>
              <a href="/pack" className="hover:text-white">Catálogo</a>
              <a href="/about" className="hover:text-white">Sobre</a>
            </nav>
          </div>
        </header>
        <main className="mx-auto max-w-6xl px-4 py-8">{children}</main>
        <footer className="border-t border-neutral-800 mt-10">
          <div className="mx-auto max-w-6xl px-4 py-6 text-xs text-neutral-500">
            IconMyBedrockMods — não afiliado à Mojang ou Microsoft.
          </div>
        </footer>
      </body>
    </html>
  );
}
