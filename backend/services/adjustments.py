"""
IFRS düzeltme motoru.
Amortisman, reeskont, kıdem tazminatı, şüpheli alacak (ECL), ertelenmiş vergi düzeltmeleri.
Her düzeltme borç/alacak çifti olarak kaydedilir.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime


@dataclass
class AdjustmentEntry:
    """Bir düzeltme fişi satırı."""
    entry_id: int
    adjustment_type: str
    description: str
    description_tr: str
    debit_account: str
    debit_account_name: str
    debit_amount: float
    credit_account: str
    credit_account_name: str
    credit_amount: float

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class AdjustmentResult:
    """Düzeltme sonucu."""
    adjustment_type: str
    label_tr: str
    label_en: str
    entries: list[AdjustmentEntry] = field(default_factory=list)
    total_impact: float = 0.0
    applied: bool = False
    parameters: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "adjustment_type": self.adjustment_type,
            "label_tr": self.label_tr,
            "label_en": self.label_en,
            "entries": [e.to_dict() for e in self.entries],
            "total_impact": round(self.total_impact, 2),
            "applied": self.applied,
            "parameters": self.parameters,
        }


_entry_counter = 0


def _next_entry_id() -> int:
    global _entry_counter
    _entry_counter += 1
    return _entry_counter


def reset_entry_counter():
    global _entry_counter
    _entry_counter = 0


def calculate_depreciation_adjustment(
    mapped_accounts: list[dict],
    tdhp_rate: float = 0.20,
    ifrs_rate: float = 0.10,
    asset_codes: list[str] | None = None,
) -> AdjustmentResult:
    """
    Amortisman düzeltmesi: TDHP oranı ile IFRS oranı arasındaki fark.
    TDHP'de fazla ayrılan amortisman iptal edilir.

    Args:
        mapped_accounts: Mapping yapılmış hesap listesi
        tdhp_rate: TDHP amortisman oranı (yıllık)
        ifrs_rate: IFRS amortisman oranı (yıllık)
        asset_codes: Düzeltme yapılacak varlık hesap kodları (default: 252-256)
    """
    result = AdjustmentResult(
        adjustment_type="depreciation",
        label_tr="Amortisman Düzeltmesi",
        label_en="Depreciation Adjustment",
        parameters={"tdhp_rate": tdhp_rate, "ifrs_rate": ifrs_rate},
    )

    if asset_codes is None:
        asset_codes = ["252", "253", "254", "255", "256"]

    # Brüt varlık değerlerini topla
    total_gross_assets = 0.0
    for acc in mapped_accounts:
        if acc["account_code"] in asset_codes and acc.get("balance_type") == "debit":
            total_gross_assets += acc["debit_balance"]

    if total_gross_assets == 0:
        return result

    # Fark hesapla: TDHP'de fazla ayrılan amortisman
    tdhp_depreciation = total_gross_assets * tdhp_rate
    ifrs_depreciation = total_gross_assets * ifrs_rate
    difference = tdhp_depreciation - ifrs_depreciation

    if abs(difference) < 0.01:
        return result

    if difference > 0:
        # TDHP'de fazla amortisman ayrılmış → iptal et
        entry = AdjustmentEntry(
            entry_id=_next_entry_id(),
            adjustment_type="depreciation",
            description="Reversal of excess depreciation (TDHP rate > IFRS rate)",
            description_tr="Fazla ayrılan amortismanın iptali (TDHP oranı > IFRS oranı)",
            debit_account="257",
            debit_account_name="Birikmiş Amortismanlar",
            debit_amount=round(difference, 2),
            credit_account="632",
            credit_account_name="Genel Yönetim Giderleri (Amortisman düzeltme)",
            credit_amount=round(difference, 2),
        )
    else:
        # IFRS'de daha fazla amortisman gerekli → ek amortisman
        diff_abs = abs(difference)
        entry = AdjustmentEntry(
            entry_id=_next_entry_id(),
            adjustment_type="depreciation",
            description="Additional depreciation required (IFRS rate > TDHP rate)",
            description_tr="Ek amortisman ayrılması (IFRS oranı > TDHP oranı)",
            debit_account="632",
            debit_account_name="Genel Yönetim Giderleri (Amortisman düzeltme)",
            debit_amount=round(diff_abs, 2),
            credit_account="257",
            credit_account_name="Birikmiş Amortismanlar",
            credit_amount=round(diff_abs, 2),
        )

    result.entries.append(entry)
    result.total_impact = round(difference, 2)
    result.applied = True
    return result


def calculate_rediscount_adjustment(
    mapped_accounts: list[dict],
    annual_interest_rate: float = 0.50,
    average_maturity_days: int = 90,
) -> AdjustmentResult:
    """
    Reeskont düzeltmesi: Alacak ve borç senetlerinin bugünkü değere indirgenmesi.
    """
    result = AdjustmentResult(
        adjustment_type="rediscount",
        label_tr="Reeskont Düzeltmesi",
        label_en="Rediscount Adjustment",
        parameters={
            "annual_interest_rate": annual_interest_rate,
            "average_maturity_days": average_maturity_days,
        },
    )

    # Alacak senetleri (121)
    receivable_notes = sum(
        acc["debit_balance"]
        for acc in mapped_accounts
        if acc["account_code"] == "121"
    )

    # Borç senetleri (321)
    payable_notes = sum(
        acc["credit_balance"]
        for acc in mapped_accounts
        if acc["account_code"] == "321"
    )

    discount_factor = annual_interest_rate * (average_maturity_days / 365)

    # Alacak senetleri reeskontu
    if receivable_notes > 0:
        receivable_discount = receivable_notes * discount_factor
        entry = AdjustmentEntry(
            entry_id=_next_entry_id(),
            adjustment_type="rediscount",
            description=f"Rediscount on trade receivable notes ({average_maturity_days} days, {annual_interest_rate*100:.0f}%)",
            description_tr=f"Alacak senetleri reeskontu ({average_maturity_days} gün, %{annual_interest_rate*100:.0f})",
            debit_account="657",
            debit_account_name="Reeskont Faiz Giderleri",
            debit_amount=round(receivable_discount, 2),
            credit_account="122",
            credit_account_name="Alacak Senetleri Reeskontu (-)",
            credit_amount=round(receivable_discount, 2),
        )
        result.entries.append(entry)
        result.total_impact -= receivable_discount

    # Borç senetleri reeskontu
    if payable_notes > 0:
        payable_discount = payable_notes * discount_factor
        entry = AdjustmentEntry(
            entry_id=_next_entry_id(),
            adjustment_type="rediscount",
            description=f"Rediscount on trade payable notes ({average_maturity_days} days, {annual_interest_rate*100:.0f}%)",
            description_tr=f"Borç senetleri reeskontu ({average_maturity_days} gün, %{annual_interest_rate*100:.0f})",
            debit_account="322",
            debit_account_name="Borç Senetleri Reeskontu (-)",
            debit_amount=round(payable_discount, 2),
            credit_account="647",
            credit_account_name="Reeskont Faiz Gelirleri",
            credit_amount=round(payable_discount, 2),
        )
        result.entries.append(entry)
        result.total_impact += payable_discount

    if result.entries:
        result.applied = True
    result.total_impact = round(result.total_impact, 2)
    return result


def calculate_severance_pay_adjustment(
    mapped_accounts: list[dict],
    employee_count: int = 50,
    average_service_years: float = 5.0,
    severance_pay_ceiling: float = 23489.83,
    discount_rate: float = 0.20,
    salary_increase_rate: float = 0.30,
    turnover_rate: float = 0.10,
) -> AdjustmentResult:
    """
    Kıdem tazminatı karşılığı düzeltmesi.
    Basitleştirilmiş aktüeryal değerleme: Projected Unit Credit yöntemi simülasyonu.
    """
    result = AdjustmentResult(
        adjustment_type="severance_pay",
        label_tr="Kıdem Tazminatı Karşılığı Düzeltmesi",
        label_en="Severance Pay Provision Adjustment (IAS 19)",
        parameters={
            "employee_count": employee_count,
            "average_service_years": average_service_years,
            "severance_pay_ceiling": severance_pay_ceiling,
            "discount_rate": discount_rate,
            "salary_increase_rate": salary_increase_rate,
            "turnover_rate": turnover_rate,
        },
    )

    # Mevcut karşılık tutarı (372 + 472)
    existing_provision = 0.0
    for acc in mapped_accounts:
        if acc["account_code"] in ("372", "472"):
            existing_provision += acc["credit_balance"]

    # Basitleştirilmiş aktüeryal hesaplama
    # Her çalışan için: tavan * hizmet yılı * (1 - devir oranı) * iskonto
    probability_factor = 1 - turnover_rate
    growth_factor = (1 + salary_increase_rate) / (1 + discount_rate)
    projected_per_employee = severance_pay_ceiling * average_service_years * probability_factor * (growth_factor ** average_service_years)
    total_obligation = projected_per_employee * employee_count

    difference = total_obligation - existing_provision

    if abs(difference) < 0.01:
        return result

    if difference > 0:
        # Ek karşılık ayrılması gerekiyor
        entry = AdjustmentEntry(
            entry_id=_next_entry_id(),
            adjustment_type="severance_pay",
            description=f"Additional severance pay provision (IAS 19 actuarial valuation)",
            description_tr="Ek kıdem tazminatı karşılığı (TMS 19 aktüeryal değerleme)",
            debit_account="654",
            debit_account_name="Karşılık Giderleri",
            debit_amount=round(difference, 2),
            credit_account="472",
            credit_account_name="Kıdem Tazminatı Karşılığı (Uzun Vadeli)",
            credit_amount=round(difference, 2),
        )
    else:
        # Fazla karşılık → iptal
        diff_abs = abs(difference)
        entry = AdjustmentEntry(
            entry_id=_next_entry_id(),
            adjustment_type="severance_pay",
            description="Reversal of excess severance pay provision",
            description_tr="Fazla kıdem tazminatı karşılığının iptali",
            debit_account="472",
            debit_account_name="Kıdem Tazminatı Karşılığı (Uzun Vadeli)",
            debit_amount=round(diff_abs, 2),
            credit_account="644",
            credit_account_name="Konusu Kalmayan Karşılıklar",
            credit_amount=round(diff_abs, 2),
        )

    result.entries.append(entry)
    result.total_impact = round(difference, 2)
    result.applied = True
    return result


def calculate_expected_credit_loss(
    mapped_accounts: list[dict],
    ecl_rate_current: float = 0.01,
    ecl_rate_overdue_30: float = 0.05,
    ecl_rate_overdue_90: float = 0.15,
    ecl_rate_overdue_180: float = 0.50,
    overdue_distribution: dict | None = None,
) -> AdjustmentResult:
    """
    IFRS 9 Beklenen Kredi Zararı (ECL) düzeltmesi.
    Basitleştirilmiş yaklaşım: yaşlandırma tablosuna göre ECL hesaplama.
    """
    result = AdjustmentResult(
        adjustment_type="expected_credit_loss",
        label_tr="Beklenen Kredi Zararı Düzeltmesi (TFRS 9)",
        label_en="Expected Credit Loss Adjustment (IFRS 9)",
        parameters={
            "ecl_rate_current": ecl_rate_current,
            "ecl_rate_overdue_30": ecl_rate_overdue_30,
            "ecl_rate_overdue_90": ecl_rate_overdue_90,
            "ecl_rate_overdue_180": ecl_rate_overdue_180,
        },
    )

    # Ticari alacaklar toplamı (120, 121 borç bakiye)
    total_receivables = 0.0
    for acc in mapped_accounts:
        if acc["account_code"] in ("120", "121"):
            total_receivables += acc["debit_balance"]

    if total_receivables == 0:
        return result

    # Mevcut şüpheli alacak karşılığı (129)
    existing_provision = sum(
        acc["credit_balance"]
        for acc in mapped_accounts
        if acc["account_code"] == "129"
    )

    # Yaşlandırma dağılımı (default varsayım)
    if overdue_distribution is None:
        overdue_distribution = {
            "current": 0.60,
            "overdue_30": 0.20,
            "overdue_90": 0.12,
            "overdue_180": 0.08,
        }

    # ECL hesaplama
    ecl = (
        total_receivables * overdue_distribution.get("current", 0.6) * ecl_rate_current
        + total_receivables * overdue_distribution.get("overdue_30", 0.2) * ecl_rate_overdue_30
        + total_receivables * overdue_distribution.get("overdue_90", 0.12) * ecl_rate_overdue_90
        + total_receivables * overdue_distribution.get("overdue_180", 0.08) * ecl_rate_overdue_180
    )

    difference = ecl - existing_provision

    if abs(difference) < 0.01:
        return result

    if difference > 0:
        entry = AdjustmentEntry(
            entry_id=_next_entry_id(),
            adjustment_type="expected_credit_loss",
            description="Additional expected credit loss provision (IFRS 9 simplified approach)",
            description_tr="Ek beklenen kredi zararı karşılığı (TFRS 9 basitleştirilmiş yaklaşım)",
            debit_account="654",
            debit_account_name="Karşılık Giderleri",
            debit_amount=round(difference, 2),
            credit_account="129",
            credit_account_name="Şüpheli Ticari Alacaklar Karşılığı (-)",
            credit_amount=round(difference, 2),
        )
    else:
        diff_abs = abs(difference)
        entry = AdjustmentEntry(
            entry_id=_next_entry_id(),
            adjustment_type="expected_credit_loss",
            description="Reversal of excess doubtful receivables provision",
            description_tr="Fazla şüpheli alacak karşılığının iptali",
            debit_account="129",
            debit_account_name="Şüpheli Ticari Alacaklar Karşılığı (-)",
            debit_amount=round(diff_abs, 2),
            credit_account="644",
            credit_account_name="Konusu Kalmayan Karşılıklar",
            credit_amount=round(diff_abs, 2),
        )

    result.entries.append(entry)
    result.total_impact = round(difference, 2)
    result.applied = True
    return result


def calculate_deferred_tax(
    adjustment_results: list[AdjustmentResult],
    tax_rate: float = 0.25,
) -> AdjustmentResult:
    """
    Ertelenmiş vergi hesaplama: Diğer düzeltmelerin yarattığı geçici farklar üzerinden.
    """
    result = AdjustmentResult(
        adjustment_type="deferred_tax",
        label_tr="Ertelenmiş Vergi Düzeltmesi (TMS 12)",
        label_en="Deferred Tax Adjustment (IAS 12)",
        parameters={"tax_rate": tax_rate},
    )

    # Tüm düzeltmelerin toplam kar/zarar etkisi
    total_temporary_diff = 0.0
    for adj in adjustment_results:
        if adj.applied and adj.adjustment_type != "deferred_tax":
            total_temporary_diff += adj.total_impact

    if abs(total_temporary_diff) < 0.01:
        return result

    deferred_tax = total_temporary_diff * tax_rate

    if deferred_tax > 0:
        # Düzeltmeler karı artırdı → ertelenmiş vergi yükümlülüğü
        entry = AdjustmentEntry(
            entry_id=_next_entry_id(),
            adjustment_type="deferred_tax",
            description=f"Deferred tax liability on temporary differences (rate: {tax_rate*100:.0f}%)",
            description_tr=f"Geçici farklar üzerinden ertelenmiş vergi yükümlülüğü (oran: %{tax_rate*100:.0f})",
            debit_account="691",
            debit_account_name="Dönem Karı Vergi ve Yasal Yük. Karşılıkları",
            debit_amount=round(abs(deferred_tax), 2),
            credit_account="481_DT",
            credit_account_name="Ertelenmiş Vergi Yükümlülüğü",
            credit_amount=round(abs(deferred_tax), 2),
        )
    else:
        # Düzeltmeler karı azalttı → ertelenmiş vergi varlığı
        entry = AdjustmentEntry(
            entry_id=_next_entry_id(),
            adjustment_type="deferred_tax",
            description=f"Deferred tax asset on temporary differences (rate: {tax_rate*100:.0f}%)",
            description_tr=f"Geçici farklar üzerinden ertelenmiş vergi varlığı (oran: %{tax_rate*100:.0f})",
            debit_account="295_DT",
            debit_account_name="Ertelenmiş Vergi Varlığı",
            debit_amount=round(abs(deferred_tax), 2),
            credit_account="691",
            credit_account_name="Dönem Karı Vergi ve Yasal Yük. Karşılıkları",
            credit_amount=round(abs(deferred_tax), 2),
        )

    result.entries.append(entry)
    result.total_impact = round(deferred_tax, 2)
    result.applied = True
    return result


def apply_all_adjustments(
    mapped_accounts: list[dict],
    params: dict | None = None,
) -> list[AdjustmentResult]:
    """
    Tüm düzeltmeleri sırayla uygula.

    Args:
        mapped_accounts: Eşleştirilmiş hesap listesi
        params: Her düzeltme tipi için parametreler
            {
                "depreciation": {"tdhp_rate": 0.20, "ifrs_rate": 0.10},
                "rediscount": {"annual_interest_rate": 0.50, "average_maturity_days": 90},
                "severance_pay": {"employee_count": 50, ...},
                "expected_credit_loss": {"ecl_rate_current": 0.01, ...},
                "deferred_tax": {"tax_rate": 0.25},
            }
    """
    reset_entry_counter()
    if params is None:
        params = {}

    results = []

    # 1. Amortisman
    dep_params = params.get("depreciation", {})
    dep_result = calculate_depreciation_adjustment(mapped_accounts, **dep_params)
    results.append(dep_result)

    # 2. Reeskont
    red_params = params.get("rediscount", {})
    red_result = calculate_rediscount_adjustment(mapped_accounts, **red_params)
    results.append(red_result)

    # 3. Kıdem Tazminatı
    sev_params = params.get("severance_pay", {})
    sev_result = calculate_severance_pay_adjustment(mapped_accounts, **sev_params)
    results.append(sev_result)

    # 4. Beklenen Kredi Zararı
    ecl_params = params.get("expected_credit_loss", {})
    ecl_result = calculate_expected_credit_loss(mapped_accounts, **ecl_params)
    results.append(ecl_result)

    # 5. Ertelenmiş Vergi (diğer düzeltmelere bağlı)
    dt_params = params.get("deferred_tax", {})
    dt_result = calculate_deferred_tax(results, **dt_params)
    results.append(dt_result)

    return results
