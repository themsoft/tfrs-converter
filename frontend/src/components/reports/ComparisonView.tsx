import { useState } from 'react';
import { ArrowLeftRight, TrendingDown, TrendingUp, Minus } from 'lucide-react';
import { formatTurkishCurrency } from '../../utils/format';
import type { ComparisonResponse, BalanceSheetResponse, IncomeStatementResponse } from '../../types';

interface ComparisonViewProps {
  data: ComparisonResponse;
}

export function ComparisonView({ data }: ComparisonViewProps) {
  const [tab, setTab] = useState<'bilanco' | 'gelir'>('bilanco');

  return (
    <div className="space-y-4 animate-fade-in">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <ArrowLeftRight className="w-5 h-5 text-[var(--accent)]" />
          <h3 className="text-base font-semibold text-[var(--text-primary)]">
            {data.title_tr}
          </h3>
        </div>

        <div className="flex gap-1 bg-[var(--bg-tertiary)] p-1 rounded-lg">
          <button
            onClick={() => setTab('bilanco')}
            className={`px-3 py-1.5 text-xs rounded-md font-medium transition-colors cursor-pointer border-none ${
              tab === 'bilanco'
                ? 'bg-[var(--bg-card)] text-[var(--text-primary)]'
                : 'text-[var(--text-muted)] bg-transparent'
            }`}
            style={tab === 'bilanco' ? { boxShadow: 'var(--shadow-sm)' } : {}}
          >
            Bilanço
          </button>
          <button
            onClick={() => setTab('gelir')}
            className={`px-3 py-1.5 text-xs rounded-md font-medium transition-colors cursor-pointer border-none ${
              tab === 'gelir'
                ? 'bg-[var(--bg-card)] text-[var(--text-primary)]'
                : 'text-[var(--text-muted)] bg-transparent'
            }`}
            style={tab === 'gelir' ? { boxShadow: 'var(--shadow-sm)' } : {}}
          >
            Gelir Tablosu
          </button>
        </div>
      </div>

      {/* Adjustments Summary Cards */}
      {data.adjustments_summary && data.adjustments_summary.length > 0 && (
        <div className="flex flex-wrap gap-2 animate-fade-in-up stagger-1">
          {data.adjustments_summary.filter(a => a.applied).map(adj => (
            <div key={adj.adjustment_type} className="inline-flex items-center gap-2 text-xs bg-[var(--bg-tertiary)] px-3 py-2 rounded-lg">
              <span className="text-[var(--text-secondary)]">{adj.label_tr}</span>
              <span className={`font-mono font-medium ${adj.total_impact >= 0 ? 'text-[var(--success)]' : 'text-[var(--error)]'}`}>
                {formatTurkishCurrency(adj.total_impact)}
              </span>
            </div>
          ))}
        </div>
      )}

      <div className="animate-fade-in" key={tab}>
        {tab === 'bilanco' ? (
          <BalanceSheetComparison before={data.balance_sheet.before} after={data.balance_sheet.after} />
        ) : (
          <IncomeStatementComparison before={data.income_statement.before} after={data.income_statement.after} />
        )}
      </div>
    </div>
  );
}

