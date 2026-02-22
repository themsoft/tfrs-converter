import type {
  MappedAccount,
  UploadResponse,
  MappingResponse,
  AdjustmentsResponse,
  BalanceSheetResponse,
  IncomeStatementResponse,
  ComparisonResponse,
} from '../types';

const MOCK_SESSION_ID = 'mock-session-001';

export const mockMappedAccounts: MappedAccount[] = [
  { account_code: '100', account_name: 'Kasa', debit_balance: 150000, credit_balance: 125000, net_balance: 25000, ifrs_category: 'current_assets', ifrs_line: 'Cash and Cash Equivalents', ifrs_line_tr: 'Nakit ve Nakit Benzerleri' },
  { account_code: '101', account_name: 'Alınan Çekler', debit_balance: 80000, credit_balance: 45000, net_balance: 35000, ifrs_category: 'current_assets', ifrs_line: 'Cash and Cash Equivalents', ifrs_line_tr: 'Nakit ve Nakit Benzerleri' },
  { account_code: '102', account_name: 'Bankalar', debit_balance: 2500000, credit_balance: 1800000, net_balance: 700000, ifrs_category: 'current_assets', ifrs_line: 'Cash and Cash Equivalents', ifrs_line_tr: 'Nakit ve Nakit Benzerleri' },
  { account_code: '120', account_name: 'Alıcılar', debit_balance: 1200000, credit_balance: 850000, net_balance: 350000, ifrs_category: 'current_assets', ifrs_line: 'Trade Receivables', ifrs_line_tr: 'Ticari Alacaklar' },
  { account_code: '121', account_name: 'Alacak Senetleri', debit_balance: 450000, credit_balance: 200000, net_balance: 250000, ifrs_category: 'current_assets', ifrs_line: 'Trade Receivables', ifrs_line_tr: 'Ticari Alacaklar' },
  { account_code: '150', account_name: 'İlk Madde ve Malzeme', debit_balance: 680000, credit_balance: 520000, net_balance: 160000, ifrs_category: 'current_assets', ifrs_line: 'Inventories', ifrs_line_tr: 'Stoklar' },
  { account_code: '152', account_name: 'Mamuller', debit_balance: 950000, credit_balance: 780000, net_balance: 170000, ifrs_category: 'current_assets', ifrs_line: 'Inventories', ifrs_line_tr: 'Stoklar' },
  { account_code: '153', account_name: 'Ticari Mallar', debit_balance: 1350000, credit_balance: 1100000, net_balance: 250000, ifrs_category: 'current_assets', ifrs_line: 'Inventories', ifrs_line_tr: 'Stoklar' },
  { account_code: '180', account_name: 'Gelecek Aylara Ait Giderler', debit_balance: 45000, credit_balance: 30000, net_balance: 15000, ifrs_category: 'current_assets', ifrs_line: 'Prepayments', ifrs_line_tr: 'Peşin Ödenmiş Giderler' },
  { account_code: '252', account_name: 'Binalar', debit_balance: 3500000, credit_balance: 0, net_balance: 3500000, ifrs_category: 'non_current_assets', ifrs_line: 'Property, Plant and Equipment', ifrs_line_tr: 'Maddi Duran Varlıklar' },
  { account_code: '253', account_name: 'Tesis, Makine ve Cihazlar', debit_balance: 2800000, credit_balance: 0, net_balance: 2800000, ifrs_category: 'non_current_assets', ifrs_line: 'Property, Plant and Equipment', ifrs_line_tr: 'Maddi Duran Varlıklar' },
  { account_code: '254', account_name: 'Taşıtlar', debit_balance: 450000, credit_balance: 0, net_balance: 450000, ifrs_category: 'non_current_assets', ifrs_line: 'Property, Plant and Equipment', ifrs_line_tr: 'Maddi Duran Varlıklar' },
  { account_code: '255', account_name: 'Demirbaşlar', debit_balance: 320000, credit_balance: 0, net_balance: 320000, ifrs_category: 'non_current_assets', ifrs_line: 'Property, Plant and Equipment', ifrs_line_tr: 'Maddi Duran Varlıklar' },
  { account_code: '257', account_name: 'Birikmiş Amortismanlar (-)', debit_balance: 0, credit_balance: 2850000, net_balance: -2850000, ifrs_category: 'non_current_assets', ifrs_line: 'Property, Plant and Equipment', ifrs_line_tr: 'Maddi Duran Varlıklar' },
  { account_code: '300', account_name: 'Banka Kredileri', debit_balance: 500000, credit_balance: 1200000, net_balance: -700000, ifrs_category: 'current_liabilities', ifrs_line: 'Short-term Borrowings', ifrs_line_tr: 'Kısa Vadeli Borçlanmalar' },
  { account_code: '320', account_name: 'Satıcılar', debit_balance: 650000, credit_balance: 1050000, net_balance: -400000, ifrs_category: 'current_liabilities', ifrs_line: 'Trade Payables', ifrs_line_tr: 'Ticari Borçlar' },
  { account_code: '321', account_name: 'Borç Senetleri', debit_balance: 100000, credit_balance: 350000, net_balance: -250000, ifrs_category: 'current_liabilities', ifrs_line: 'Trade Payables', ifrs_line_tr: 'Ticari Borçlar' },
  { account_code: '335', account_name: 'Personele Borçlar', debit_balance: 180000, credit_balance: 290000, net_balance: -110000, ifrs_category: 'current_liabilities', ifrs_line: 'Employee Benefits', ifrs_line_tr: 'Çalışanlara Borçlar' },
  { account_code: '360', account_name: 'Ödenecek Vergi ve Fonlar', debit_balance: 220000, credit_balance: 380000, net_balance: -160000, ifrs_category: 'current_liabilities', ifrs_line: 'Current Tax Liabilities', ifrs_line_tr: 'Vergi Yükümlülükleri' },
  { account_code: '361', account_name: 'Ödenecek Sosyal Güvenlik Kes.', debit_balance: 95000, credit_balance: 155000, net_balance: -60000, ifrs_category: 'current_liabilities', ifrs_line: 'Employee Benefits', ifrs_line_tr: 'Çalışanlara Borçlar' },
  { account_code: '370', account_name: 'Dönem Karı Vergi ve Diğer Yük.', debit_balance: 0, credit_balance: 185000, net_balance: -185000, ifrs_category: 'current_liabilities', ifrs_line: 'Current Tax Liabilities', ifrs_line_tr: 'Vergi Yükümlülükleri' },
  { account_code: '400', account_name: 'Banka Kredileri (Uzun Vadeli)', debit_balance: 200000, credit_balance: 1500000, net_balance: -1300000, ifrs_category: 'non_current_liabilities', ifrs_line: 'Long-term Borrowings', ifrs_line_tr: 'Uzun Vadeli Borçlanmalar' },
  { account_code: '472', account_name: 'Kıdem Tazminatı Karşılığı', debit_balance: 50000, credit_balance: 280000, net_balance: -230000, ifrs_category: 'non_current_liabilities', ifrs_line: 'Employee Benefits (Non-Current)', ifrs_line_tr: 'Çalışanlara Sağlanan Fayda Karşılıkları' },
  { account_code: '500', account_name: 'Sermaye', debit_balance: 0, credit_balance: 2000000, net_balance: -2000000, ifrs_category: 'equity', ifrs_line: 'Share Capital', ifrs_line_tr: 'Ödenmiş Sermaye' },
  { account_code: '540', account_name: 'Yasal Yedekler', debit_balance: 0, credit_balance: 320000, net_balance: -320000, ifrs_category: 'equity', ifrs_line: 'Retained Earnings', ifrs_line_tr: 'Yedekler' },
  { account_code: '570', account_name: 'Geçmiş Yıllar Karları', debit_balance: 0, credit_balance: 680000, net_balance: -680000, ifrs_category: 'equity', ifrs_line: 'Retained Earnings', ifrs_line_tr: 'Geçmiş Yıllar Karları' },
];

