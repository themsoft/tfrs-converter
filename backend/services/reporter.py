"""
IFRS/TFRS rapor üretici.
Bilanço (Statement of Financial Position) ve Gelir Tablosu (Statement of Profit or Loss) üretir.
Düzeltme öncesi / sonrası karşılaştırma sağlar.
"""

from .adjustments import AdjustmentResult


# Bilanço kalem sıralaması
BALANCE_SHEET_STRUCTURE = {
    "assets": {
        "label_tr": "VARLIKLAR",
        "label_en": "ASSETS",
        "sections": {
            "current_assets": {
                "label_tr": "Dönen Varlıklar",
                "label_en": "Current Assets",
                "lines": [
                    "Cash and Cash Equivalents",
                    "Financial Assets at Fair Value",
                    "Trade Receivables",
                    "Related Party Receivables",
                    "Other Receivables",
                    "Inventories",
                    "Prepayments",
                    "Contract Assets",
                    "Current Tax Assets",
                    "Other Current Assets",
                ],
            },
            "non_current_assets": {
                "label_tr": "Duran Varlıklar",
                "label_en": "Non-current Assets",
                "lines": [
                    "Investments in Associates",
                    "Investments in Subsidiaries",
                    "Property, Plant and Equipment",
                    "Intangible Assets",
                    "Goodwill",
                    "Right-of-use Assets",
                    "Deferred Tax Assets",
                    "Prepayments",
                    "Other Non-current Assets",
                ],
            },
        },
    },
    "liabilities_and_equity": {
        "label_tr": "KAYNAKLAR",
        "label_en": "LIABILITIES AND EQUITY",
        "sections": {
            "current_liabilities": {
                "label_tr": "Kısa Vadeli Yükümlülükler",
                "label_en": "Current Liabilities",
                "lines": [
                    "Short-term Borrowings",
                    "Current Portion of Long-term Borrowings",
                    "Trade Payables",
                    "Employee Benefit Obligations",
                    "Contract Liabilities",
                    "Current Tax Liabilities",
                    "Provisions",
                    "Deferred Revenue",
                    "Accrued Expenses",
                    "Other Payables",
                    "Other Current Liabilities",
                ],
            },
            "non_current_liabilities": {
                "label_tr": "Uzun Vadeli Yükümlülükler",
                "label_en": "Non-current Liabilities",
                "lines": [
                    "Long-term Borrowings",
                    "Long-term Trade Payables",
                    "Employee Benefit Obligations",
                    "Contract Liabilities",
                    "Deferred Revenue",
                    "Accrued Expenses",
                    "Deferred Tax Liabilities",
                    "Other Non-current Liabilities",
                ],
            },
            "equity": {
                "label_tr": "Özkaynaklar",
                "label_en": "Equity",
                "lines": [
                    "Share Capital",
                    "Revaluation Surplus",
                    "Retained Earnings",
                    "Net Income for the Period",
                ],
            },
        },
    },
}

INCOME_STATEMENT_STRUCTURE = [
    {"key": "revenue", "label_en": "Revenue", "label_tr": "Hasılat", "sign": 1},
    {"key": "cost_of_sales", "label_en": "Cost of Sales", "label_tr": "Satışların Maliyeti (-)", "sign": -1},
    {"key": "gross_profit", "label_en": "GROSS PROFIT", "label_tr": "BRÜT KAR", "calculated": True},
    {"key": "operating_expenses", "label_en": "Operating Expenses (-)", "label_tr": "Faaliyet Giderleri (-)", "sign": -1},
    {"key": "other_income", "label_en": "Other Operating Income", "label_tr": "Diğer Faaliyet Gelirleri", "sign": 1},
    {"key": "other_expense", "label_en": "Other Operating Expenses (-)", "label_tr": "Diğer Faaliyet Giderleri (-)", "sign": -1},
    {"key": "operating_profit", "label_en": "OPERATING PROFIT", "label_tr": "FAALİYET KARI", "calculated": True},
    {"key": "finance_income", "label_en": "Finance Income", "label_tr": "Finansman Gelirleri", "sign": 1},
    {"key": "finance_costs", "label_en": "Finance Costs (-)", "label_tr": "Finansman Giderleri (-)", "sign": -1},
    {"key": "profit_before_tax", "label_en": "PROFIT BEFORE TAX", "label_tr": "VERGİ ÖNCESİ KAR", "calculated": True},
    {"key": "tax_expense", "label_en": "Tax Expense (-)", "label_tr": "Vergi Gideri (-)", "sign": -1},
    {"key": "net_profit", "label_en": "NET PROFIT FOR THE PERIOD", "label_tr": "DÖNEM NET KARI", "calculated": True},
]


def _make_line_key(category: str, line_name: str) -> str:
    """Kategori ve kalem adından benzersiz key oluştur."""
    return f"{category}::{line_name}"


def _build_line_totals(mapped_accounts: list[dict]) -> dict[str, float]:
    """IFRS kalem bazında bakiye toplamlarını hesapla (kategori bilgisiyle)."""
    line_totals = {}
    for acc in mapped_accounts:
        category = acc.get("ifrs_category", "unmapped")
        line = acc.get("ifrs_line", "Unmapped")
        key = _make_line_key(category, line)
        if key not in line_totals:
            line_totals[key] = 0.0
        line_totals[key] += acc["net_balance"]
    return line_totals


