import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { BalanceSheet } from '../components/reports/BalanceSheet';
import { IncomeStatement } from '../components/reports/IncomeStatement';
import { ComparisonView } from '../components/reports/ComparisonView';
import { AdjustmentList } from '../components/adjustments/AdjustmentList';
import { DashboardCharts } from '../components/reports/DashboardCharts';
import { useSession } from '../context/SessionContext';
import { api } from '../utils/api';
import { Scale, TrendingUp, ArrowLeftRight, Settings, PieChart, ArrowLeft, AlertCircle, RefreshCw } from 'lucide-react';
import { CardSkeleton } from '../components/common/Skeleton';
import type {
  BalanceSheetResponse,
  IncomeStatementResponse,
  AdjustmentsResponse,
  ComparisonResponse,
} from '../types';

type Tab = 'dashboard' | 'bilanco' | 'gelir' | 'duzeltme' | 'karsilastirma';

export function ReportsPage() {
  const { sessionId } = useSession();
  const navigate = useNavigate();
  const [tab, setTab] = useState<Tab>('dashboard');

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [balanceSheet, setBalanceSheet] = useState<BalanceSheetResponse | null>(null);
  const [incomeStatement, setIncomeStatement] = useState<IncomeStatementResponse | null>(null);
  const [adjustments, setAdjustments] = useState<AdjustmentsResponse | null>(null);
  const [comparison, setComparison] = useState<ComparisonResponse | null>(null);

  const loadData = useCallback(async () => {
    if (!sessionId) return;
    setLoading(true);
    setError(null);

    try {
      // Step 1: Apply adjustments first
      await api.applyAdjustments(sessionId);

      // Step 2: Fetch all reports in parallel
      const [bs, is, adj, cmp] = await Promise.all([
        api.getBalanceSheet(sessionId),
        api.getIncomeStatement(sessionId),
        api.getAdjustments(sessionId),
        api.getComparison(sessionId),
      ]);

      setBalanceSheet(bs);
      setIncomeStatement(is);
      setAdjustments(adj);
      setComparison(cmp);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Raporlar yüklenirken bir hata oluştu.');
    } finally {
      setLoading(false);
    }
  }, [sessionId]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  if (!sessionId) {
    return (
      <div className="text-center py-20 animate-fade-in">
        <p className="text-[var(--text-muted)] mb-4">Henüz bir mizan yüklenmedi.</p>
        <button
          onClick={() => navigate('/')}
          className="px-4 py-2 rounded-lg bg-[var(--accent)] text-white text-sm font-medium hover:bg-[var(--accent-dark)] transition-colors cursor-pointer border-none"
        >
          Mizan Yükle
        </button>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="space-y-6 animate-fade-in">
        <CardSkeleton count={3} />
        <CardSkeleton count={2} />
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-20 animate-fade-in">
        <div className="inline-flex items-center gap-2 text-[var(--error)] mb-4">
          <AlertCircle className="w-5 h-5" />
          <p className="text-sm">{error}</p>
        </div>
        <br />
        <button
          onClick={loadData}
          className="mt-4 inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-[var(--accent)] text-white text-sm font-medium hover:bg-[var(--accent-dark)] transition-colors cursor-pointer border-none"
        >
          <RefreshCw className="w-4 h-4" />
          Tekrar Dene
        </button>
      </div>
    );
  }

  // Derive chart data from API responses
  const chartAssetData = balanceSheet
    ? Object.entries(balanceSheet.sections.assets.sub_sections).flatMap(([, sub]) =>
        sub.lines.map(l => ({ name: l.name, value: l.amount }))
      )
    : [];

  const chartLiabilityData = balanceSheet
    ? Object.entries(balanceSheet.sections.liabilities_and_equity.sub_sections).map(([, sub]) => ({
        name: sub.label_tr,
        value: sub.total,
      }))
    : [];

  const chartIncomeExpense = comparison
    ? [
        {
          name: 'TDHP',
          gelir: comparison.income_statement.before.lines.find(l => l.key === 'revenue')?.amount ?? 0,
          gider: Math.abs(comparison.income_statement.before.lines.find(l => l.key === 'cost_of_sales')?.amount ?? 0) +
                 Math.abs(comparison.income_statement.before.lines.find(l => l.key === 'operating_expenses')?.amount ?? 0),
        },
        {
          name: 'UFRS',
          gelir: comparison.income_statement.after.lines.find(l => l.key === 'revenue')?.amount ?? 0,
          gider: Math.abs(comparison.income_statement.after.lines.find(l => l.key === 'cost_of_sales')?.amount ?? 0) +
                 Math.abs(comparison.income_statement.after.lines.find(l => l.key === 'operating_expenses')?.amount ?? 0),
        },
      ]
    : [];

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Back button + tabs */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3">
        <button
          onClick={() => navigate('/')}
          className="flex items-center gap-1.5 text-sm text-[var(--text-muted)] hover:text-[var(--text-primary)] transition-colors cursor-pointer bg-transparent border-none"
        >
          <ArrowLeft className="w-4 h-4" />
          Mizana Dön
        </button>

        <div className="flex flex-wrap gap-1 sm:ml-auto bg-[var(--bg-tertiary)] p-1 rounded-lg">
          <ReportTab active={tab === 'dashboard'} onClick={() => setTab('dashboard')} icon={<PieChart className="w-3.5 h-3.5" />} label="Genel Bakış" />
          <ReportTab active={tab === 'bilanco'} onClick={() => setTab('bilanco')} icon={<Scale className="w-3.5 h-3.5" />} label="Bilanço" />
          <ReportTab active={tab === 'gelir'} onClick={() => setTab('gelir')} icon={<TrendingUp className="w-3.5 h-3.5" />} label="Gelir Tablosu" />
          <ReportTab active={tab === 'duzeltme'} onClick={() => setTab('duzeltme')} icon={<Settings className="w-3.5 h-3.5" />} label="Düzeltmeler" />
          <ReportTab active={tab === 'karsilastirma'} onClick={() => setTab('karsilastirma')} icon={<ArrowLeftRight className="w-3.5 h-3.5" />} label="Karşılaştırma" />
        </div>
      </div>

      {/* Tab Content */}
      <div className="animate-fade-in" key={tab}>
        {tab === 'dashboard' && (
          <DashboardCharts
            assetData={chartAssetData}
            liabilityData={chartLiabilityData}
            incomeExpenseData={chartIncomeExpense}
          />
        )}
        {tab === 'bilanco' && balanceSheet && <BalanceSheet data={balanceSheet} />}
        {tab === 'gelir' && incomeStatement && <IncomeStatement data={incomeStatement} />}
        {tab === 'duzeltme' && adjustments && <AdjustmentList data={adjustments} />}
        {tab === 'karsilastirma' && comparison && <ComparisonView data={comparison} />}
      </div>
    </div>
  );
}

function ReportTab({ active, onClick, icon, label }: {
  active: boolean; onClick: () => void; icon: React.ReactNode; label: string;
}) {
  return (
    <button
      onClick={onClick}
      className={`flex items-center gap-1.5 px-3 py-1.5 text-xs rounded-md font-medium transition-all duration-200 cursor-pointer border-none ${
        active
          ? 'bg-[var(--bg-card)] text-[var(--text-primary)]'
          : 'text-[var(--text-muted)] hover:text-[var(--text-secondary)] bg-transparent'
      }`}
      style={active ? { boxShadow: 'var(--shadow-sm)' } : {}}
    >
      {icon}
      <span className="hidden sm:inline">{label}</span>
    </button>
  );
}
