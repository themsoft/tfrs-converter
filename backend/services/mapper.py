"""
TDHP → IFRS/TFRS mapping engine.
Hesap kodlarını IFRS kategorilerine eşler, eşleşmeyenleri Unmapped olarak raporlar.
"""

import json
from pathlib import Path


_CONFIG_PATH = Path(__file__).parent.parent / "config" / "mapping.json"
_mapping_cache: dict | None = None


def _load_mapping() -> dict:
    global _mapping_cache
    if _mapping_cache is None:
        with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
            _mapping_cache = json.load(f)
    return _mapping_cache


def map_accounts(trial_balance_data: list[dict]) -> dict:
    """
    Mizan verilerini IFRS kategorilerine eşle.

    Args:
        trial_balance_data: parser'dan gelen hesap listesi

    Returns:
        dict: {
            "mapped": list[dict],      # Eşleşen hesaplar (detaylı)
            "unmapped": list[dict],     # Eşleşmeyen hesaplar
            "summary": dict,            # Kategori bazında toplam
            "statistics": dict          # İstatistikler
        }
    """
    config = _load_mapping()
    accounts_map = config["accounts"]
    categories_meta = config["meta"]["ifrs_categories"]

    mapped = []
    unmapped = []

    for item in trial_balance_data:
        code = item["account_code"]
        mapping_info = accounts_map.get(code)

        if mapping_info:
            mapped.append({
                **item,
                "ifrs_category": mapping_info["ifrs_category"],
                "ifrs_line": mapping_info["ifrs_line"],
                "ifrs_line_tr": mapping_info["ifrs_line_tr"],
                "tdhp_name": mapping_info["tdhp_name"],
                "balance_type": mapping_info["balance_type"],
                "ifrs_note": mapping_info.get("ifrs_note"),
            })
        else:
            unmapped.append({
                **item,
                "ifrs_category": "unmapped",
                "ifrs_line": "Unmapped",
                "ifrs_line_tr": "Eslesmemis",
                "tdhp_name": item.get("account_name", ""),
                "balance_type": "debit" if item["net_balance"] >= 0 else "credit",
            })

    # Kategori bazında özet
    summary = {}
    for cat_key, cat_meta in categories_meta.items():
        cat_items = [m for m in mapped if m["ifrs_category"] == cat_key]
        total = sum(_signed_balance(m) for m in cat_items)
        summary[cat_key] = {
            "label_tr": cat_meta["tr"],
            "label_en": cat_meta["en"],
            "total": round(total, 2),
            "account_count": len(cat_items),
        }

    if unmapped:
        unmapped_total = sum(m["net_balance"] for m in unmapped)
        summary["unmapped"] = {
            "label_tr": "Eslesmemis",
            "label_en": "Unmapped",
            "total": round(unmapped_total, 2),
            "account_count": len(unmapped),
        }

    total_accounts = len(trial_balance_data)
    mapped_count = len(mapped)

    return {
        "mapped": mapped,
        "unmapped": unmapped,
        "summary": summary,
        "statistics": {
            "total_accounts": total_accounts,
            "mapped_count": mapped_count,
            "unmapped_count": len(unmapped),
            "mapping_rate": round(mapped_count / total_accounts * 100, 1) if total_accounts else 0,
        },
    }


def _signed_balance(item: dict) -> float:
    """Hesabın balance_type'ına göre işaretli bakiye döndür."""
    net = item["net_balance"]
    # credit balance_type olan hesaplar negatif net_balance'a sahip olabilir
    # IFRS raporlamada hepsi pozitif gösterilir, burada raw net_balance kullanıyoruz
    return net


def get_mapping_config() -> dict:
    """Mapping konfigürasyonunu döndür (frontend'in görmesi için)."""
    return _load_mapping()


def get_ifrs_line_detail(mapped_accounts: list[dict]) -> dict:
    """IFRS kalem bazında detaylı breakdown."""
    lines = {}
    for m in mapped_accounts:
        line_key = m["ifrs_line"]
        if line_key not in lines:
            lines[line_key] = {
                "ifrs_line": line_key,
                "ifrs_line_tr": m["ifrs_line_tr"],
                "ifrs_category": m["ifrs_category"],
                "total": 0.0,
                "accounts": [],
            }
        lines[line_key]["total"] += m["net_balance"]
        lines[line_key]["accounts"].append({
            "account_code": m["account_code"],
            "account_name": m.get("account_name") or m.get("tdhp_name", ""),
            "net_balance": m["net_balance"],
        })

    for line in lines.values():
        line["total"] = round(line["total"], 2)

    return lines
