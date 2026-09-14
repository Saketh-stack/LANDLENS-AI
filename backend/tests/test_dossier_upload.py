import io
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_dossier_upload_empty():
    res = client.post("/api/officer/dossier-upload")
    assert res.status_code == 400
    msg = res.json().get("error") or res.json().get("detail", "")
    assert "provide at least one" in msg

def test_dossier_upload_multi_docs():
    deed_content = b"Registered Sale Deed. Survey No: 101/2B. Buyer: Ramesh Kumar. Seller: Suresh Singh. Area: 2.40 Acres. District: Bhopal. Village: Rampur."
    khasra_content = b"Khasra Register. Khasra No: 101/2B. Owner: Ramesh Kumar. Total Area: 2.40 Acres. Village: Rampur."
    
    files = {
        "sale_deed": ("sale_deed.txt", io.BytesIO(deed_content), "text/plain"),
        "khasra": ("khasra.txt", io.BytesIO(khasra_content), "text/plain")
    }
    data = {"language": "English"}
    
    res = client.post("/api/officer/dossier-upload", files=files, data=data)
    assert res.status_code == 200
    json_data = res.json()
    assert json_data["documents_analyzed_count"] == 2
    assert "comparison_matrix" in json_data
    assert "overall_status" in json_data
    assert len(json_data["records"]) == 2
