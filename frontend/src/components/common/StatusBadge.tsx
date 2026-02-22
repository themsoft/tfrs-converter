interface StatusBadgeProps {
  variant: 'success' | 'error' | 'warning' | 'info';
  children: React.ReactNode;
}

const variants = {
  success: 'bg-[var(--success-light)] text-[var(--success)] border-[var(--success)]',
  error: 'bg-[var(--error-light)] text-[var(--error)] border-[var(--error)]',
  warning: 'bg-[var(--warning-light)] text-[var(--warning)] border-[var(--warning)]',
  info: 'bg-[var(--info-light)] text-[var(--info)] border-[var(--info)]',
};

export function StatusBadge({ variant, children }: StatusBadgeProps) {
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${variants[variant]}`}>
      {children}
    </span>
  );
}