export const mockUnmappedAccounts: MappedAccount[] = [
  { account_code: '191', account_name: 'İndirilecek KDV', debit_balance: 280000, credit_balance: 280000, net_balance: 0, ifrs_category: 'unmapped', ifrs_line: 'Unmapped', ifrs_line_tr: 'Eşleşmemiş' },
];

export const mockUploadResponse: UploadResponse = {
  session_id: MOCK_SESSION_ID,
  file_name: 'ornek_mizan_2025.xlsx',
  total_rows: mockMappedAccounts.length + mockUnmappedAccounts.length,
  statistics: {
    total_accounts: 27,
    mapped_count: 26,
    unmapped_count: 1,
    mapping_rate: 96.3,
  },
  column_mapping: {
    account_code: 'Hesap Kodu',
    account_name: 'Hesap Adı',
    debit_balance: 'Borç Bakiye',
    credit_balance: 'Alacak Bakiye',
  },
};

export const mockMappingData: MappingResponse = {
  session_id: MOCK_SESSION_ID,
  mapped: mockMappedAccounts,
  unmapped: mockUnmappedAccounts,
  summary: {
    current_assets: { label_tr: 'Dönen Varlıklar', label_en: 'Current Assets', total: 1955000, account_count: 9 },
    non_current_assets: { label_tr: 'Duran Varlıklar', label_en: 'Non-current Assets', total: 4220000, account_count: 5 },
    current_liabilities: { label_tr: 'Kısa Vadeli Yükümlülükler', label_en: 'Current Liabilities', total: 1865000, account_count: 6 },
    non_current_liabilities: { label_tr: 'Uzun Vadeli Yükümlülükler', label_en: 'Non-current Liabilities', total: 1530000, account_count: 2 },
    equity: { label_tr: 'Özkaynaklar', label_en: 'Equity', total: 3000000, account_count: 3 },
  },
  statistics: {
    total_accounts: 27,
    mapped_count: 26,
    unmapped_count: 1,
    mapping_rate: 96.3,
  },
  ifrs_line_detail: {},
};

