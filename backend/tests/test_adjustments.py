"""
Duzeltme motoru testleri.
Amortisman, reeskont, kidem tazminati, ECL ve ertelenmis vergi duzeltmelerini dogrular.
"""

import pytest
from services.adjustments import (
    AdjustmentEntry,
    AdjustmentResult,
    calculate_depreciation_adjustment,
    calculate_rediscount_adjustment,
    calculate_severance_pay_adjustment,
    calculate_expected_credit_loss,
    calculate_deferred_tax,
    apply_all_adjustments,
    reset_entry_counter,
)


@pytest.fixture(autouse=True)
def reset_counter():
    """Her testten once entry counter'i sifirla."""
    reset_entry_counter()


class TestAdjustmentEntry:
    """AdjustmentEntry dataclass testleri."""

    def test_to_dict(self):
        entry = AdjustmentEntry(
            entry_id=1,
            adjustment_type="test",
            description="Test entry",
            description_tr="Test kaydi",
            debit_account="100",
            debit_account_name="Kasa",
            debit_amount=1000.0,
            credit_account="102",
            credit_account_name="Bankalar",
            credit_amount=1000.0,
        )
        d = entry.to_dict()
        assert d["entry_id"] == 1
        assert d["debit_amount"] == 1000.0
        assert d["credit_amount"] == 1000.0
        assert d["debit_amount"] == d["credit_amount"]


class TestDepreciation:
    """Amortisman duzeltmesi testleri."""

    def test_tdhp_higher_rate(self, basit_mapped):
        """TDHP orani > IFRS orani: fazla amortisman iptali."""
        result = calculate_depreciation_adjustment(
            basit_mapped["mapped"],
            tdhp_rate=0.20,
            ifrs_rate=0.10,
        )
        assert result.applied is True
        assert len(result.entries) == 1
        assert result.entries[0].debit_account == "257"  # Birikmis amortisman
        assert result.total_impact > 0  # Kar artisi (fazla gider iptali)

    def test_ifrs_higher_rate(self, basit_mapped):
        """IFRS orani > TDHP orani: ek amortisman."""
        result = calculate_depreciation_adjustment(
            basit_mapped["mapped"],
            tdhp_rate=0.05,
            ifrs_rate=0.15,
        )
        assert result.applied is True
        assert result.entries[0].debit_account == "632"  # Gider artisi
        assert result.total_impact < 0  # Kar dususu

    def test_same_rate_no_adjustment(self, basit_mapped):
        """Ayni oran: duzeltme olmamali."""
        result = calculate_depreciation_adjustment(
            basit_mapped["mapped"],
            tdhp_rate=0.10,
            ifrs_rate=0.10,
        )
        assert result.applied is False
        assert len(result.entries) == 0

    def test_entry_balance(self, basit_mapped):
        """Duzeltme fisi dengeli olmali: borc = alacak."""
        result = calculate_depreciation_adjustment(
            basit_mapped["mapped"],
            tdhp_rate=0.20,
            ifrs_rate=0.10,
        )
        for entry in result.entries:
            assert abs(entry.debit_amount - entry.credit_amount) < 0.01

    def test_parameters_stored(self, basit_mapped):
        result = calculate_depreciation_adjustment(
            basit_mapped["mapped"],
            tdhp_rate=0.20,
            ifrs_rate=0.10,
        )
        assert result.parameters["tdhp_rate"] == 0.20
        assert result.parameters["ifrs_rate"] == 0.10


class TestRediscount:
    """Reeskont duzeltmesi testleri."""

    def test_kapsamli_has_notes(self, kapsamli_mapped):
        """Kapsamli mizan reeskont duzeltmesi icermeli (121, 321 hesaplari var)."""
        result = calculate_rediscount_adjustment(
            kapsamli_mapped["mapped"],
            annual_interest_rate=0.50,
            average_maturity_days=90,
        )
        assert result.applied is True
        assert len(result.entries) >= 1

    def test_basit_no_notes(self, basit_mapped):
        """Basit mizan: 121/321 hesabi yok, duzeltme olmamali."""
        result = calculate_rediscount_adjustment(basit_mapped["mapped"])
        # 121 ve 321 basit mizanda yok
        assert result.applied is False or len(result.entries) == 0

    def test_receivable_discount_entry(self, kapsamli_mapped):
        result = calculate_rediscount_adjustment(
            kapsamli_mapped["mapped"],
            annual_interest_rate=0.50,
            average_maturity_days=90,
        )
        receivable_entries = [
            e for e in result.entries if e.debit_account == "657"
        ]
        if receivable_entries:
            assert receivable_entries[0].credit_account == "122"
            assert receivable_entries[0].debit_amount > 0

    def test_entry_balance(self, kapsamli_mapped):
        result = calculate_rediscount_adjustment(kapsamli_mapped["mapped"])
        for entry in result.entries:
            assert abs(entry.debit_amount - entry.credit_amount) < 0.01