function BalanceSheetComparison({ before, after }: { before: BalanceSheetResponse; after: BalanceSheetResponse }) {
  // Flatten both into comparable rows
  const rows: { label: string; beforeVal: number; afterVal: number; isHeader: boolean; isTotal: boolean }[] = [];

  // Assets
  for (const sectionKey of ['assets', 'liabilities_and_equity'] as const) {
    const beforeSection = before.sections[sectionKey];
    const afterSection = after.sections[sectionKey];
    rows.push({ label: afterSection.label_tr, beforeVal: beforeSection.total, afterVal: afterSection.total, isHeader: true, isTotal: false });

    const allSubKeys = new Set([
      ...Object.keys(beforeSection.sub_sections),
      ...Object.keys(afterSection.sub_sections),
    ]);

    for (const subKey of allSubKeys) {
      const beforeSub = beforeSection.sub_sections[subKey];
      const afterSub = afterSection.sub_sections[subKey];
      const label = afterSub?.label_tr || beforeSub?.label_tr || subKey;
      rows.push({ label: `  ${label}`, beforeVal: beforeSub?.total ?? 0, afterVal: afterSub?.total ?? 0, isHeader: false, isTotal: false });

      // Individual lines
      const allLineNames = new Set([
        ...(beforeSub?.lines.map(l => l.name) ?? []),
        ...(afterSub?.lines.map(l => l.name) ?? []),
      ]);
      for (const lineName of allLineNames) {
        const bLine = beforeSub?.lines.find(l => l.name === lineName);
        const aLine = afterSub?.lines.find(l => l.name === lineName);
        rows.push({ label: `    ${lineName}`, beforeVal: bLine?.amount ?? 0, afterVal: aLine?.amount ?? 0, isHeader: false, isTotal: false });
      }
    }

    // Section total
    const totalLabel = sectionKey === 'assets' ? 'TOPLAM VARLIKLAR' : 'TOPLAM KAYNAKLAR';
    rows.push({ label: totalLabel, beforeVal: beforeSection.total, afterVal: afterSection.total, isHeader: false, isTotal: true });
  }

  return <ComparisonTable title="Bilanço Karşılaştırması" rows={rows} />;
}

function IncomeStatementComparison({ before, after }: { before: IncomeStatementResponse; after: IncomeStatementResponse }) {
  const allKeys = new Set([
    ...before.lines.map(l => l.key),
    ...after.lines.map(l => l.key),
  ]);

  const rows: { label: string; beforeVal: number; afterVal: number; isHeader: boolean; isTotal: boolean }[] = [];

  for (const key of allKeys) {
    const bLine = before.lines.find(l => l.key === key);
    const aLine = after.lines.find(l => l.key === key);
    const line = aLine || bLine;
    if (!line) continue;

    rows.push({
      label: line.label_tr,
      beforeVal: bLine?.amount ?? 0,
      afterVal: aLine?.amount ?? 0,
      isHeader: false,
      isTotal: line.is_subtotal,
    });
  }

  return <ComparisonTable title="Gelir Tablosu Karşılaştırması" rows={rows} />;
}

function ComparisonTable({ title, rows }: {
  title: string;
  rows: { label: string; beforeVal: number; afterVal: number; isHeader: boolean; isTotal: boolean }[];
}) {
  return (
    <div className="rounded-xl border border-[var(--border-color)] bg-[var(--bg-card)] overflow-hidden">
      <div className="px-5 py-3 border-b border-[var(--border-color)] bg-[var(--bg-tertiary)]">
        <h4 className="text-sm font-semibold text-[var(--text-primary)]">{title}</h4>
      </div>
      <div className="overflow-x-auto">
        <table className="fin-table">
          <thead>
            <tr>
              <th>Kalem</th>
              <th className="text-right">TDHP (Öncesi)</th>
              <th className="text-right">UFRS (Sonrası)</th>
              <th className="text-right">Fark</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row, i) => {
              const diff = row.afterVal - row.beforeVal;
              const isBold = row.isHeader || row.isTotal;

              return (
                <tr key={i} className={row.isTotal ? 'total-row' : ''}>
                  <td
                    className={`text-sm ${isBold ? 'font-bold text-[var(--text-primary)]' : 'text-[var(--text-secondary)]'}`}
                    style={{ whiteSpace: 'pre' }}
                  >
                    {row.label}
                  </td>
                  <td className={`amount ${isBold ? 'font-bold' : ''}`}>
                    {formatTurkishCurrency(row.beforeVal, false)}
                  </td>
                  <td className={`amount ${isBold ? 'font-bold' : ''}`}>
                    {formatTurkishCurrency(row.afterVal, false)}
                  </td>
                  <td className="amount">
                    {Math.abs(diff) > 0.01 ? (
                      <span className={`inline-flex items-center gap-1 ${diff > 0 ? 'text-[var(--success)]' : 'text-[var(--error)]'}`}>
                        {diff > 0 ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                        {formatTurkishCurrency(diff, false)}
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 text-[var(--text-muted)]">
                        <Minus className="w-3 h-3" /> -
                      </span>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