export const mockAdjustments: AdjustmentsResponse = {
  session_id: MOCK_SESSION_ID,
  adjustments: [
    {
      adjustment_type: 'depreciation',
      label_tr: 'Amortisman Farkı',
      label_en: 'Depreciation Difference',
      entries: [
        {
          entry_id: 1,
          adjustment_type: 'depreciation',
          description: 'Additional depreciation due to useful life difference (IAS 16)',
          description_tr: 'TFRS kapsamında faydalı ömür farkından kaynaklanan ek amortisman gideri (IAS 16)',
          debit_account: '730',
          debit_account_name: 'Genel Üretim Giderleri',
          debit_amount: 185000,
          credit_account: '257',
          credit_account_name: 'Birikmiş Amortismanlar',
          credit_amount: 185000,
        },
      ],
      total_impact: -185000,
      applied: true,
      parameters: { tdhp_rate: 0.20, ifrs_rate: 0.10 },
    },
    {
      adjustment_type: 'severance_pay',
      label_tr: 'Kıdem Tazminatı Karşılığı',
      label_en: 'Severance Pay Provision',
      entries: [
        {
          entry_id: 2,
          adjustment_type: 'severance_pay',
          description: 'Actuarial severance pay provision difference under IAS 19',
          description_tr: 'IAS 19 kapsamında aktüeryal hesaplama ile kıdem tazminatı karşılığı farkı',
          debit_account: '632',
          debit_account_name: 'Genel Yönetim Giderleri',
          debit_amount: 95000,
          credit_account: '472',
          credit_account_name: 'Kıdem Tazminatı Karşılığı',
          credit_amount: 95000,
        },
      ],
      total_impact: -95000,
      applied: true,
      parameters: { severance_pay_ceiling: 35058.58, discount_rate: 0.035 },
    },
    {
      adjustment_type: 'expected_credit_loss',
      label_tr: 'Beklenen Kredi Zararı (Şüpheli Alacak)',
      label_en: 'Expected Credit Loss',
      entries: [
        {
          entry_id: 3,
          adjustment_type: 'expected_credit_loss',
          description: 'Additional bad debt provision under IFRS 9 expected credit loss model',
          description_tr: 'TFRS 9 beklenen kredi zararı modeline göre ek karşılık ayrılması',
          debit_account: '654',
          debit_account_name: 'Karşılık Giderleri',
          debit_amount: 42000,
          credit_account: '129',
          credit_account_name: 'Şüpheli Ticari Alacaklar Karşılığı',
          credit_amount: 42000,
        },
      ],
      total_impact: -42000,
      applied: true,
      parameters: { ecl_rate_current: 0.01 },
    },
    {
      adjustment_type: 'rediscount',
      label_tr: 'Stok Değer Düşüklüğü',
      label_en: 'Inventory Impairment',
      entries: [
        {
          entry_id: 4,
          adjustment_type: 'rediscount',
          description: 'Inventory impairment under IAS 2 net realizable value test',
          description_tr: 'IAS 2 kapsamında net gerçekleşebilir değer testi sonucu stok değer düşüklüğü',
          debit_account: '623',
          debit_account_name: 'Diğer Satışların Maliyeti',
          debit_amount: 28000,
          credit_account: '158',
          credit_account_name: 'Stok Değer Düşüklüğü Karşılığı',
          credit_amount: 28000,
        },
      ],
      total_impact: -28000,
      applied: true,
      parameters: {},
    },
    {
      adjustment_type: 'deferred_tax',
      label_tr: 'Ertelenmiş Vergi',
      label_en: 'Deferred Tax',
      entries: [
        {
          entry_id: 5,
          adjustment_type: 'deferred_tax',
          description: 'Deferred tax asset/liability calculation on temporary differences under IAS 12',
          description_tr: 'IAS 12 kapsamında geçici farklar üzerinden ertelenmiş vergi varlığı/yükümlülüğü hesaplaması',
          debit_account: '284',
          debit_account_name: 'Ertelenmiş Vergi Varlığı',
          debit_amount: 67500,
          credit_account: '691',
          credit_account_name: 'Ertelenmiş Vergi Geliri',
          credit_amount: 67500,
        },
      ],
      total_impact: 67500,
      applied: true,
      parameters: { tax_rate: 0.25 },
    },
  ],
  total_entries: 5,
  applied_count: 5,
};

