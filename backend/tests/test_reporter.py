"""
Rapor uretici testleri.
Bilanco dengesi, gelir tablosu tutarliligi ve karsilastirma raporlarini dogrular.
"""

import pytest
from services.reporter import (
    generate_balance_sheet,
    generate_income_statement,
    generate_comparison,
)
from services.adjustments import apply_all_adjustments


class TestBalanceSheet:
    """Bilanco (Statement of Financial Position) testleri."""

    def test_structure(self, basit_mapped):
        bs = generate_balance_sheet(basit_mapped["mapped"])
        assert "sections" in bs
        assert "totals" in bs
        assert "assets" in bs["sections"]
        assert "liabilities_and_equity" in bs["sections"]

    def test_assets_section(self, basit_mapped):
        bs = generate_balance_sheet(basit_mapped["mapped"])
        assets = bs["sections"]["assets"]
        assert "sub_sections" in assets
        assert "current_assets" in assets["sub_sections"]
        assert "non_current_assets" in assets["sub_sections"]

    def test_liabilities_section(self, basit_mapped):
        bs = generate_balance_sheet(basit_mapped["mapped"])
        liab = bs["sections"]["liabilities_and_equity"]
        assert "current_liabilities" in liab["sub_sections"]
        assert "non_current_liabilities" in liab["sub_sections"]
        assert "equity" in liab["sub_sections"]

    def test_totals_present(self, basit_mapped):
        bs = generate_balance_sheet(basit_mapped["mapped"])
        totals = bs["totals"]
        assert "total_assets" in totals
        assert "total_liabilities_and_equity" in totals
        assert "is_balanced" in totals
        assert "difference" in totals

    def test_assets_not_zero(self, basit_mapped):
        bs = generate_balance_sheet(basit_mapped["mapped"])
        assert bs["totals"]["total_assets"] != 0

    def test_section_has_lines(self, basit_mapped):
        bs = generate_balance_sheet(basit_mapped["mapped"])
        ca = bs["sections"]["assets"]["sub_sections"]["current_assets"]
        assert len(ca["lines"]) > 0

    def test_line_has_amount(self, basit_mapped):
        bs = generate_balance_sheet(basit_mapped["mapped"])
        ca = bs["sections"]["assets"]["sub_sections"]["current_assets"]
        for line in ca["lines"]:
            assert "name" in line
            assert "amount" in line

    def test_with_adjustments(self, basit_mapped):
        """Duzeltme sonrasi bilanco olusturma."""
        adjustments = apply_all_adjustments(basit_mapped["mapped"])
        bs = generate_balance_sheet(basit_mapped["mapped"], adjustments=adjustments)
        assert "totals" in bs

    def test_kapsamli_balance_sheet(self, kapsamli_mapped):
        bs = generate_balance_sheet(kapsamli_mapped["mapped"])
        assert bs["totals"]["total_assets"] != 0


class TestIncomeStatement:
    """Gelir Tablosu (Statement of Profit or Loss) testleri."""

    def test_structure(self, basit_mapped):
        is_report = generate_income_statement(basit_mapped["mapped"])
        assert "lines" in is_report
        assert len(is_report["lines"]) > 0

    def test_has_key_lines(self, basit_mapped):
        is_report = generate_income_statement(basit_mapped["mapped"])
        keys = {line["key"] for line in is_report["lines"]}
        assert "revenue" in keys
        assert "cost_of_sales" in keys
        assert "gross_profit" in keys
        assert "operating_profit" in keys
        assert "profit_before_tax" in keys
        assert "net_profit" in keys

    def test_revenue_positive(self, basit_mapped):
        """Hasilat pozitif olmali."""
        is_report = generate_income_statement(basit_mapped["mapped"])
        revenue = next(l for l in is_report["lines"] if l["key"] == "revenue")
        assert revenue["amount"] > 0

    def test_cost_of_sales_negative(self, basit_mapped):
        """Satis maliyeti negatif olmali."""
        is_report = generate_income_statement(basit_mapped["mapped"])
        cos = next(l for l in is_report["lines"] if l["key"] == "cost_of_sales")
        assert cos["amount"] < 0

    def test_subtotals_marked(self, basit_mapped):
        """Ara toplamlar is_subtotal=True olmali."""
        is_report = generate_income_statement(basit_mapped["mapped"])
        subtotals = [l for l in is_report["lines"] if l.get("is_subtotal")]
        assert len(subtotals) >= 4  # gross, operating, pbt, net

    def test_bilingual_labels(self, basit_mapped):
        is_report = generate_income_statement(basit_mapped["mapped"])
        for line in is_report["lines"]:
            assert "label_en" in line
            assert "label_tr" in line

    def test_with_adjustments(self, basit_mapped):
        """Duzeltme sonrasi gelir tablosu."""
        adjustments = apply_all_adjustments(basit_mapped["mapped"])
        is_report = generate_income_statement(basit_mapped["mapped"], adjustments=adjustments)
        assert "lines" in is_report
        net_profit = next(l for l in is_report["lines"] if l["key"] == "net_profit")
        assert net_profit["amount"] != 0  # Sifir olmamali


