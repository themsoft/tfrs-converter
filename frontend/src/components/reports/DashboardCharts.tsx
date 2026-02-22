import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { useTheme } from '../../context/ThemeContext';
import { formatTurkishCurrency } from '../../utils/format';

const COLORS = ['#f59e0b', '#3b82f6', '#10b981', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16'];

interface ChartData {
  name: string;
  value: number;
}

interface DashboardChartsProps {
  assetData: ChartData[];
  liabilityData: ChartData[];
  incomeExpenseData: { name: string; gelir: number; gider: number }[];
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const pieLabel = (props: any) => {
  const { name, percent } = props;
  return `${name ?? ''} %${((percent ?? 0) * 100).toFixed(0)}`;
};

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const tooltipFormatter = (value: any) => formatTurkishCurrency(Number(value));

export function DashboardCharts({ assetData, liabilityData, incomeExpenseData }: DashboardChartsProps) {
  const { theme } = useTheme();
  const textColor = theme === 'dark' ? '#94a3b8' : '#475569';
  const gridColor = theme === 'dark' ? '#334155' : '#e2e8f0';

  const tooltipStyle = {
    background: theme === 'dark' ? '#1e293b' : '#ffffff',
    border: `1px solid ${gridColor}`,
    borderRadius: '8px',
    color: theme === 'dark' ? '#f1f5f9' : '#0f172a',
    fontSize: '12px',
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Asset Distribution Donut */}
      <div className="rounded-xl border border-[var(--border-color)] bg-[var(--bg-card)] p-5 animate-fade-in-up stagger-1" style={{ boxShadow: 'var(--shadow-sm)' }}>
        <h4 className="text-sm font-semibold text-[var(--text-primary)] mb-4">Varlık Dağılımı</h4>
        <ResponsiveContainer width="100%" height={280}>
          <PieChart>
            <Pie
              data={assetData}
              cx="50%"
              cy="50%"
              innerRadius={60}
              outerRadius={100}
              dataKey="value"
              paddingAngle={2}
              label={pieLabel}
              labelLine={false}
              isAnimationActive={true}
              animationDuration={800}
            >
              {assetData.map((_, i) => (
                <Cell key={i} fill={COLORS[i % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip formatter={tooltipFormatter} contentStyle={tooltipStyle} />
          </PieChart>
        </ResponsiveContainer>
      </div>

      {/* Liability Distribution Donut */}
      <div className="rounded-xl border border-[var(--border-color)] bg-[var(--bg-card)] p-5 animate-fade-in-up stagger-2" style={{ boxShadow: 'var(--shadow-sm)' }}>
        <h4 className="text-sm font-semibold text-[var(--text-primary)] mb-4">Kaynak Dağılımı</h4>
        <ResponsiveContainer width="100%" height={280}>
          <PieChart>
            <Pie
              data={liabilityData}
              cx="50%"
              cy="50%"
              innerRadius={60}
              outerRadius={100}
              dataKey="value"
              paddingAngle={2}
              label={pieLabel}
              labelLine={false}
              isAnimationActive={true}
              animationDuration={800}
            >
              {liabilityData.map((_, i) => (
                <Cell key={i} fill={COLORS[(i + 3) % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip formatter={tooltipFormatter} contentStyle={tooltipStyle} />
          </PieChart>
        </ResponsiveContainer>
      </div>

      {/* Income vs Expense Bar Chart */}
      <div className="lg:col-span-2 rounded-xl border border-[var(--border-color)] bg-[var(--bg-card)] p-5 animate-fade-in-up stagger-3" style={{ boxShadow: 'var(--shadow-sm)' }}>
        <h4 className="text-sm font-semibold text-[var(--text-primary)] mb-4">Gelir / Gider Karşılaştırması</h4>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={incomeExpenseData} barGap={8}>
            <CartesianGrid strokeDasharray="3 3" stroke={gridColor} />
            <XAxis dataKey="name" tick={{ fill: textColor, fontSize: 12 }} />
            <YAxis
              tick={{ fill: textColor, fontSize: 11 }}
              tickFormatter={(v: number) => {
                if (Math.abs(v) >= 1_000_000) return `${(v / 1_000_000).toFixed(1)}M`;
                if (Math.abs(v) >= 1_000) return `${(v / 1_000).toFixed(0)}K`;
                return String(v);
              }}
            />
            <Tooltip formatter={tooltipFormatter} contentStyle={tooltipStyle} />
            <Legend />
            <Bar dataKey="gelir" name="Gelir" fill="#10b981" radius={[4, 4, 0, 0]} isAnimationActive={true} animationDuration={800} />
            <Bar dataKey="gider" name="Gider" fill="#ef4444" radius={[4, 4, 0, 0]} isAnimationActive={true} animationDuration={800} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