export const mockBalanceSheet: BalanceSheetResponse = {
  session_id: MOCK_SESSION_ID,
  report_type: 'balance_sheet',
  title_tr: 'Finansal Durum Tablosu (Bilanço)',
  title_en: 'Statement of Financial Position',
  sections: {
    assets: {
      label_tr: 'VARLIKLAR',
      label_en: 'ASSETS',
      sub_sections: {
        current_assets: {
          label_tr: 'Dönen Varlıklar',
          label_en: 'Current Assets',
          lines: [
            { name: 'Cash and Cash Equivalents', amount: 760000 },
            { name: 'Trade Receivables', amount: 558000 },
            { name: 'Inventories', amount: 552000 },
            { name: 'Prepayments', amount: 15000 },
            { name: 'Deferred Tax Asset', amount: 28000 },
          ],
          total: 1913000,
        },
        non_current_assets: {
          label_tr: 'Duran Varlıklar',
          label_en: 'Non-current Assets',
          lines: [
            { name: 'Property, Plant and Equipment', amount: 4035000 },
          ],
          total: 4035000,
        },
      },
      total: 5948000,
    },
    liabilities_and_equity: {
      label_tr: 'KAYNAKLAR',
      label_en: 'LIABILITIES AND EQUITY',
      sub_sections: {
        current_liabilities: {
          label_tr: 'Kısa Vadeli Yükümlülükler',
          label_en: 'Current Liabilities',
          lines: [
            { name: 'Short-term Borrowings', amount: 700000 },
            { name: 'Trade Payables', amount: 650000 },
            { name: 'Employee Benefits', amount: 170000 },
            { name: 'Current Tax Liabilities', amount: 345000 },
          ],
          total: 1865000,
        },
        non_current_liabilities: {
          label_tr: 'Uzun Vadeli Yükümlülükler',
          label_en: 'Non-current Liabilities',
          lines: [
            { name: 'Long-term Borrowings', amount: 1300000 },
            { name: 'Employee Benefits (Non-Current)', amount: 325000 },
          ],
          total: 1625000,
        },
        equity: {
          label_tr: 'Özkaynaklar',
          label_en: 'Equity',
          lines: [
            { name: 'Share Capital', amount: 2000000 },
            { name: 'Retained Earnings', amount: 1000000 },
            { name: 'Net Profit/(Loss) for the Period', amount: -542000 },
          ],
          total: 2458000,
        },
      },
      total: 5948000,
    },
  },
  totals: {
    total_assets: 5948000,
    total_liabilities_and_equity: 5948000,
    is_balanced: true,
    difference: 0,
  },
};

