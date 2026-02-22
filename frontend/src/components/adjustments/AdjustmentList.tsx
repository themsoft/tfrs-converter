import { useState } from 'react';
import { Settings, ChevronDown, ChevronUp, FileText, CheckCircle } from 'lucide-react';
import { formatTurkishCurrency } from '../../utils/format';
import { StatusBadge } from '../common/StatusBadge';
import type { AdjustmentsResponse, Adjustment } from '../../types';

interface AdjustmentListProps {
  data: AdjustmentsResponse;
}

export function AdjustmentList({ data }: AdjustmentListProps) {
  const [expandedType, setExpandedType] = useState<string | null>(null);

  const { adjustments } = data;
  const appliedCount = adjustments.filter(a => a.applied).length;
  const totalDebit = adjustments
    .filter(a => a.applied)
    .reduce((sum, a) => sum + a.entries.reduce((s, e) => s + e.debit_amount, 0), 0);
  const totalCredit = adjustments
    .filter(a => a.applied)
    .reduce((sum, a) => sum + a.entries.reduce((s, e) => s + e.credit_amount, 0), 0);

  return (
    <div className="space-y-4 animate-fade-in">
      {/* Summary */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="p-4 rounded-xl border border-[var(--border-color)] bg-[var(--bg-card)] animate-fade-in-up stagger-1" style={{ boxShadow: 'var(--shadow-sm)' }}>
          <p className="text-xs text-[var(--text-muted)]">Uygulanan Düzeltme</p>
          <p className="text-2xl font-bold text-[var(--text-primary)]">{appliedCount} / {adjustments.length}</p>
        </div>
        <div className="p-4 rounded-xl border border-[var(--border-color)] bg-[var(--bg-card)] animate-fade-in-up stagger-2" style={{ boxShadow: 'var(--shadow-sm)' }}>
          <p className="text-xs text-[var(--text-muted)]">Toplam Borç</p>
          <p className="text-2xl font-bold text-[var(--text-primary)] font-mono">{formatTurkishCurrency(totalDebit)}</p>
        </div>
        <div className="p-4 rounded-xl border border-[var(--border-color)] bg-[var(--bg-card)] animate-fade-in-up stagger-3" style={{ boxShadow: 'var(--shadow-sm)' }}>
          <p className="text-xs text-[var(--text-muted)]">Toplam Alacak</p>
          <p className="text-2xl font-bold text-[var(--text-primary)] font-mono">{formatTurkishCurrency(totalCredit)}</p>
        </div>
      </div>

      {/* Adjustment Cards */}
      <div className="space-y-3">
        {adjustments.map((adj, idx) => (
          <AdjustmentCard
            key={adj.adjustment_type}
            adjustment={adj}
            expanded={expandedType === adj.adjustment_type}
            onToggle={() => setExpandedType(expandedType === adj.adjustment_type ? null : adj.adjustment_type)}
            index={idx}
          />
        ))}
      </div>
    </div>
  );
}

function AdjustmentCard({ adjustment: adj, expanded, onToggle, index }: {
  adjustment: Adjustment;
  expanded: boolean;
  onToggle: () => void;
  index: number;
}) {
  return (
    <div
      className={`rounded-xl border bg-[var(--bg-card)] overflow-hidden transition-all animate-fade-in-up ${
        adj.applied ? 'border-[var(--border-color)]' : 'border-[var(--border-color)] opacity-60'
      }`}
      style={{ boxShadow: 'var(--shadow-sm)', animationDelay: `${(index + 4) * 0.1}s` }}
    >
      {/* Card Header */}
      <button
        onClick={onToggle}
        className="w-full flex items-center gap-3 px-5 py-4 cursor-pointer bg-transparent border-none text-left hover:bg-[var(--bg-hover)] transition-colors"
      >
        <div className="shrink-0">
          <CheckCircle className={`w-6 h-6 ${adj.applied ? 'text-[var(--success)]' : 'text-[var(--text-muted)]'}`} />
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <h4 className="text-sm font-semibold text-[var(--text-primary)]">{adj.label_tr}</h4>
            <StatusBadge variant={adj.applied ? 'success' : 'warning'}>
              {adj.applied ? 'Uygulandı' : 'Uygulanmadı'}
            </StatusBadge>
          </div>
          <p className="text-xs text-[var(--text-muted)] mt-0.5">{adj.label_en}</p>
        </div>

        <div className="hidden sm:flex items-center gap-4">
          <div className="text-right">
            <p className="text-[10px] text-[var(--text-muted)]">ETKİ</p>
            <p className={`text-sm font-mono font-semibold ${adj.total_impact >= 0 ? 'text-[var(--success)]' : 'text-[var(--error)]'}`}>
              {formatTurkishCurrency(adj.total_impact)}
            </p>
          </div>
        </div>

        <div className="shrink-0 text-[var(--text-muted)]">
          {expanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </div>
      </button>

      {/* Expanded Details */}
      {expanded && (
        <div className="px-5 py-4 border-t border-[var(--border-color)] bg-[var(--bg-secondary)] animate-fade-in">
          {/* Entries Table */}
          <div className="mb-4">
            <p className="text-[10px] font-semibold text-[var(--text-muted)] uppercase mb-2 flex items-center gap-1">
              <FileText className="w-3 h-3" /> Düzeltme Fişleri
            </p>
            <div className="overflow-x-auto rounded-lg border border-[var(--border-color)]">
              <table className="fin-table">
                <thead>
                  <tr>
                    <th>Açıklama</th>
                    <th>Borç Hesabı</th>
                    <th className="text-right">Borç Tutarı</th>
                    <th>Alacak Hesabı</th>
                    <th className="text-right">Alacak Tutarı</th>
                  </tr>
                </thead>
                <tbody>
                  {adj.entries.map(entry => (
                    <tr key={entry.entry_id}>
                      <td className="text-xs text-[var(--text-secondary)]">{entry.description_tr}</td>
                      <td className="text-xs">
                        <span className="font-mono bg-[var(--bg-tertiary)] px-1.5 py-0.5 rounded mr-1">{entry.debit_account}</span>
                        {entry.debit_account_name}
                      </td>
                      <td className="amount text-sm">{formatTurkishCurrency(entry.debit_amount, false)}</td>
                      <td className="text-xs">
                        <span className="font-mono bg-[var(--bg-tertiary)] px-1.5 py-0.5 rounded mr-1">{entry.credit_account}</span>
                        {entry.credit_account_name}
                      </td>
                      <td className="amount text-sm">{formatTurkishCurrency(entry.credit_amount, false)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Parameters */}
          {adj.parameters && Object.keys(adj.parameters).length > 0 && (
            <div>
              <p className="text-[10px] font-semibold text-[var(--text-muted)] uppercase mb-2 flex items-center gap-1">
                <Settings className="w-3 h-3" /> Parametreler
              </p>
              <div className="flex flex-wrap gap-2">
                {Object.entries(adj.parameters).map(([key, val]) => (
                  <div key={key} className="inline-flex items-center gap-1.5 text-xs bg-[var(--bg-tertiary)] px-2.5 py-1.5 rounded-lg">
                    <span className="text-[var(--text-muted)]">{key}:</span>
                    <span className="font-medium text-[var(--text-primary)]">{String(val)}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
