import io
import pytest
from PIL import Image
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_root_endpoint():
    res = client.get("/")
    assert res.status_code == 200
    data = res.json()
    assert data["project"] == "MARINE-SHIELD"


def test_health_endpoint():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] in ["healthy", "degraded"]
    assert "components" in data


def test_analyze_endpoint_valid_image():
    img = Image.new("RGB", (256, 256), color=(200, 220, 240))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)

    files = {"file": ("test_marine.jpg", buf, "image/jpeg")}
    res = client.post("/api/analyze", files=files)
    assert res.status_code == 200
    data = res.json()
    assert "analysis_id" in data
    assert "prediction" in data
    assert "confidence" in data
    assert "severity" in data
    assert "severity_score" in data
    assert "severity_reason" in data
    assert "analysis_status" in data


def test_analyze_endpoint_corrupted_image():
    corrupted_data = io.BytesIO(b"NOT_A_VALID_IMAGE_BYTES")
    files = {"file": ("corrupt.jpg", corrupted_data, "image/jpeg")}
    res = client.post("/api/analyze", files=files)
    assert res.status_code == 400


def test_ask_endpoint():
    payload = {"question": "What personal protective equipment is required for coastal cleanup?"}
    res = client.post("/api/ask", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "answer" in data
    assert "sources" in data
    assert len(data["sources"]) > 0


def test_evaluation_endpoint():
    res = client.get("/api/evaluation")
    assert res.status_code == 200
    data = res.json()
    assert "is_trained" in data
    assert "class_labels" in data


def test_knowledge_endpoint():
    res = client.get("/api/knowledge")
    assert res.status_code == 200
    data = res.json()
    assert data["total_documents"] >= 6
    assert data["total_chunks"] >= 20


def test_reports_crud_endpoints():
    # First create an analysis
    img = Image.new("RGB", (200, 200), color=(180, 200, 220))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)
    files = {"file": ("test_rep.jpg", buf, "image/jpeg")}
    an_res = client.post("/api/analyze", files=files)
    assert an_res.status_code == 200
    aid = an_res.json()["analysis_id"]

    # Generate Report
    rep_res = client.post("/api/reports", json={"analysis_id": aid})
    assert rep_res.status_code == 201
    rep_data = rep_res.json()
    assert "report_id" in rep_data
    rid = rep_data["report_id"]

    # List Reports
    list_res = client.get("/api/reports")
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1

    # Download Report
    dl_res = client.get(f"/api/reports/{rid}/download")
    assert dl_res.status_code == 200
    assert dl_res.headers["content-type"] == "application/pdf"