class TestSeverancePay:
    """Kidem tazminati duzeltmesi testleri."""

    def test_additional_provision(self, basit_mapped):
        """Ek karsilik gerekli mi test et."""
        result = calculate_severance_pay_adjustment(
            basit_mapped["mapped"],
            employee_count=50,
            average_service_years=5.0,
        )
        assert result.applied is True
        assert len(result.entries) == 1

    def test_entry_accounts(self, basit_mapped):
        result = calculate_severance_pay_adjustment(basit_mapped["mapped"])
        if result.applied:
            entry = result.entries[0]
            # Ek karsilik: borc 654, alacak 472
            # veya iptal: borc 472, alacak 644
            assert entry.debit_account in ("654", "472")
            assert entry.credit_account in ("472", "644")

    def test_entry_balance(self, basit_mapped):
        result = calculate_severance_pay_adjustment(basit_mapped["mapped"])
        for entry in result.entries:
            assert abs(entry.debit_amount - entry.credit_amount) < 0.01

    def test_parameters_stored(self, basit_mapped):
        result = calculate_severance_pay_adjustment(
            basit_mapped["mapped"],
            employee_count=100,
            average_service_years=7.0,
        )
        assert result.parameters["employee_count"] == 100
        assert result.parameters["average_service_years"] == 7.0


class TestExpectedCreditLoss:
    """Beklenen kredi zarari (IFRS 9 ECL) testleri."""

    def test_ecl_applied(self, basit_mapped):
        """ECL duzeltmesi uygulanmali (120 hesap mevcut)."""
        result = calculate_expected_credit_loss(basit_mapped["mapped"])
        assert result.applied is True

    def test_ecl_accounts(self, basit_mapped):
        result = calculate_expected_credit_loss(basit_mapped["mapped"])
        if result.applied:
            entry = result.entries[0]
            # Ek karsilik: borc 654, alacak 129
            # veya iptal: borc 129, alacak 644
            assert entry.debit_account in ("654", "129")
            assert entry.credit_account in ("129", "644")

    def test_ecl_entry_balance(self, basit_mapped):
        result = calculate_expected_credit_loss(basit_mapped["mapped"])
        for entry in result.entries:
            assert abs(entry.debit_amount - entry.credit_amount) < 0.01

    def test_custom_rates(self, basit_mapped):
        """Farkli ECL oranlari ile test."""
        result = calculate_expected_credit_loss(
            basit_mapped["mapped"],
            ecl_rate_current=0.02,
            ecl_rate_overdue_30=0.10,
            ecl_rate_overdue_90=0.25,
            ecl_rate_overdue_180=0.75,
        )
        assert result.applied is True


class TestDeferredTax:
    """Ertelenmis vergi duzeltmesi testleri."""

    def test_deferred_tax_from_adjustments(self, basit_mapped):
        """Diger duzeltmeler varsa ertelenmis vergi hesaplanmali."""
        dep = calculate_depreciation_adjustment(basit_mapped["mapped"])
        result = calculate_deferred_tax([dep], tax_rate=0.25)
        if dep.applied:
            assert result.applied is True
            expected_tax = abs(dep.total_impact * 0.25)
            assert abs(abs(result.total_impact) - expected_tax) < 0.01

    def test_no_adjustments_no_tax(self):
        """Duzeltme yoksa vergi de yok."""
        result = calculate_deferred_tax([], tax_rate=0.25)
        assert result.applied is False

    def test_entry_balance(self, basit_mapped):
        dep = calculate_depreciation_adjustment(basit_mapped["mapped"])
        result = calculate_deferred_tax([dep])
        for entry in result.entries:
            assert abs(entry.debit_amount - entry.credit_amount) < 0.01


class TestApplyAllAdjustments:
    """Toplu duzeltme uygulama testleri."""

    def test_returns_five_results(self, basit_mapped):
        """5 duzeltme tipi dondurulmeli."""
        results = apply_all_adjustments(basit_mapped["mapped"])
        assert len(results) == 5

    def test_adjustment_types(self, basit_mapped):
        results = apply_all_adjustments(basit_mapped["mapped"])
        types = {r.adjustment_type for r in results}
        expected = {"depreciation", "rediscount", "severance_pay", "expected_credit_loss", "deferred_tax"}
        assert types == expected

    def test_all_entries_balanced(self, basit_mapped):
        """Tum duzeltme fisleri dengeli olmali."""
        results = apply_all_adjustments(basit_mapped["mapped"])
        for adj in results:
            for entry in adj.entries:
                assert abs(entry.debit_amount - entry.credit_amount) < 0.01, (
                    f"{adj.adjustment_type} dengesiz: "
                    f"borc={entry.debit_amount}, alacak={entry.credit_amount}"
                )

    def test_custom_params(self, basit_mapped):
        """Ozel parametrelerle calistirma."""
        params = {
            "depreciation": {"tdhp_rate": 0.25, "ifrs_rate": 0.08},
            "rediscount": {"annual_interest_rate": 0.45, "average_maturity_days": 120},
            "severance_pay": {"employee_count": 30, "average_service_years": 3.0},
            "expected_credit_loss": {"ecl_rate_current": 0.02},
            "deferred_tax": {"tax_rate": 0.22},
        }
        results = apply_all_adjustments(basit_mapped["mapped"], params=params)
        assert len(results) == 5

    def test_entry_ids_sequential(self, basit_mapped):
        """Entry ID'leri sirali olmali."""
        results = apply_all_adjustments(basit_mapped["mapped"])
        ids = []
        for adj in results:
            for entry in adj.entries:
                ids.append(entry.entry_id)
        # ID'ler artan sirali olmali
        for i in range(1, len(ids)):
            assert ids[i] > ids[i - 1]

    def test_to_dict(self, basit_mapped):
        """Sonuclar JSON serializable olmali."""
        results = apply_all_adjustments(basit_mapped["mapped"])
        for adj in results:
            d = adj.to_dict()
            assert isinstance(d, dict)
            assert "adjustment_type" in d
            assert "entries" in d
            assert isinstance(d["entries"], list)
