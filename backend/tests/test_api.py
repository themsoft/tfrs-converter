"""
API integration testleri.
FastAPI endpoint'lerini httpx TestClient ile test eder.
Uctan uca akis: upload → mapping → adjustments → reports
"""

import os
import sys
import pytest
from httpx import AsyncClient, ASGITransport

# Backend modullerini import edebilmek icin path ayarla
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from main import app

TEST_DATA_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "test-data")
)


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.fixture
async def uploaded_session(client):
    """Basit mizan yuklenip session olusturulmus fixture."""
    file_path = os.path.join(TEST_DATA_DIR, "mizan_basit_plain.xlsx")
    with open(file_path, "rb") as f:
        response = await client.post(
            "/api/upload",
            files={"file": ("mizan_basit.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        )
    assert response.status_code == 200
    return response.json()["session_id"]


# ─── Health ──────────────────────────────────────────────────────────────

class TestHealth:
    @pytest.mark.anyio
    async def test_health_check(self, client):
        response = await client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "tfrs-converter-backend"


# ─── Upload ──────────────────────────────────────────────────────────────

class TestUpload:
    @pytest.mark.anyio
    async def test_upload_xlsx(self, client):
        file_path = os.path.join(TEST_DATA_DIR, "mizan_basit_plain.xlsx")
        with open(file_path, "rb") as f:
            response = await client.post(
                "/api/upload",
                files={"file": ("mizan_basit.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
            )
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert data["total_rows"] == 38
        assert data["statistics"]["total_accounts"] == 38

    @pytest.mark.anyio
    async def test_upload_csv(self, client):
        file_path = os.path.join(TEST_DATA_DIR, "mizan_basit.csv")
        with open(file_path, "rb") as f:
            response = await client.post(
                "/api/upload",
                files={"file": ("mizan_basit.csv", f, "text/csv")},
            )
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert data["total_rows"] == 38

    @pytest.mark.anyio
    async def test_upload_kapsamli(self, client):
        file_path = os.path.join(TEST_DATA_DIR, "mizan_kapsamli_plain.xlsx")
        with open(file_path, "rb") as f:
            response = await client.post(
                "/api/upload",
                files={"file": ("mizan_kapsamli.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
            )
        assert response.status_code == 200
        data = response.json()
        assert data["total_rows"] >= 60

    @pytest.mark.anyio
    async def test_upload_unsupported_format(self, client):
        response = await client.post(
            "/api/upload",
            files={"file": ("test.txt", b"dummy content", "text/plain")},
        )
        assert response.status_code == 400

    @pytest.mark.anyio
    async def test_upload_returns_session(self, client):
        file_path = os.path.join(TEST_DATA_DIR, "mizan_basit_plain.xlsx")
        with open(file_path, "rb") as f:
            response = await client.post(
                "/api/upload",
                files={"file": ("test.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
            )
        data = response.json()
        assert len(data["session_id"]) == 8
        assert "file_name" in data
        assert "column_mapping" in data


# ─── Mapping ─────────────────────────────────────────────────────────────

class TestMapping:
    @pytest.mark.anyio
    async def test_get_mapping(self, client, uploaded_session):
        response = await client.get(f"/api/mapping/{uploaded_session}")
        assert response.status_code == 200
        data = response.json()
        assert "mapped" in data
        assert "unmapped" in data
        assert "summary" in data
        assert "statistics" in data
        assert "ifrs_line_detail" in data

    @pytest.mark.anyio
    async def test_mapping_has_accounts(self, client, uploaded_session):
        response = await client.get(f"/api/mapping/{uploaded_session}")
        data = response.json()
        assert len(data["mapped"]) > 0
        assert data["statistics"]["total_accounts"] == 38

    @pytest.mark.anyio
    async def test_mapping_config_endpoint(self, client):
        response = await client.get("/api/mapping-config")
        assert response.status_code == 200
        data = response.json()
        assert "meta" in data
        assert "accounts" in data

    @pytest.mark.anyio
    async def test_mapping_invalid_session(self, client):
        response = await client.get("/api/mapping/nonexistent")
        assert response.status_code == 404


# ─── Adjustments ─────────────────────────────────────────────────────────

class TestAdjustments:
    @pytest.mark.anyio
    async def test_apply_adjustments(self, client, uploaded_session):
        response = await client.post(f"/api/adjustments/{uploaded_session}")
        assert response.status_code == 200
        data = response.json()
        assert "adjustments" in data
        assert len(data["adjustments"]) == 5
        assert data["applied_count"] >= 1
        assert data["total_entries"] >= 1

    @pytest.mark.anyio
    async def test_apply_with_params(self, client, uploaded_session):
        response = await client.post(
            f"/api/adjustments/{uploaded_session}",
            json={
                "depreciation": {"tdhp_rate": 0.25, "ifrs_rate": 0.08},
                "severance_pay": {"employee_count": 30},
                "deferred_tax": {"tax_rate": 0.22},
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["adjustments"]) == 5

    @pytest.mark.anyio
    async def test_get_adjustments_before_apply(self, client, uploaded_session):
        response = await client.get(f"/api/reports/{uploaded_session}/adjustments")
        assert response.status_code == 200
        data = response.json()
        assert data["adjustments"] == []

    @pytest.mark.anyio
    async def test_get_adjustments_after_apply(self, client, uploaded_session):
        # Once uygula
        await client.post(f"/api/adjustments/{uploaded_session}")
        # Sonra getir
        response = await client.get(f"/api/reports/{uploaded_session}/adjustments")
        assert response.status_code == 200
        data = response.json()
        assert len(data["adjustments"]) == 5

    @pytest.mark.anyio
    async def test_adjustments_invalid_session(self, client):
        response = await client.post("/api/adjustments/nonexistent")
        assert response.status_code == 404


# ─── Reports ─────────────────────────────────────────────────────────────

class TestReports:
    @pytest.mark.anyio
    async def test_balance_sheet(self, client, uploaded_session):
        response = await client.get(f"/api/reports/{uploaded_session}/balance-sheet")
        assert response.status_code == 200
        data = response.json()
        assert data["report_type"] == "balance_sheet"
        assert "sections" in data
        assert "totals" in data
        assert data["totals"]["total_assets"] != 0

    @pytest.mark.anyio
    async def test_balance_sheet_with_adjustments(self, client, uploaded_session):
        await client.post(f"/api/adjustments/{uploaded_session}")
        response = await client.get(f"/api/reports/{uploaded_session}/balance-sheet")
        assert response.status_code == 200
        data = response.json()
        assert "totals" in data

    @pytest.mark.anyio
    async def test_income_statement(self, client, uploaded_session):
        response = await client.get(f"/api/reports/{uploaded_session}/income-statement")
        assert response.status_code == 200
        data = response.json()
        assert data["report_type"] == "income_statement"
        assert "lines" in data
        keys = {line["key"] for line in data["lines"]}
        assert "revenue" in keys
        assert "net_profit" in keys

    @pytest.mark.anyio
    async def test_income_statement_revenue_positive(self, client, uploaded_session):
        response = await client.get(f"/api/reports/{uploaded_session}/income-statement")
        data = response.json()
        revenue = next(l for l in data["lines"] if l["key"] == "revenue")
        assert revenue["amount"] > 0

    @pytest.mark.anyio
    async def test_comparison_requires_adjustments(self, client, uploaded_session):
        """Duzeltme uygulanmadan karsilastirma istemek hata vermeli."""
        response = await client.get(f"/api/reports/{uploaded_session}/comparison")
        assert response.status_code == 400

    @pytest.mark.anyio
    async def test_comparison_after_adjustments(self, client, uploaded_session):
        await client.post(f"/api/adjustments/{uploaded_session}")
        response = await client.get(f"/api/reports/{uploaded_session}/comparison")
        assert response.status_code == 200
        data = response.json()
        assert "balance_sheet" in data
        assert "income_statement" in data
        assert "adjustments_summary" in data
        assert data["total_adjustment_entries"] > 0

    @pytest.mark.anyio
    async def test_reports_invalid_session(self, client):
        response = await client.get("/api/reports/nonexistent/balance-sheet")
        assert response.status_code == 404


# ─── End-to-End Flow ─────────────────────────────────────────────────────

class TestEndToEndFlow:
    @pytest.mark.anyio
    async def test_full_flow(self, client):
        """Tam akis: Upload → Mapping → Adjustments → Reports"""
        # 1. Upload
        file_path = os.path.join(TEST_DATA_DIR, "mizan_basit_plain.xlsx")
        with open(file_path, "rb") as f:
            upload_resp = await client.post(
                "/api/upload",
                files={"file": ("mizan.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
            )
        assert upload_resp.status_code == 200
        session_id = upload_resp.json()["session_id"]

        # 2. Mapping
        mapping_resp = await client.get(f"/api/mapping/{session_id}")
        assert mapping_resp.status_code == 200
        assert len(mapping_resp.json()["mapped"]) > 0

        # 3. Adjustments
        adj_resp = await client.post(f"/api/adjustments/{session_id}")
        assert adj_resp.status_code == 200
        assert adj_resp.json()["applied_count"] >= 1

        # 4. Balance Sheet
        bs_resp = await client.get(f"/api/reports/{session_id}/balance-sheet")
        assert bs_resp.status_code == 200

        # 5. Income Statement
        is_resp = await client.get(f"/api/reports/{session_id}/income-statement")
        assert is_resp.status_code == 200

        # 6. Comparison
        comp_resp = await client.get(f"/api/reports/{session_id}/comparison")
        assert comp_resp.status_code == 200
        assert comp_resp.json()["total_adjustment_entries"] > 0

    @pytest.mark.anyio
    async def test_full_flow_kapsamli(self, client):
        """Kapsamli mizan ile tam akis."""
        file_path = os.path.join(TEST_DATA_DIR, "mizan_kapsamli_plain.xlsx")
        with open(file_path, "rb") as f:
            upload_resp = await client.post(
                "/api/upload",
                files={"file": ("mizan_kapsamli.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
            )
        assert upload_resp.status_code == 200
        session_id = upload_resp.json()["session_id"]
        assert upload_resp.json()["total_rows"] >= 60

        adj_resp = await client.post(f"/api/adjustments/{session_id}")
        assert adj_resp.status_code == 200

        comp_resp = await client.get(f"/api/reports/{session_id}/comparison")
        assert comp_resp.status_code == 200