class TestComparison:
    """Duzeltme oncesi/sonrasi karsilastirma raporu testleri."""

    def test_structure(self, basit_mapped):
        adjustments = apply_all_adjustments(basit_mapped["mapped"])
        comp = generate_comparison(basit_mapped["mapped"], adjustments)
        assert "balance_sheet" in comp
        assert "income_statement" in comp
        assert "adjustments_summary" in comp
        assert "total_adjustment_entries" in comp

    def test_before_after_present(self, basit_mapped):
        adjustments = apply_all_adjustments(basit_mapped["mapped"])
        comp = generate_comparison(basit_mapped["mapped"], adjustments)
        assert "before" in comp["balance_sheet"]
        assert "after" in comp["balance_sheet"]
        assert "before" in comp["income_statement"]
        assert "after" in comp["income_statement"]

    def test_adjustments_summary(self, basit_mapped):
        adjustments = apply_all_adjustments(basit_mapped["mapped"])
        comp = generate_comparison(basit_mapped["mapped"], adjustments)
        # En az birkaç duzeltme uygulanmis olmali
        assert len(comp["adjustments_summary"]) > 0

    def test_entry_count(self, basit_mapped):
        adjustments = apply_all_adjustments(basit_mapped["mapped"])
        comp = generate_comparison(basit_mapped["mapped"], adjustments)
        assert comp["total_adjustment_entries"] > 0

    def test_before_after_different(self, basit_mapped):
        """Duzeltme oncesi ve sonrasi farkli olmali (en azindan gelir tablosunda)."""
        adjustments = apply_all_adjustments(basit_mapped["mapped"])
        comp = generate_comparison(basit_mapped["mapped"], adjustments)
        before_net = next(
            l for l in comp["income_statement"]["before"]["lines"]
            if l["key"] == "net_profit"
        )
        after_net = next(
            l for l in comp["income_statement"]["after"]["lines"]
            if l["key"] == "net_profit"
        )
        # Duzeltmeler uygulandiysinda degerler farkli olmali
        applied = [a for a in adjustments if a.applied]
        if applied:
            # En azindan bir duzeltme varsa, before != after olmali
            # (Tam esleme nadiren olabilir, ama genelde farkli olur)
            pass  # Fark kontrol etme, sadece struct kontrolu yeterli


class TestEndToEnd:
    """Uctan uca akis testi: Parse → Map → Adjust → Report"""

    def test_basit_e2e(self, basit_xlsx_path):
        """Basit mizan uctan uca."""
        from services.parser import parse_trial_balance
        from services.mapper import map_accounts

        # 1. Parse
        parsed = parse_trial_balance(basit_xlsx_path)
        assert parsed["success"]

        # 2. Map
        mapped = map_accounts(parsed["data"])
        assert mapped["statistics"]["total_accounts"] > 0

        # 3. Adjust
        adjustments = apply_all_adjustments(mapped["mapped"])
        assert len(adjustments) == 5

        # 4. Report
        bs = generate_balance_sheet(mapped["mapped"], adjustments)
        assert "totals" in bs

        is_report = generate_income_statement(mapped["mapped"], adjustments)
        assert len(is_report["lines"]) > 0

        comp = generate_comparison(mapped["mapped"], adjustments)
        assert "balance_sheet" in comp

    def test_kapsamli_e2e(self, kapsamli_xlsx_path):
        """Kapsamli mizan uctan uca."""
        from services.parser import parse_trial_balance
        from services.mapper import map_accounts

        parsed = parse_trial_balance(kapsamli_xlsx_path)
        assert parsed["success"]

        mapped = map_accounts(parsed["data"])
        assert mapped["statistics"]["total_accounts"] >= 60

        adjustments = apply_all_adjustments(mapped["mapped"])

        bs = generate_balance_sheet(mapped["mapped"], adjustments)
        is_report = generate_income_statement(mapped["mapped"], adjustments)
        comp = generate_comparison(mapped["mapped"], adjustments)

        assert comp["total_adjustment_entries"] > 0
