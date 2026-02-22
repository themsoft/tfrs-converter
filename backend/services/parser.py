"""
Excel/CSV mizan dosyası parser servisi.
Hesap kodu, hesap adı, borç, alacak kolonlarını otomatik algılar.
"""

import pandas as pd
import re
from pathlib import Path


# Kolon ismi eşleştirme için aday isimler (büyük/küçük harf duyarsız)
COLUMN_PATTERNS = {
    "account_code": [
        r"hesap\s*kodu", r"hesap\s*no", r"account\s*code", r"account\s*no",
        r"kod", r"code", r"no"
    ],
    "account_name": [
        r"hesap\s*adi", r"hesap\s*ismi", r"account\s*name", r"aciklama",
        r"tanim", r"description", r"name"
    ],
    "debit": [
        r"borc$", r"borc\s*tutar", r"debit", r"borc\s*bakiye"
    ],
    "credit": [
        r"alacak$", r"alacak\s*tutar", r"credit", r"alacak\s*bakiye"
    ],
    "debit_balance": [
        r"borc\s*bakiye", r"borc\s*kalan", r"debit\s*balance"
    ],
    "credit_balance": [
        r"alacak\s*bakiye", r"alacak\s*kalan", r"credit\s*balance"
    ],
}


def _normalize(text: str) -> str:
    """Kolon ismini normalize et: küçük harf, trim, çoklu boşluk → tek boşluk."""
    text = str(text).strip().lower()
    text = re.sub(r"\s+", " ", text)
    # Türkçe karakter dönüşümleri
    tr_map = str.maketrans("çğıöşü", "cgiosu")
    text = text.translate(tr_map)
    return text


def _match_column(col_name: str, patterns: list[str]) -> bool:
    """Bir kolon isminin pattern listesindeki herhangi biriyle eşleşip eşleşmediğini kontrol et."""
    norm = _normalize(col_name)
    for pat in patterns:
        if re.search(pat, norm):
            return True
    return False


def _detect_columns(df: pd.DataFrame) -> dict[str, str | None]:
    """DataFrame kolonlarını otomatik algıla ve standart isimlere eşle."""
    mapping = {}
    used_cols = set()

    # Önce daha spesifik pattern'leri kontrol et (balance önce)
    for field in ["debit_balance", "credit_balance", "account_code", "account_name", "debit", "credit"]:
        patterns = COLUMN_PATTERNS[field]
        for col in df.columns:
            if col in used_cols:
                continue
            if _match_column(col, patterns):
                mapping[field] = col
                used_cols.add(col)
                break

    # debit_balance ve credit_balance yoksa, debit/credit'i bakiye olarak da kullan
    if "debit_balance" not in mapping and "debit" in mapping:
        mapping["debit_balance"] = mapping["debit"]
    if "credit_balance" not in mapping and "credit" in mapping:
        mapping["credit_balance"] = mapping["credit"]

    return mapping


def parse_trial_balance(file_path: str) -> dict:
    """
    Mizan dosyasını parse et.

    Returns:
        dict: {
            "success": bool,
            "data": list[dict],  # Her satır bir hesap
            "column_mapping": dict,
            "total_rows": int,
            "errors": list[str]
        }
    """
    errors = []
    path = Path(file_path)

    try:
        if path.suffix.lower() in (".xlsx", ".xls"):
            df = pd.read_excel(file_path, dtype={"Hesap Kodu": str, "Account Code": str})
        elif path.suffix.lower() == ".csv":
            # Önce utf-8, olmazsa cp1254 (Türkçe Windows)
            try:
                df = pd.read_csv(file_path, encoding="utf-8", dtype=str)
            except UnicodeDecodeError:
                df = pd.read_csv(file_path, encoding="cp1254", dtype=str)
        else:
            return {"success": False, "data": [], "column_mapping": {}, "total_rows": 0,
                    "errors": [f"Desteklenmeyen dosya formatı: {path.suffix}"]}
    except Exception as e:
        return {"success": False, "data": [], "column_mapping": {}, "total_rows": 0,
                "errors": [f"Dosya okuma hatası: {str(e)}"]}

    # Boş satırları temizle
    df = df.dropna(how="all").reset_index(drop=True)

    if df.empty:
        return {"success": False, "data": [], "column_mapping": {}, "total_rows": 0,
                "errors": ["Dosya boş veya okunabilir veri bulunamadı."]}

    # Kolon eşleştirmesi
    col_map = _detect_columns(df)

    if "account_code" not in col_map:
        errors.append("Hesap kodu kolonu bulunamadı. Beklenen kolon isimleri: Hesap Kodu, Account Code, Kod, No")
    if "debit_balance" not in col_map and "debit" not in col_map:
        errors.append("Borç/Borç Bakiye kolonu bulunamadı.")
    if "credit_balance" not in col_map and "credit" not in col_map:
        errors.append("Alacak/Alacak Bakiye kolonu bulunamadı.")

    if errors:
        return {"success": False, "data": [], "column_mapping": col_map, "total_rows": 0, "errors": errors}

    # Verileri standart formata dönüştür
    records = []
    for idx, row in df.iterrows():
        code_raw = str(row.get(col_map.get("account_code", ""), "")).strip()
        # Hesap kodu boş veya sayısal değilse atla
        code_clean = re.sub(r"[^0-9.]", "", code_raw)
        if not code_clean:
            continue

        # Ana hesap kodu (ilk 3 hane)
        account_code = code_clean.split(".")[0][:3] if "." in code_clean else code_clean[:3]

        name = str(row.get(col_map.get("account_name", ""), "")).strip()

        def to_float(val):
            if pd.isna(val):
                return 0.0
            val = str(val).replace(",", ".").replace(" ", "").strip()
            try:
                return float(val)
            except (ValueError, TypeError):
                return 0.0

        debit_bal = to_float(row.get(col_map.get("debit_balance", ""), 0))
        credit_bal = to_float(row.get(col_map.get("credit_balance", ""), 0))

        records.append({
            "account_code": account_code,
            "account_code_full": code_clean,
            "account_name": name if name and name != "nan" else "",
            "debit_balance": debit_bal,
            "credit_balance": credit_bal,
            "net_balance": debit_bal - credit_bal,
        })

    return {
        "success": True,
        "data": records,
        "column_mapping": col_map,
        "total_rows": len(records),
        "errors": errors,
    }
