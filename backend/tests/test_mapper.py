"""
Mapping engine testleri.
TDHP hesap kodlarinin dogru IFRS kategorilerine eslendigini dogrular.
"""

import pytest
from services.mapper import map_accounts, get_mapping_config, get_ifrs_line_detail


class TestMappingConfig:
    """Mapping konfigurasyonu testleri."""

    def test_config_loads(self):
        config = get_mapping_config()
        assert "meta" in config
        assert "accounts" in config

    def test_config_has_categories(self):
        config = get_mapping_config()
        cats = config["meta"]["ifrs_categories"]
        expected_categories = [
            "current_assets", "non_current_assets",
            "current_liabilities", "non_current_liabilities",
            "equity", "revenue", "cost_of_sales", "operating_expenses",
            "finance_income", "finance_costs", "other_income", "other_expense",
            "tax_expense",
        ]
        for cat in expected_categories:
            assert cat in cats, f"Kategori eksik: {cat}"

    def test_config_has_50_plus_accounts(self):
        config = get_mapping_config()
        assert len(config["accounts"]) >= 50, (
            f"En az 50 hesap mapping'i bekleniyor, {len(config['accounts'])} bulundu"
        )

    def test_config_bilingual_labels(self):
        """Her kategori TR ve EN label icermeli."""
        config = get_mapping_config()
        for key, cat in config["meta"]["ifrs_categories"].items():
            assert "tr" in cat, f"{key} icin Turkce label eksik"
            assert "en" in cat, f"{key} icin Ingilizce label eksik"

    def test_account_structure(self):
        """Her hesap gerekli alanlara sahip olmali."""
        config = get_mapping_config()
        required_fields = ["tdhp_name", "ifrs_category", "ifrs_line", "ifrs_line_tr", "balance_type"]
        for code, acc in config["accounts"].items():
            for field in required_fields:
                assert field in acc, f"Hesap {code} icin {field} alani eksik"


