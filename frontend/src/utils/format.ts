/**
 * Formats a number in Turkish financial format: 1.234.567,89
 */
export function formatTurkishCurrency(value: number, showSymbol = true): string {
  const formatted = new Intl.NumberFormat('tr-TR', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(Math.abs(value));

  const sign = value < 0 ? '-' : '';
  return showSymbol ? `${sign}${formatted} TL` : `${sign}${formatted}`;
}

/**
 * Formats a number as percentage
 */
export function formatPercent(value: number, decimals = 1): string {
  return `%${value.toFixed(decimals)}`;
}

/**
 * Formats a number with thousand separators (no decimals)
 */
export function formatNumber(value: number): string {
  return new Intl.NumberFormat('tr-TR').format(value);
}

/**
 * Shortens large numbers: 1.2M, 3.4B etc.
 */
export function formatCompact(value: number): string {
  const abs = Math.abs(value);
  const sign = value < 0 ? '-' : '';

  if (abs >= 1_000_000_000) {
    return `${sign}${(abs / 1_000_000_000).toFixed(1)} Milyar TL`;
  }
  if (abs >= 1_000_000) {
    return `${sign}${(abs / 1_000_000).toFixed(1)} Milyon TL`;
  }
  if (abs >= 1_000) {
    return `${sign}${(abs / 1_000).toFixed(1)} Bin TL`;
  }
  return formatTurkishCurrency(value);
}

/**
 * CSS class for positive/negative amounts
 */
export function amountClass(value: number): string {
  if (value > 0) return 'text-[var(--success)]';
  if (value < 0) return 'text-[var(--error)]';
  return 'text-[var(--text-muted)]';
}
