"""
Parser servis testleri.
Excel ve CSV dosyalarinin dogru parse edildigini dogrular.
"""

import os
import pytest
import tempfile
from services.parser import parse_trial_balance, _normalize, _match_column


class TestNormalize:
    """Kolon ismi normalizasyon testleri."""

    def test_lowercase(self):
        assert _normalize("HESAP KODU") == "hesap kodu"

    def test_trim(self):
        assert _normalize("  Hesap Kodu  ") == "hesap kodu"

    def test_multiple_spaces(self):
        assert _normalize("Hesap   Kodu") == "hesap kodu"

    def test_turkish_chars(self):
        assert _normalize("Borç Bakiye") == "borc bakiye"
        assert _normalize("Alacak Bakiye") == "alacak bakiye"
        assert _normalize("Hesap Adı") == "hesap adi"
        assert _normalize("Ödeme") == "odeme"
        assert _normalize("Ücret") == "ucret"
        assert _normalize("Şirket") == "sirket"
        assert _normalize("Gönder") == "gonder"


class TestMatchColumn:
    """Kolon pattern eslestirme testleri."""

    def test_hesap_kodu_match(self):
        patterns = [r"hesap\s*kodu", r"hesap\s*no"]
        assert _match_column("Hesap Kodu", patterns) is True
        assert _match_column("HESAP KODU", patterns) is True
        assert _match_column("Hesap  Kodu", patterns) is True

    def test_borc_bakiye_match(self):
        patterns = [r"borc\s*bakiye"]
        assert _match_column("Borç Bakiye", patterns) is True
        assert _match_column("BORC BAKIYE", patterns) is True

    def test_no_match(self):
        patterns = [r"hesap\s*kodu"]
        assert _match_column("Tutar", patterns) is False


class TestParseExcel:
    """Excel dosyasi parse testleri."""

    def test_basit_xlsx_success(self, basit_xlsx_path):
        result = parse_trial_balance(basit_xlsx_path)
        assert result["success"] is True
        assert result["total_rows"] > 0
        assert len(result["errors"]) == 0

    def test_basit_xlsx_row_count(self, basit_xlsx_path):
        result = parse_trial_balance(basit_xlsx_path)
        assert result["total_rows"] == 38

    def test_basit_xlsx_column_mapping(self, basit_xlsx_path):
        result = parse_trial_balance(basit_xlsx_path)
        col_map = result["column_mapping"]
        assert "account_code" in col_map
        assert "account_name" in col_map
        # debit_balance veya debit olmali
        assert "debit_balance" in col_map or "debit" in col_map
        assert "credit_balance" in col_map or "credit" in col_map

    def test_basit_xlsx_first_account(self, basit_xlsx_path):
        result = parse_trial_balance(basit_xlsx_path)
        first = result["data"][0]
        assert first["account_code"] == "100"
        assert first["debit_balance"] > 0

    def test_basit_xlsx_account_structure(self, basit_xlsx_path):
        result = parse_trial_balance(basit_xlsx_path)
        for record in result["data"]:
            assert "account_code" in record
            assert "account_name" in record
            assert "debit_balance" in record
            assert "credit_balance" in record
            assert "net_balance" in record
            # Hesap kodu 3 haneli olmali
            assert len(record["account_code"]) == 3

    def test_kapsamli_xlsx_success(self, kapsamli_xlsx_path):
        result = parse_trial_balance(kapsamli_xlsx_path)
        assert result["success"] is True
        assert result["total_rows"] >= 60  # 65+ hesap bekleniyor

    def test_kapsamli_xlsx_all_groups(self, kapsamli_xlsx_path):
        """Tum TDHP gruplari (1-6) mevcut olmali."""
        result = parse_trial_balance(kapsamli_xlsx_path)
        codes = {r["account_code"][0] for r in result["data"]}
        assert "1" in codes, "1xx hesaplar eksik"
        assert "2" in codes, "2xx hesaplar eksik"
        assert "3" in codes, "3xx hesaplar eksik"
        assert "4" in codes, "4xx hesaplar eksik"
        assert "5" in codes, "5xx hesaplar eksik"
        assert "6" in codes, "6xx hesaplar eksik"


class TestParseCSV:
    """CSV dosyasi parse testleri."""

    def test_basit_csv_success(self, basit_csv_path):
        result = parse_trial_balance(basit_csv_path)
        assert result["success"] is True
        assert result["total_rows"] > 0

    def test_csv_matches_xlsx_row_count(self, basit_xlsx_path, basit_csv_path):
        """CSV ve Excel ayni sayida kayit icermeli."""
        xlsx_result = parse_trial_balance(basit_xlsx_path)
        csv_result = parse_trial_balance(basit_csv_path)
        assert xlsx_result["total_rows"] == csv_result["total_rows"]

    def test_csv_matches_xlsx_accounts(self, basit_xlsx_path, basit_csv_path):
        """CSV ve Excel ayni hesap kodlarini icermeli."""
        xlsx_result = parse_trial_balance(basit_xlsx_path)
        csv_result = parse_trial_balance(basit_csv_path)
        xlsx_codes = {r["account_code"] for r in xlsx_result["data"]}
        csv_codes = {r["account_code"] for r in csv_result["data"]}
        assert xlsx_codes == csv_codes


class TestParseErrors:
    """Hata senaryolari."""

    def test_unsupported_format(self, tmp_path):
        dummy = tmp_path / "test.txt"
        dummy.write_text("dummy")
        result = parse_trial_balance(str(dummy))
        assert result["success"] is False
        assert any("Desteklenmeyen" in e for e in result["errors"])

    def test_nonexistent_file(self):
        result = parse_trial_balance("nonexistent_file.xlsx")
        assert result["success"] is False
        assert len(result["errors"]) > 0

    def test_empty_xlsx(self, tmp_path):
        """Bos Excel dosyasi."""
        from openpyxl import Workbook
        wb = Workbook()
        path = str(tmp_path / "empty.xlsx")
        wb.save(path)
        result = parse_trial_balance(path)
        assert result["success"] is False


class TestMizanDengesi:
    """Mizan dengesi kontrolu (borc toplami = alacak toplami)."""

    def test_basit_mizan_dengesi(self, basit_parsed):
        toplam_borc = sum(r["debit_balance"] for r in basit_parsed)
        toplam_alacak = sum(r["credit_balance"] for r in basit_parsed)
        assert abs(toplam_borc - toplam_alacak) < 0.01, (
            f"Basit mizan dengesiz: Borc={toplam_borc:.2f}, Alacak={toplam_alacak:.2f}"
        )

    def test_kapsamli_mizan_dengesi(self, kapsamli_parsed):
        toplam_borc = sum(r["debit_balance"] for r in kapsamli_parsed)
        toplam_alacak = sum(r["credit_balance"] for r in kapsamli_parsed)
        assert abs(toplam_borc - toplam_alacak) < 0.01, (
            f"Kapsamli mizan dengesiz: Borc={toplam_borc:.2f}, Alacak={toplam_alacak:.2f}"
        )
