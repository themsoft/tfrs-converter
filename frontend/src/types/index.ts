// ---- Upload ----
export interface UploadStatistics {
  total_accounts: number;
  mapped_count: number;
  unmapped_count: number;
  mapping_rate: number;
}

export interface UploadResponse {
  session_id: string;
  file_name: string;
  total_rows: number;
  statistics: UploadStatistics;
  column_mapping: Record<string, string>;
}

// ---- Mapping ----
export interface MappedAccount {
  account_code: string;
  account_code_full?: string;
  account_name: string;
  debit_balance: number;
  credit_balance: number;
  net_balance: number;
  ifrs_category: string;
  ifrs_line: string;
  ifrs_line_tr: string;
  tdhp_name?: string;
  balance_type?: string;
  ifrs_note?: string | null;
}

export interface MappingSummaryItem {
  label_tr: string;
  label_en: string;
  total: number;
  account_count: number;
}

export interface MappingStatistics {
  total_accounts: number;
  mapped_count: number;
  unmapped_count: number;
  mapping_rate: number;
}

export interface IFRSLineDetail {
  ifrs_line: string;
  ifrs_line_tr: string;
  ifrs_category: string;
  total: number;
  accounts: {
    account_code: string;
    account_name: string;
    net_balance: number;
  }[];
}

export interface MappingResponse {
  session_id: string;
  mapped: MappedAccount[];
  unmapped: MappedAccount[];
  summary: Record<string, MappingSummaryItem>;
  statistics: MappingStatistics;
  ifrs_line_detail: Record<string, IFRSLineDetail>;
}

// ---- Adjustments ----
export interface AdjustmentEntry {
  entry_id: number;
  adjustment_type: string;
  description: string;
  description_tr: string;
  debit_account: string;
  debit_account_name: string;
  debit_amount: number;
  credit_account: string;
  credit_account_name: string;
  credit_amount: number;
}

export interface Adjustment {
  adjustment_type: string;
  label_tr: string;
  label_en: string;
  entries: AdjustmentEntry[];
  total_impact: number;
  applied: boolean;
  parameters: Record<string, unknown>;
}

export interface AdjustmentsResponse {
  session_id: string;
  adjustments: Adjustment[];
  total_entries: number;
  applied_count: number;
  message?: string;
}

// ---- Balance Sheet ----
export interface BalanceSheetLine {
  name: string;
  amount: number;
}

export interface BalanceSheetSubSection {
  label_tr: string;
  label_en: string;
  lines: BalanceSheetLine[];
  total: number;
}

export interface BalanceSheetSection {
  label_tr: string;
  label_en: string;
  sub_sections: Record<string, BalanceSheetSubSection>;
  total: number;
}

export interface BalanceSheetTotals {
  total_assets: number;
  total_liabilities_and_equity: number;
  is_balanced: boolean;
  difference: number;
}

export interface BalanceSheetResponse {
  session_id: string;
  report_type: string;
  title_tr: string;
  title_en: string;
  sections: {
    assets: BalanceSheetSection;
    liabilities_and_equity: BalanceSheetSection;
  };
  totals: BalanceSheetTotals;
}

// ---- Income Statement ----
export interface IncomeStatementLine {
  key: string;
  label_en: string;
  label_tr: string;
  amount: number;
  is_subtotal: boolean;
}

export interface IncomeStatementResponse {
  session_id: string;
  report_type: string;
  title_tr: string;
  title_en: string;
  lines: IncomeStatementLine[];
}

// ---- Comparison ----
export interface ComparisonResponse {
  session_id: string;
  report_type: string;
  title_tr: string;
  title_en: string;
  balance_sheet: {
    before: BalanceSheetResponse;
    after: BalanceSheetResponse;
  };
  income_statement: {
    before: IncomeStatementResponse;
    after: IncomeStatementResponse;
  };
  adjustments_summary: Adjustment[];
  total_adjustment_entries: number;
}

// ---- Theme ----
export type ThemeMode = 'light' | 'dark';

// ---- App State ----
export interface AppState {
  sessionId: string | null;
  loading: boolean;
  error: string | null;
}