def _apply_adjustment_effects(line_totals: dict[str, float], adjustments: list[AdjustmentResult]) -> dict[str, float]:
    """
    Düzeltme fişlerinin etkilerini kalem toplamlarına uygula.

    net_balance = debit - credit kuralı:
    - Borç (debit) kaydı → net_balance artar (+)
    - Alacak (credit) kaydı → net_balance azalır (-)

    Bilanço hesapları direkt ilgili IFRS kalemine eşlenir.
    Gelir/Gider (P&L) hesapları ise "Net Income for the Period" üzerinden bilançoya yansır.
    """
    adjusted = dict(line_totals)

    # Bilanço hesapları → (ifrs_category, ifrs_line)
    bs_account_map = {
        "257": ("non_current_assets", "Property, Plant and Equipment"),
        "122": ("current_assets", "Trade Receivables"),
        "322": ("current_liabilities", "Trade Payables"),
        "472": ("non_current_liabilities", "Employee Benefit Obligations"),
        "129": ("current_assets", "Trade Receivables"),
        "481_DT": ("non_current_liabilities", "Deferred Tax Liabilities"),
        "295_DT": ("non_current_assets", "Deferred Tax Assets"),
    }

    # P&L hesapları — bilanço etkisi Net Income üzerinden
    pl_accounts = {"632", "654", "644", "647", "657", "691"}
    net_income_key = _make_line_key("equity", "Net Income for the Period")

    for adj in adjustments:
        if not adj.applied:
            continue
        for entry in adj.entries:
            # BORÇ (debit) tarafı → net_balance artar
            if entry.debit_account in bs_account_map:
                cat, line = bs_account_map[entry.debit_account]
                key = _make_line_key(cat, line)
                adjusted[key] = adjusted.get(key, 0.0) + entry.debit_amount
            elif entry.debit_account in pl_accounts:
                adjusted[net_income_key] = adjusted.get(net_income_key, 0.0) + entry.debit_amount

            # ALACAK (credit) tarafı → net_balance azalır
            if entry.credit_account in bs_account_map:
                cat, line = bs_account_map[entry.credit_account]
                key = _make_line_key(cat, line)
                adjusted[key] = adjusted.get(key, 0.0) - entry.credit_amount
            elif entry.credit_account in pl_accounts:
                adjusted[net_income_key] = adjusted.get(net_income_key, 0.0) - entry.credit_amount

    return adjusted


def _get_category_total(mapped_accounts: list[dict], category: str) -> float:
    """Belirli bir IFRS kategorisinin toplamını al."""
    total = 0.0
    for acc in mapped_accounts:
        if acc.get("ifrs_category") == category:
            total += acc["net_balance"]
    return total


def generate_balance_sheet(
    mapped_accounts: list[dict],
    adjustments: list[AdjustmentResult] | None = None,
) -> dict:
    """IFRS uyumlu bilanço üret."""
    line_totals = _build_line_totals(mapped_accounts)

    if adjustments:
        adjusted_line_totals = _apply_adjustment_effects(line_totals, adjustments)
    else:
        adjusted_line_totals = line_totals

    report = {"sections": {}, "totals": {}}

    for side_key, side_info in BALANCE_SHEET_STRUCTURE.items():
        report["sections"][side_key] = {
            "label_tr": side_info["label_tr"],
            "label_en": side_info["label_en"],
            "sub_sections": {},
            "total": 0.0,
        }

        side_total = 0.0
        for section_key, section_info in side_info["sections"].items():
            section_data = {
                "label_tr": section_info["label_tr"],
                "label_en": section_info["label_en"],
                "lines": [],
                "total": 0.0,
            }

            # Yükümlülük ve özkaynak tarafı credit bakiyeli → negatif net_balance
            # Raporlamada pozitif gösterilmeli
            is_credit_side = side_key == "liabilities_and_equity"

            section_total = 0.0
            for line_name in section_info["lines"]:
                key = _make_line_key(section_key, line_name)
                amount = adjusted_line_totals.get(key, 0.0)
                display_amount = round(-amount if is_credit_side else amount, 2)
                if display_amount != 0:
                    section_data["lines"].append({
                        "name": line_name,
                        "amount": display_amount,
                    })
                    section_total += display_amount

            section_data["total"] = round(section_total, 2)
            report["sections"][side_key]["sub_sections"][section_key] = section_data
            side_total += section_total

        report["sections"][side_key]["total"] = round(side_total, 2)

    # Toplam kontrol
    assets_total = report["sections"]["assets"]["total"]
    liabilities_equity_total = report["sections"]["liabilities_and_equity"]["total"]

    report["totals"] = {
        "total_assets": round(assets_total, 2),
        "total_liabilities_and_equity": round(liabilities_equity_total, 2),
        "is_balanced": abs(assets_total - liabilities_equity_total) < 1.0,
        "difference": round(assets_total - liabilities_equity_total, 2),
    }

    return report


