interface SkeletonProps {
  className?: string;
  count?: number;
}

export function Skeleton({ className = 'h-4 w-full', count = 1 }: SkeletonProps) {
  return (
    <>
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className={`skeleton ${className}`} />
      ))}
    </>
  );
}

export function TableSkeleton({ rows = 8, cols = 6 }: { rows?: number; cols?: number }) {
  return (
    <div className="overflow-x-auto rounded-lg border border-[var(--border-color)]">
      <table className="fin-table">
        <thead>
          <tr>
            {Array.from({ length: cols }).map((_, i) => (
              <th key={i}><div className="skeleton h-4 w-20" /></th>
            ))}
          </tr>
        </thead>
        <tbody>
          {Array.from({ length: rows }).map((_, r) => (
            <tr key={r}>
              {Array.from({ length: cols }).map((_, c) => (
                <td key={c}><div className="skeleton h-4 w-24" /></td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export function CardSkeleton({ count = 4 }: { count?: number }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="p-5 rounded-xl border border-[var(--border-color)] bg-[var(--bg-card)]">
          <div className="skeleton h-3 w-24 mb-3" />
          <div className="skeleton h-8 w-32 mb-2" />
          <div className="skeleton h-3 w-16" />
        </div>
      ))}
    </div>
  );
}
