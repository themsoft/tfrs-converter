import { useState, useMemo } from 'react';
import { Search, ArrowUpDown, ArrowUp, ArrowDown } from 'lucide-react';
import { formatTurkishCurrency } from '../../utils/format';
import type { MappedAccount } from '../../types';

interface MizanTableProps {
  data: MappedAccount[];
}

type SortField = 'account_code' | 'account_name' | 'debit_balance' | 'credit_balance' | 'net_balance';
type SortDir = 'asc' | 'desc';

export function MizanTable({ data }: MizanTableProps) {
  const [search, setSearch] = useState('');
  const [sortField, setSortField] = useState<SortField>('account_code');
  const [sortDir, setSortDir] = useState<SortDir>('asc');

  const filtered = useMemo(() => {
    const q = search.toLowerCase();
    return data.filter(r =>
      r.account_code.toLowerCase().includes(q) ||
      r.account_name.toLowerCase().includes(q)
    );
  }, [data, search]);

  const sorted = useMemo(() => {
    return [...filtered].sort((a, b) => {
      const aVal = a[sortField];
      const bVal = b[sortField];
      const cmp = typeof aVal === 'string'
        ? aVal.localeCompare(bVal as string, 'tr')
        : (aVal as number) - (bVal as number);
      return sortDir === 'asc' ? cmp : -cmp;
    });
  }, [filtered, sortField, sortDir]);

  const totals = useMemo(() => {
    return sorted.reduce(
      (acc, r) => ({
        debit_balance: acc.debit_balance + r.debit_balance,
        credit_balance: acc.credit_balance + r.credit_balance,
        net_balance: acc.net_balance + r.net_balance,
      }),
      { debit_balance: 0, credit_balance: 0, net_balance: 0 }
    );
  }, [sorted]);

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDir(d => (d === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortField(field);
      setSortDir('asc');
    }
  };

  const SortIcon = ({ field }: { field: SortField }) => {
    if (sortField !== field) return <ArrowUpDown className="w-3.5 h-3.5 opacity-40" />;
    return sortDir === 'asc'
      ? <ArrowUp className="w-3.5 h-3.5 text-[var(--accent)]" />
      : <ArrowDown className="w-3.5 h-3.5 text-[var(--accent)]" />;
  };

  return (
    <div className="rounded-xl border border-[var(--border-color)] bg-[var(--bg-card)] overflow-hidden animate-fade-in">
      {/* Search Bar */}
      <div className="px-5 py-3 border-b border-[var(--border-color)] flex items-center gap-3">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--text-muted)]" />
          <input
            type="text"
            placeholder="Hesap kodu veya adı ile ara..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2 rounded-lg border border-[var(--border-color)] bg-[var(--bg-primary)] text-sm text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:outline-none focus:border-[var(--accent)] transition-colors"
          />
        </div>
        <span className="text-xs text-[var(--text-muted)]">
          {sorted.length} / {data.length} hesap
        </span>
      </div>

      {/* Table */}
      <div className="overflow-x-auto max-h-[600px] overflow-y-auto">
        <table className="fin-table">
          <thead>
            <tr>
              <SortableHeader field="account_code" label="Hesap Kodu" onClick={handleSort} icon={<SortIcon field="account_code" />} />
              <SortableHeader field="account_name" label="Hesap Adı" onClick={handleSort} icon={<SortIcon field="account_name" />} />
              <SortableHeader field="debit_balance" label="Borç Bakiye" onClick={handleSort} icon={<SortIcon field="debit_balance" />} right />
              <SortableHeader field="credit_balance" label="Alacak Bakiye" onClick={handleSort} icon={<SortIcon field="credit_balance" />} right />
              <SortableHeader field="net_balance" label="Net Bakiye" onClick={handleSort} icon={<SortIcon field="net_balance" />} right />
            </tr>
          </thead>
          <tbody>
            {sorted.map((row, i) => (
              <tr key={row.account_code} className="animate-fade-in" style={{ animationDelay: `${Math.min(i * 0.02, 0.5)}s` }}>
                <td>
                  <span className="font-mono text-xs font-medium bg-[var(--bg-tertiary)] px-2 py-0.5 rounded">
                    {row.account_code}
                  </span>
                </td>
                <td className="text-sm">{row.account_name}</td>
                <td className="amount">{fmtAmount(row.debit_balance)}</td>
                <td className="amount">{fmtAmount(row.credit_balance)}</td>
                <td className={`amount ${row.net_balance < 0 ? 'text-[var(--error)]' : ''}`}>{fmtAmount(row.net_balance)}</td>
              </tr>
            ))}
            {/* Totals Row */}
            <tr className="total-row">
              <td colSpan={2} className="font-bold text-sm">TOPLAM</td>
              <td className="amount font-bold">{formatTurkishCurrency(totals.debit_balance, false)}</td>
              <td className="amount font-bold">{formatTurkishCurrency(totals.credit_balance, false)}</td>
              <td className="amount font-bold">{formatTurkishCurrency(totals.net_balance, false)}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}

function SortableHeader({ field, label, onClick, icon, right }: {
  field: SortField; label: string; onClick: (f: SortField) => void; icon: React.ReactNode; right?: boolean;
}) {
  return (
    <th
      className={`cursor-pointer select-none hover:text-[var(--accent)] ${right ? 'text-right' : ''}`}
      onClick={() => onClick(field)}
    >
      <div className={`flex items-center gap-1 ${right ? 'justify-end' : ''}`}>
        {label}
        {icon}
      </div>
    </th>
  );
}

function fmtAmount(val: number): string {
  if (val === 0) return '-';
  return new Intl.NumberFormat('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(val);
}