class TestMapAccounts:
    """Hesap eslestirme testleri."""

    def test_basit_all_mapped(self, basit_parsed):
        """Basit mizan: tum hesaplar eslesmeli (yaygın hesap kodlari)."""
        result = map_accounts(basit_parsed)
        # Basit mizanda yaygın kodlar var, hepsi eslesmeli
        assert result["statistics"]["unmapped_count"] == 0, (
            f"Eslesmemis hesaplar: {[u['account_code'] for u in result['unmapped']]}"
        )

    def test_kapsamli_high_mapping_rate(self, kapsamli_parsed):
        """Kapsamli mizan: en az %90 mapping orani."""
        result = map_accounts(kapsamli_parsed)
        rate = result["statistics"]["mapping_rate"]
        assert rate >= 90.0, f"Mapping orani dusuk: %{rate}"

    def test_mapping_result_structure(self, basit_parsed):
        result = map_accounts(basit_parsed)
        assert "mapped" in result
        assert "unmapped" in result
        assert "summary" in result
        assert "statistics" in result

    def test_mapped_item_has_ifrs_fields(self, basit_parsed):
        result = map_accounts(basit_parsed)
        for item in result["mapped"]:
            assert "ifrs_category" in item
            assert "ifrs_line" in item
            assert "ifrs_line_tr" in item
            assert "balance_type" in item

    def test_kasa_maps_to_cash(self, basit_parsed):
        """100 Kasa → Cash and Cash Equivalents"""
        result = map_accounts(basit_parsed)
        kasa = next(m for m in result["mapped"] if m["account_code"] == "100")
        assert kasa["ifrs_category"] == "current_assets"
        assert kasa["ifrs_line"] == "Cash and Cash Equivalents"

    def test_bankalar_maps_to_cash(self, basit_parsed):
        """102 Bankalar → Cash and Cash Equivalents"""
        result = map_accounts(basit_parsed)
        banka = next(m for m in result["mapped"] if m["account_code"] == "102")
        assert banka["ifrs_category"] == "current_assets"
        assert banka["ifrs_line"] == "Cash and Cash Equivalents"

    def test_alicilar_maps_to_receivables(self, basit_parsed):
        """120 Alicilar → Trade Receivables"""
        result = map_accounts(basit_parsed)
        alici = next(m for m in result["mapped"] if m["account_code"] == "120")
        assert alici["ifrs_category"] == "current_assets"
        assert "Receivable" in alici["ifrs_line"]

    def test_binalar_maps_to_ppe(self, basit_parsed):
        """252 Binalar → Property, Plant and Equipment"""
        result = map_accounts(basit_parsed)
        bina = next(m for m in result["mapped"] if m["account_code"] == "252")
        assert bina["ifrs_category"] == "non_current_assets"
        assert "Property" in bina["ifrs_line"]

    def test_banka_kredisi_maps_to_borrowings(self, basit_parsed):
        """300 Banka Kredileri → Short-term Borrowings"""
        result = map_accounts(basit_parsed)
        kredi = next(m for m in result["mapped"] if m["account_code"] == "300")
        assert kredi["ifrs_category"] == "current_liabilities"

    def test_sermaye_maps_to_equity(self, basit_parsed):
        """500 Sermaye → Share Capital"""
        result = map_accounts(basit_parsed)
        sermaye = next(m for m in result["mapped"] if m["account_code"] == "500")
        assert sermaye["ifrs_category"] == "equity"

    def test_yurtici_satislar_maps_to_revenue(self, basit_parsed):
        """600 Yurtici Satislar → Revenue"""
        result = map_accounts(basit_parsed)
        satis = next(m for m in result["mapped"] if m["account_code"] == "600")
        assert satis["ifrs_category"] == "revenue"

    def test_smm_maps_to_cost_of_sales(self, basit_parsed):
        """620 Satilan Mamul Maliyeti → Cost of Sales"""
        result = map_accounts(basit_parsed)
        smm = next(m for m in result["mapped"] if m["account_code"] == "620")
        assert smm["ifrs_category"] == "cost_of_sales"

    def test_vergi_maps_to_tax(self, basit_parsed):
        """691 Donem Kari Vergi Karsiligi → Tax Expense"""
        result = map_accounts(basit_parsed)
        vergi = next(m for m in result["mapped"] if m["account_code"] == "691")
        assert vergi["ifrs_category"] == "tax_expense"


class TestMappingSummary:
    """Kategori bazinda ozet testleri."""

    def test_summary_has_totals(self, basit_mapped):
        summary = basit_mapped["summary"]
        assert "current_assets" in summary
        assert "non_current_assets" in summary
        assert "equity" in summary
        assert "revenue" in summary

    def test_summary_has_labels(self, basit_mapped):
        summary = basit_mapped["summary"]
        for key, val in summary.items():
            assert "label_tr" in val
            assert "label_en" in val
            assert "total" in val
            assert "account_count" in val

    def test_current_assets_positive(self, basit_mapped):
        """Donen varliklar pozitif olmali."""
        ca = basit_mapped["summary"]["current_assets"]
        assert ca["total"] > 0


class TestIfrsLineDetail:
    """IFRS kalem detay testleri."""

    def test_line_detail_structure(self, basit_mapped):
        lines = get_ifrs_line_detail(basit_mapped["mapped"])
        assert len(lines) > 0
        for key, line in lines.items():
            assert "ifrs_line" in line
            assert "ifrs_category" in line
            assert "total" in line
            assert "accounts" in line
            assert len(line["accounts"]) > 0

    def test_cash_equivalents_positive(self, basit_mapped):
        """Nakit ve nakit benzerleri pozitif olmali."""
        lines = get_ifrs_line_detail(basit_mapped["mapped"])
        cash_line = lines.get("Cash and Cash Equivalents")
        assert cash_line is not None
        assert cash_line["total"] > 0