export const mockIncomeStatement: IncomeStatementResponse = {
  session_id: MOCK_SESSION_ID,
  report_type: 'income_statement',
  title_tr: 'Kâr veya Zarar Tablosu',
  title_en: 'Statement of Profit or Loss',
  lines: [
    { key: 'revenue', label_en: 'Revenue', label_tr: 'Hasılat', amount: 8295000, is_subtotal: false },
    { key: 'cost_of_sales', label_en: 'Cost of Sales', label_tr: 'Satışların Maliyeti (-)', amount: -6028000, is_subtotal: false },
    { key: 'gross_profit', label_en: 'GROSS PROFIT', label_tr: 'BRÜT KÂR', amount: 2267000, is_subtotal: true },
    { key: 'operating_expenses', label_en: 'Operating Expenses (-)', label_tr: 'Faaliyet Giderleri (-)', amount: -1590000, is_subtotal: false },
    { key: 'other_income', label_en: 'Other Operating Income', label_tr: 'Diğer Faaliyet Gelirleri', amount: 215000, is_subtotal: false },
    { key: 'other_expense', label_en: 'Other Operating Expenses (-)', label_tr: 'Diğer Faaliyet Giderleri (-)', amount: -85000, is_subtotal: false },
    { key: 'operating_profit', label_en: 'OPERATING PROFIT', label_tr: 'FAALİYET KÂRI', amount: 807000, is_subtotal: true },
    { key: 'finance_income', label_en: 'Finance Income', label_tr: 'Finansman Gelirleri', amount: 67500, is_subtotal: false },
    { key: 'finance_costs', label_en: 'Finance Costs (-)', label_tr: 'Finansman Giderleri (-)', amount: -150000, is_subtotal: false },
    { key: 'profit_before_tax', label_en: 'PROFIT BEFORE TAX', label_tr: 'VERGİ ÖNCESİ KÂR', amount: 724500, is_subtotal: true },
    { key: 'tax_expense', label_en: 'Tax Expense (-)', label_tr: 'Vergi Gideri (-)', amount: -185000, is_subtotal: false },
    { key: 'net_profit', label_en: 'NET PROFIT FOR THE PERIOD', label_tr: 'DÖNEM NET KÂRI', amount: 539500, is_subtotal: true },
  ],
};

