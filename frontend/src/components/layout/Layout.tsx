import type { ReactNode } from 'react';
import { Header } from './Header';

export function Layout({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen bg-[var(--bg-primary)]">
      <Header />
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="page-enter">
          {children}
        </div>
      </main>
      <footer className="border-t border-[var(--border-color)] py-4 mt-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-xs text-[var(--text-muted)]">
          TFRS Dönüştürücü &mdash; Türkiye Muhasebe Standartları'ndan UFRS'ye dönüşüm aracı
        </div>
      </footer>
    </div>
  );
}
