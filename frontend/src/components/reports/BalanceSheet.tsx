import { useState } from 'react';
import { Scale, ChevronDown, ChevronRight, CheckCircle, AlertTriangle } from 'lucide-react';
import { formatTurkishCurrency } from '../../utils/format';
import type { BalanceSheetResponse, BalanceSheetSubSection } from '../../types';

interface BalanceSheetProps {
  data: BalanceSheetResponse;
}

export function BalanceSheet({ data }: BalanceSheetProps) {
  const { sections, totals } = data;

  return (
    <div className="space-y-4 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Scale className="w-5 h-5 text-[var(--accent)]" />
          <h3 className="text-base font-semibold text-[var(--text-primary)]">
            {data.title_tr}
          </h3>
        </div>
      </div>

      {/* Balance Check */}
      <div className={`flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm animate-scale-in ${
        totals.is_balanced ? 'bg-[var(--success-light)] text-[var(--success)]' : 'bg-[var(--error-light)] text-[var(--error)]'
      }`}>
        {totals.is_balanced
          ? <><CheckCircle className="w-4 h-4" /> Bilanço denk</>
          : <><AlertTriangle className="w-4 h-4" /> Bilanço denk değil!</>
        }
        <span className="ml-auto font-mono text-xs">
          Varlıklar: {formatTurkishCurrency(totals.total_assets)} | Kaynaklar: {formatTurkishCurrency(totals.total_liabilities_and_equity)}
        </span>
      </div>

      {/* Assets / Liabilities Two Column */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Assets */}
        <SectionCard
          title={sections.assets.label_tr}
          subSections={sections.assets.sub_sections}
          total={sections.assets.total}
          totalLabel="TOPLAM VARLIKLAR"
        />

        {/* Liabilities & Equity */}
        <SectionCard
          title={sections.liabilities_and_equity.label_tr}
          subSections={sections.liabilities_and_equity.sub_sections}
          total={sections.liabilities_and_equity.total}
          totalLabel="TOPLAM KAYNAKLAR"
        />
      </div>
    </div>
  );
}

function SectionCard({ title, subSections, total, totalLabel }: {
  title: string;
  subSections: Record<string, BalanceSheetSubSection>;
  total: number;
  totalLabel: string;
}) {
  return (
    <div className="rounded-xl border border-[var(--border-color)] bg-[var(--bg-card)] overflow-hidden">
      <div className="px-5 py-3 border-b border-[var(--border-color)] bg-[var(--bg-tertiary)]">
        <h4 className="text-sm font-semibold text-[var(--text-primary)]">{title}</h4>
      </div>
      <div className="divide-y divide-[var(--border-color)]">
        {Object.entries(subSections).map(([key, sub]) => (
          <CollapsibleSubSection key={key} subSection={sub} />
        ))}
      </div>
      {/* Total */}
      <div className="px-5 py-3 border-t-2 border-[var(--accent)] bg-[var(--accent-light)] flex items-center justify-between">
        <span className="text-sm font-bold text-[var(--text-primary)]">{totalLabel}</span>
        <span className="text-sm font-bold font-mono text-[var(--text-primary)]">
          {formatTurkishCurrency(total)}
        </span>
      </div>
    </div>
  );
}

function CollapsibleSubSection({ subSection }: { subSection: BalanceSheetSubSection }) {
  const [open, setOpen] = useState(true);

  return (
    <div>
      {/* Sub-section header */}
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between px-5 py-2.5 hover:bg-[var(--bg-hover)] transition-colors cursor-pointer bg-transparent border-none text-left"
      >
        <div className="flex items-center gap-2">
          {open
            ? <ChevronDown className="w-4 h-4 text-[var(--text-muted)]" />
            : <ChevronRight className="w-4 h-4 text-[var(--text-muted)]" />
          }
          <span className="text-sm font-semibold text-[var(--text-primary)]">{subSection.label_tr}</span>
        </div>
        <span className="text-sm font-semibold font-mono text-[var(--text-primary)]">
          {formatTurkishCurrency(subSection.total)}
        </span>
      </button>

      {/* Lines */}
      {open && (
        <div className="animate-fade-in">
          {subSection.lines.map((line, i) => (
            <div
              key={i}
              className="flex items-center justify-between px-5 py-2 pl-12 text-sm hover:bg-[var(--bg-hover)] transition-colors"
            >
              <span className="text-[var(--text-secondary)]">{line.name}</span>
              <span className={`font-mono ${line.amount < 0 ? 'text-[var(--error)]' : 'text-[var(--text-primary)]'}`}>
                {formatTurkishCurrency(line.amount)}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