export const mockComparison: ComparisonResponse = {
  session_id: MOCK_SESSION_ID,
  report_type: 'comparison',
  title_tr: 'Düzeltme Öncesi / Sonrası Karşılaştırma',
  title_en: 'Before / After Adjustments Comparison',
  balance_sheet: {
    before: {
      ...mockBalanceSheet,
      sections: {
        assets: {
          ...mockBalanceSheet.sections.assets,
          sub_sections: {
            current_assets: {
              label_tr: 'Dönen Varlıklar', label_en: 'Current Assets',
              lines: [
                { name: 'Cash and Cash Equivalents', amount: 760000 },
                { name: 'Trade Receivables', amount: 600000 },
                { name: 'Inventories', amount: 580000 },
                { name: 'Prepayments', amount: 15000 },
              ],
              total: 1955000,
            },
            non_current_assets: {
              label_tr: 'Duran Varlıklar', label_en: 'Non-current Assets',
              lines: [{ name: 'Property, Plant and Equipment', amount: 4220000 }],
              total: 4220000,
            },
          },
          total: 6175000,
        },
        liabilities_and_equity: {
          ...mockBalanceSheet.sections.liabilities_and_equity,
          total: 6175000,
        },
      },
      totals: { total_assets: 6175000, total_liabilities_and_equity: 6175000, is_balanced: true, difference: 0 },
    },
    after: mockBalanceSheet,
  },
  income_statement: {
    before: {
      session_id: MOCK_SESSION_ID,
      report_type: 'income_statement',
      title_tr: 'Kâr veya Zarar Tablosu',
      title_en: 'Statement of Profit or Loss',
      lines: [
        { key: 'revenue', label_en: 'Revenue', label_tr: 'Hasılat', amount: 8295000, is_subtotal: false },
        { key: 'cost_of_sales', label_en: 'Cost of Sales', label_tr: 'Satışların Maliyeti (-)', amount: -6000000, is_subtotal: false },
        { key: 'gross_profit', label_en: 'GROSS PROFIT', label_tr: 'BRÜT KÂR', amount: 2295000, is_subtotal: true },
        { key: 'operating_expenses', label_en: 'Operating Expenses (-)', label_tr: 'Faaliyet Giderleri (-)', amount: -1310000, is_subtotal: false },
        { key: 'other_income', label_en: 'Other Operating Income', label_tr: 'Diğer Faaliyet Gelirleri', amount: 215000, is_subtotal: false },
        { key: 'other_expense', label_en: 'Other Operating Expenses (-)', label_tr: 'Diğer Faaliyet Giderleri (-)', amount: -85000, is_subtotal: false },
        { key: 'operating_profit', label_en: 'OPERATING PROFIT', label_tr: 'FAALİYET KÂRI', amount: 1115000, is_subtotal: true },
        { key: 'finance_income', label_en: 'Finance Income', label_tr: 'Finansman Gelirleri', amount: 0, is_subtotal: false },
        { key: 'finance_costs', label_en: 'Finance Costs (-)', label_tr: 'Finansman Giderleri (-)', amount: -150000, is_subtotal: false },
        { key: 'profit_before_tax', label_en: 'PROFIT BEFORE TAX', label_tr: 'VERGİ ÖNCESİ KÂR', amount: 965000, is_subtotal: true },
        { key: 'tax_expense', label_en: 'Tax Expense (-)', label_tr: 'Vergi Gideri (-)', amount: -185000, is_subtotal: false },
        { key: 'net_profit', label_en: 'NET PROFIT FOR THE PERIOD', label_tr: 'DÖNEM NET KÂRI', amount: 780000, is_subtotal: true },
      ],
    },
    after: mockIncomeStatement,
  },
  adjustments_summary: mockAdjustments.adjustments,
  total_adjustment_entries: 5,
};

function delay(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

export const mockApi = {
  upload: async (_file: File): Promise<UploadResponse> => {
    await delay(1500);
    return mockUploadResponse;
  },
  getMapping: async (_sessionId: string): Promise<MappingResponse> => {
    await delay(800);
    return mockMappingData;
  },
  applyAdjustments: async (_sessionId: string): Promise<AdjustmentsResponse> => {
    await delay(600);
    return mockAdjustments;
  },
  getAdjustments: async (_sessionId: string): Promise<AdjustmentsResponse> => {
    await delay(600);
    return mockAdjustments;
  },
  getBalanceSheet: async (_sessionId: string): Promise<BalanceSheetResponse> => {
    await delay(700);
    return mockBalanceSheet;
  },
  getIncomeStatement: async (_sessionId: string): Promise<IncomeStatementResponse> => {
    await delay(700);
    return mockIncomeStatement;
  },
  getComparison: async (_sessionId: string): Promise<ComparisonResponse> => {
    await delay(1000);
    return mockComparison;
  },
};
