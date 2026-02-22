"""
TFRS Converter Backend — FastAPI uygulaması.
TDHP mizan dosyasını IFRS/TFRS formatına dönüştürme API'si.
"""

import uuid
import os
import tempfile
from typing import Any

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from services.parser import parse_trial_balance
from services.mapper import map_accounts, get_mapping_config, get_ifrs_line_detail
from services.adjustments import apply_all_adjustments, AdjustmentResult
from services.reporter import (
    generate_balance_sheet,
    generate_income_statement,
    generate_comparison,
)

app = FastAPI(
    title="TFRS Converter API",
    description="TDHP (Tek Düzen Hesap Planı) mizanını IFRS/TFRS formatına dönüştürme servisi",
    version="1.0.0",
)

# CORS — frontend erişimi için
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session store
sessions: dict[str, dict[str, Any]] = {}


class AdjustmentParams(BaseModel):
    depreciation: dict | None = None
    rediscount: dict | None = None
    severance_pay: dict | None = None
    expected_credit_loss: dict | None = None
    deferred_tax: dict | None = None


def _get_session(session_id: str) -> dict:
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail=f"Session bulunamadı: {session_id}")
    return sessions[session_id]


# ─── Upload ────────────────────────────────────────────────────────────────

@app.post("/api/upload")
async def upload_trial_balance(file: UploadFile = File(...)):
    """Mizan dosyasını yükle, parse et ve mapping yap."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="Dosya adı bulunamadı.")

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in (".xlsx", ".xls", ".csv"):
        raise HTTPException(
            status_code=400,
            detail=f"Desteklenmeyen dosya formatı: {ext}. Desteklenen: .xlsx, .xls, .csv",
        )

    # Geçici dosyaya yaz
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        # Parse
        parse_result = parse_trial_balance(tmp_path)
        if not parse_result["success"]:
            raise HTTPException(status_code=422, detail={
                "message": "Dosya parse edilemedi.",
                "errors": parse_result["errors"],
            })

        # Mapping
        mapping_result = map_accounts(parse_result["data"])

        # Session oluştur
        session_id = str(uuid.uuid4())[:8]
        sessions[session_id] = {
            "file_name": file.filename,
            "parse_result": parse_result,
            "mapping_result": mapping_result,
            "adjustments": None,
        }

        return {
            "session_id": session_id,
            "file_name": file.filename,
            "total_rows": parse_result["total_rows"],
            "statistics": mapping_result["statistics"],
            "column_mapping": parse_result["column_mapping"],
        }
    finally:
        os.unlink(tmp_path)


# ─── Mapping ──────────────────────────────────────────────────────────────

@app.get("/api/mapping/{session_id}")
async def get_mapping(session_id: str):
    """Mapping sonuçlarını getir."""
    session = _get_session(session_id)
    mr = session["mapping_result"]

    return {
        "session_id": session_id,
        "mapped": mr["mapped"],
        "unmapped": mr["unmapped"],
        "summary": mr["summary"],
        "statistics": mr["statistics"],
        "ifrs_line_detail": get_ifrs_line_detail(mr["mapped"]),
    }


@app.get("/api/mapping-config")
async def get_mapping_configuration():
    """Mapping konfigürasyonunu getir (frontend referansı için)."""
    return get_mapping_config()


# ─── Adjustments ──────────────────────────────────────────────────────────

@app.post("/api/adjustments/{session_id}")
async def apply_adjustments(session_id: str, params: AdjustmentParams | None = None):
    """IFRS düzeltmelerini uygula."""
    session = _get_session(session_id)
    mapped = session["mapping_result"]["mapped"]

    param_dict = {}
    if params:
        if params.depreciation:
            param_dict["depreciation"] = params.depreciation
        if params.rediscount:
            param_dict["rediscount"] = params.rediscount
        if params.severance_pay:
            param_dict["severance_pay"] = params.severance_pay
        if params.expected_credit_loss:
            param_dict["expected_credit_loss"] = params.expected_credit_loss
        if params.deferred_tax:
            param_dict["deferred_tax"] = params.deferred_tax

    results: list[AdjustmentResult] = apply_all_adjustments(mapped, param_dict)
    session["adjustments"] = results

    return {
        "session_id": session_id,
        "adjustments": [r.to_dict() for r in results],
        "total_entries": sum(len(r.entries) for r in results if r.applied),
        "applied_count": sum(1 for r in results if r.applied),
    }


@app.get("/api/reports/{session_id}/adjustments")
async def get_adjustments(session_id: str):
    """Düzeltme fişleri listesini getir."""
    session = _get_session(session_id)
    adjustments = session.get("adjustments")

    if not adjustments:
        return {
            "session_id": session_id,
            "message": "Henüz düzeltme uygulanmadı. POST /api/adjustments/{session_id} ile düzeltmeleri uygulayın.",
            "adjustments": [],
        }

    return {
        "session_id": session_id,
        "adjustments": [r.to_dict() for r in adjustments],
        "total_entries": sum(len(r.entries) for r in adjustments if r.applied),
    }


# ─── Reports ──────────────────────────────────────────────────────────────

@app.get("/api/reports/{session_id}/balance-sheet")
async def get_balance_sheet(session_id: str):
    """IFRS bilanço raporu."""
    session = _get_session(session_id)
    mapped = session["mapping_result"]["mapped"]
    adjustments = session.get("adjustments")

    report = generate_balance_sheet(mapped, adjustments)
    return {
        "session_id": session_id,
        "report_type": "balance_sheet",
        "title_tr": "Finansal Durum Tablosu (Bilanço)",
        "title_en": "Statement of Financial Position",
        **report,
    }


@app.get("/api/reports/{session_id}/income-statement")
async def get_income_statement(session_id: str):
    """IFRS gelir tablosu raporu."""
    session = _get_session(session_id)
    mapped = session["mapping_result"]["mapped"]
    adjustments = session.get("adjustments")

    report = generate_income_statement(mapped, adjustments)
    return {
        "session_id": session_id,
        "report_type": "income_statement",
        "title_tr": "Kâr veya Zarar Tablosu",
        "title_en": "Statement of Profit or Loss",
        **report,
    }


@app.get("/api/reports/{session_id}/comparison")
async def get_comparison(session_id: str):
    """Düzeltme öncesi / sonrası karşılaştırma raporu."""
    session = _get_session(session_id)
    mapped = session["mapping_result"]["mapped"]
    adjustments = session.get("adjustments")

    if not adjustments:
        raise HTTPException(
            status_code=400,
            detail="Karşılaştırma için önce düzeltmelerin uygulanması gerekiyor. POST /api/adjustments/{session_id}",
        )

    report = generate_comparison(mapped, adjustments)
    return {
        "session_id": session_id,
        "report_type": "comparison",
        "title_tr": "Düzeltme Öncesi / Sonrası Karşılaştırma",
        "title_en": "Before / After Adjustments Comparison",
        **report,
    }


# ─── Health ───────────────────────────────────────────────────────────────

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "tfrs-converter-backend", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
