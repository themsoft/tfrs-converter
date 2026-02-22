import { TrendingUp } from 'lucide-react';
import { formatTurkishCurrency } from '../../utils/format';
import type { IncomeStatementResponse } from '../../types';

interface IncomeStatementProps {
  data: IncomeStatementResponse;
}

export function IncomeStatement({ data }: IncomeStatementProps) {
  const netProfit = data.lines.find(l => l.key === 'net_profit');
  const netAmount = netProfit?.amount ?? 0;

  return (
    <div className="space-y-4 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-[var(--accent)]" />
          <h3 className="text-base font-semibold text-[var(--text-primary)]">
            {data.title_tr}
          </h3>
        </div>
      </div>

      {/* Net P/L Banner */}
      <div className={`flex items-center justify-between px-4 py-3 rounded-lg animate-scale-in ${
        netAmount >= 0
          ? 'bg-[var(--success-light)]'
          : 'bg-[var(--error-light)]'
      }`}>
        <span className="text-sm font-medium text-[var(--text-primary)]">
          Dönem Net {netAmount >= 0 ? 'Kârı' : 'Zararı'}
        </span>
        <span className={`text-lg font-bold font-mono ${
          netAmount >= 0 ? 'text-[var(--success)]' : 'text-[var(--error)]'
        }`} style={netAmount >= 0 ? { textShadow: '0 0 8px rgba(16,185,129,0.3)' } : {}}>
          {formatTurkishCurrency(netAmount)}
        </span>
      </div>

      {/* Income Statement Table */}
      <div className="rounded-xl border border-[var(--border-color)] bg-[var(--bg-card)] overflow-hidden">
        <div className="overflow-x-auto">
          <table className="fin-table">
            <thead>
              <tr>
                <th className="w-3/4">Kalem</th>
                <th className="text-right">Tutar</th>
              </tr>
            </thead>
            <tbody>
              {data.lines.map((line, i) => (
                <tr
                  key={line.key}
                  className={`animate-fade-in ${
                    line.is_subtotal ? 'border-t-2 border-t-[var(--accent)]' : ''
                  } ${line.key === 'net_profit' ? 'total-row' : ''}`}
                  style={{ animationDelay: `${i * 0.05}s` }}
                >
                  <td className={`text-sm ${
                    line.is_subtotal
                      ? 'font-bold text-[var(--text-primary)]'
                      : 'text-[var(--text-secondary)] pl-6'
                  }`}>
                    {line.label_tr}
                  </td>
                  <td className={`amount ${
                    line.is_subtotal ? 'font-bold' : ''
                  } ${line.amount < 0 ? 'text-[var(--error)]' : ''} ${
                    line.key === 'net_profit' && line.amount >= 0 ? 'text-[var(--success)]' : ''
                  }`}>
                    {formatTurkishCurrency(line.amount)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
