"""
Paylasilmis test fixture'lari.
Mock mizan verileri ve yardimci fonksiyonlar.
"""

import os
import sys
import pytest

# Backend modullerini import edebilmek icin path ayarla
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Test data dizini
TEST_DATA_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "test-data")
)


@pytest.fixture
def basit_xlsx_path():
    """Basit mizan Excel dosya yolu (plain - parser uyumlu)."""
    return os.path.join(TEST_DATA_DIR, "mizan_basit_plain.xlsx")


@pytest.fixture
def kapsamli_xlsx_path():
    """Kapsamli mizan Excel dosya yolu (plain - parser uyumlu)."""
    return os.path.join(TEST_DATA_DIR, "mizan_kapsamli_plain.xlsx")


@pytest.fixture
def basit_xlsx_formatted_path():
    """Basit mizan Excel dosya yolu (formatli - sirket basligi ve grup satirlari)."""
    return os.path.join(TEST_DATA_DIR, "mizan_basit.xlsx")


@pytest.fixture
def kapsamli_xlsx_formatted_path():
    """Kapsamli mizan Excel dosya yolu (formatli)."""
    return os.path.join(TEST_DATA_DIR, "mizan_kapsamli.xlsx")


@pytest.fixture
def basit_csv_path():
    """Basit mizan CSV dosya yolu."""
    return os.path.join(TEST_DATA_DIR, "mizan_basit.csv")


@pytest.fixture
def basit_parsed(basit_xlsx_path):
    """Basit mizan parse edilmis veri."""
    from services.parser import parse_trial_balance
    result = parse_trial_balance(basit_xlsx_path)
    assert result["success"], f"Parse hatasi: {result['errors']}"
    return result["data"]


@pytest.fixture
def kapsamli_parsed(kapsamli_xlsx_path):
    """Kapsamli mizan parse edilmis veri."""
    from services.parser import parse_trial_balance
    result = parse_trial_balance(kapsamli_xlsx_path)
    assert result["success"], f"Parse hatasi: {result['errors']}"
    return result["data"]


@pytest.fixture
def basit_mapped(basit_parsed):
    """Basit mizan mapping sonucu."""
    from services.mapper import map_accounts
    return map_accounts(basit_parsed)


@pytest.fixture
def kapsamli_mapped(kapsamli_parsed):
    """Kapsamli mizan mapping sonucu."""
    from services.mapper import map_accounts
    return map_accounts(kapsamli_parsed)
