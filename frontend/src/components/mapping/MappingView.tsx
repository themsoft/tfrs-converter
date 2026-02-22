import { useState, useEffect, useMemo } from 'react';
import { GitBranch, CheckCircle, XCircle, Search, BarChart3 } from 'lucide-react';
import { api } from '../../utils/api';
import { useSession } from '../../context/SessionContext';
import { StatusBadge } from '../common/StatusBadge';
import { TableSkeleton, CardSkeleton } from '../common/Skeleton';
import type { MappingResponse, MappedAccount } from '../../types';

export function MappingView() {
  const { sessionId } = useSession();
  const [data, setData] = useState<MappingResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState<'all' | 'matched' | 'unmatched'>('all');

  useEffect(() => {
    if (!sessionId) return;
    setLoading(true);
    api.getMapping(sessionId).then(setData).finally(() => setLoading(false));
  }, [sessionId]);

  const allAccounts: MappedAccount[] = useMemo(() => {
    if (!data) return [];
    return [...data.mapped, ...data.unmapped];
  }, [data]);

  const filtered = useMemo(() => {
    const q = search.toLowerCase();
    return allAccounts.filter(m => {
      const isMatched = m.ifrs_category !== 'unmapped';
      const matchSearch =
        m.account_code.toLowerCase().includes(q) ||
        m.account_name.toLowerCase().includes(q) ||
        m.ifrs_line.toLowerCase().includes(q) ||
        m.ifrs_line_tr.toLowerCase().includes(q);
      const matchFilter =
        filter === 'all' ||
        (filter === 'matched' && isMatched) ||
        (filter === 'unmatched' && !isMatched);
      return matchSearch && matchFilter;
    });
  }, [allAccounts, search, filter]);

  if (loading) {
    return (
      <div className="space-y-4">
        <CardSkeleton count={3} />
        <TableSkeleton rows={10} cols={5} />
      </div>
    );
  }

  if (!data) return null;

  const { statistics } = data;

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <StatCard
          icon={<BarChart3 className="w-5 h-5 text-[var(--info)]" />}
          label="Toplam Hesap"
          value={statistics.total_accounts}
          color="info"
          className="animate-fade-in-up stagger-1"
        />
        <StatCard
          icon={<CheckCircle className="w-5 h-5 text-[var(--success)]" />}
          label="Eşleşen"
          value={statistics.mapped_count}
          sub={`%${statistics.mapping_rate.toFixed(1)}`}
          color="success"
          className="animate-fade-in-up stagger-2"
        />
        <StatCard
          icon={<XCircle className="w-5 h-5 text-[var(--error)]" />}
          label="Eşleşmeyen"
          value={statistics.unmapped_count}
          color="error"
          className="animate-fade-in-up stagger-3"
        />
      </div>

      {/* Mapping Table */}
      <div className="rounded-xl border border-[var(--border-color)] bg-[var(--bg-card)] overflow-hidden animate-fade-in-up stagger-4">
        <div className="px-5 py-3 border-b border-[var(--border-color)] flex flex-col sm:flex-row items-start sm:items-center gap-3">
          <div className="flex items-center gap-2">
            <GitBranch className="w-4 h-4 text-[var(--accent)]" />
            <h3 className="text-sm font-semibold text-[var(--text-primary)]">TDHP → UFRS Eşleştirme</h3>
          </div>
          <div className="flex-1 flex flex-col sm:flex-row items-start sm:items-center gap-2 sm:ml-auto">
            <div className="relative w-full sm:w-64">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--text-muted)]" />
              <input
                type="text"
                placeholder="Ara..."
                value={search}
                onChange={e => setSearch(e.target.value)}
                className="w-full pl-10 pr-4 py-1.5 rounded-lg border border-[var(--border-color)] bg-[var(--bg-primary)] text-sm text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:outline-none focus:border-[var(--accent)] transition-colors"
              />
            </div>
            <div className="flex gap-1">
              {(['all', 'matched', 'unmatched'] as const).map(f => (
                <button
                  key={f}
                  onClick={() => setFilter(f)}
                  className={`px-3 py-1.5 text-xs rounded-lg font-medium transition-colors cursor-pointer border-none ${
                    filter === f
                      ? 'bg-[var(--accent-light)] text-[var(--accent-dark)]'
                      : 'text-[var(--text-muted)] hover:bg-[var(--bg-hover)] bg-transparent'
                  }`}
                >
                  {f === 'all' ? 'Tümü' : f === 'matched' ? 'Eşleşen' : 'Eşleşmeyen'}
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="overflow-x-auto max-h-[500px] overflow-y-auto">
          <table className="fin-table">
            <thead>
              <tr>
                <th>Hesap Kodu</th>
                <th>Hesap Adı</th>
                <th>IFRS Kategorisi</th>
                <th>IFRS Kalemi</th>
                <th className="text-center">Durum</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map(m => {
                const isMatched = m.ifrs_category !== 'unmapped';
                return (
                  <tr key={m.account_code} className={!isMatched ? 'bg-[var(--error-light)]' : ''}>
                    <td>
                      <span className="font-mono text-xs font-medium bg-[var(--bg-tertiary)] px-2 py-0.5 rounded">
                        {m.account_code}
                      </span>
                    </td>
                    <td className="text-sm">{m.account_name}</td>
                    <td className="text-sm text-[var(--text-secondary)]">{isMatched ? m.ifrs_category.replace(/_/g, ' ') : ''}</td>
                    <td className="text-sm">
                      {isMatched ? (
                        <span>{m.ifrs_line_tr}</span>
                      ) : (
                        <span className="text-[var(--error)] italic">Eşleştirilemedi</span>
                      )}
                    </td>
                    <td className="text-center">
                      <StatusBadge variant={isMatched ? 'success' : 'error'}>
                        {isMatched ? 'Eşleşti' : 'Eşleşmedi'}
                      </StatusBadge>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function StatCard({ icon, label, value, sub, color, className = '' }: {
  icon: React.ReactNode; label: string; value: number; sub?: string;
  color: 'info' | 'success' | 'error'; className?: string;
}) {
  const bgMap = { info: 'var(--info-light)', success: 'var(--success-light)', error: 'var(--error-light)' };
  return (
    <div className={`p-4 rounded-xl border border-[var(--border-color)] bg-[var(--bg-card)] ${className}`} style={{ boxShadow: 'var(--shadow-sm)' }}>
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-lg flex items-center justify-center" style={{ background: bgMap[color] }}>
          {icon}
        </div>
        <div>
          <p className="text-xs text-[var(--text-muted)]">{label}</p>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold text-[var(--text-primary)]">{value}</span>
            {sub && <span className="text-sm font-medium text-[var(--text-muted)]">{sub}</span>}
          </div>
        </div>
      </div>
    </div>
  );
}