def generate_income_statement(
    mapped_accounts: list[dict],
    adjustments: list[AdjustmentResult] | None = None,
) -> dict:
    """IFRS uyumlu gelir tablosu üret."""
    # Kategori bazında toplamlar
    category_totals = {}
    for acc in mapped_accounts:
        cat = acc.get("ifrs_category", "unmapped")
        if cat not in category_totals:
            category_totals[cat] = 0.0
        # Gelir tablosu hesapları: credit bakiye gelir, debit bakiye gider
        category_totals[cat] += acc["net_balance"]

    # Düzeltme etkileri
    adj_effects = {
        "revenue": 0.0,
        "cost_of_sales": 0.0,
        "operating_expenses": 0.0,
        "other_income": 0.0,
        "other_expense": 0.0,
        "finance_income": 0.0,
        "finance_costs": 0.0,
        "tax_expense": 0.0,
    }

    if adjustments:
        for adj in adjustments:
            if not adj.applied:
                continue
            for entry in adj.entries:
                # Düzeltme etkilerini kategoriye göre dağıt
                _map_adj_to_income(entry, adj_effects)

    lines = []
    running = {}

    for item in INCOME_STATEMENT_STRUCTURE:
        key = item["key"]

        if item.get("calculated"):
            if key == "gross_profit":
                val = running.get("revenue", 0) + running.get("cost_of_sales", 0)
            elif key == "operating_profit":
                val = (running.get("gross_profit", 0)
                       + running.get("operating_expenses", 0)
                       + running.get("other_income", 0)
                       + running.get("other_expense", 0))
            elif key == "profit_before_tax":
                val = (running.get("operating_profit", 0)
                       + running.get("finance_income", 0)
                       + running.get("finance_costs", 0))
            elif key == "net_profit":
                val = running.get("profit_before_tax", 0) + running.get("tax_expense", 0)
            else:
                val = 0

            running[key] = val
            lines.append({
                "key": key,
                "label_en": item["label_en"],
                "label_tr": item["label_tr"],
                "amount": round(val, 2),
                "is_subtotal": True,
            })
        else:
            raw = category_totals.get(key, 0.0)
            # Gelir tablosu hesaplarında: credit bakiye (gelirler) negatif net_balance olur
            # Raporlama: gelirleri pozitif, giderleri negatif göster
            sign = item.get("sign", 1)
            # net_balance: debit - credit. Gelirler credit ağırlıklı → negatif.
            # sign=1 (gelir): -net_balance → pozitif
            # sign=-1 (gider): net_balance zaten pozitif (debit ağırlıklı) → negatif
            if sign == 1:
                val = -raw  # credit bakiyeyi pozitife çevir
            else:
                val = -abs(raw)  # giderleri negatif göster

            # Düzeltme etkisi
            val += adj_effects.get(key, 0.0)

            running[key] = val
            lines.append({
                "key": key,
                "label_en": item["label_en"],
                "label_tr": item["label_tr"],
                "amount": round(val, 2),
                "is_subtotal": False,
            })

    return {"lines": lines}


def _map_adj_to_income(entry, effects: dict):
    """Düzeltme fişi satırını gelir tablosu kategorilerine eşle."""
    income_account_map = {
        "632": "operating_expenses",
        "654": "other_expense",
        "644": "other_income",
        "657": "finance_costs",
        "647": "finance_income",
        "691": "tax_expense",
    }

    # Debit taraf → gider artışı (negatif etki) veya gelir azalışı
    debit_cat = income_account_map.get(entry.debit_account)
    if debit_cat:
        if debit_cat in ("other_income", "finance_income"):
            effects[debit_cat] = effects.get(debit_cat, 0) + entry.debit_amount
        else:
            effects[debit_cat] = effects.get(debit_cat, 0) - entry.debit_amount

    # Credit taraf → gelir artışı veya gider azalışı
    credit_cat = income_account_map.get(entry.credit_account)
    if credit_cat:
        if credit_cat in ("other_income", "finance_income"):
            effects[credit_cat] = effects.get(credit_cat, 0) + entry.credit_amount
        else:
            effects[credit_cat] = effects.get(credit_cat, 0) + entry.credit_amount


def generate_comparison(
    mapped_accounts: list[dict],
    adjustments: list[AdjustmentResult],
) -> dict:
    """Düzeltme öncesi vs sonrası karşılaştırma raporu."""
    bs_before = generate_balance_sheet(mapped_accounts, adjustments=None)
    bs_after = generate_balance_sheet(mapped_accounts, adjustments=adjustments)

    is_before = generate_income_statement(mapped_accounts, adjustments=None)
    is_after = generate_income_statement(mapped_accounts, adjustments=adjustments)

    return {
        "balance_sheet": {
            "before": bs_before,
            "after": bs_after,
        },
        "income_statement": {
            "before": is_before,
            "after": is_after,
        },
        "adjustments_summary": [adj.to_dict() for adj in adjustments if adj.applied],
        "total_adjustment_entries": sum(len(adj.entries) for adj in adjustments if adj.applied),
    }
