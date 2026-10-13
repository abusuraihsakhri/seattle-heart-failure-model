"""API and audit integrity regression coverage."""
from fastapi.testclient import TestClient
from agents.api import app
from agents.base import AuditTrail

PROFILE = {
    "age": 60, "sex": "male", "nyha_class": 2, "ischemic": False,
    "ejection_fraction": 30, "systolic_bp": 120, "sodium": 140,
    "hemoglobin": 14, "lymphocyte_percent": 25, "uric_acid": 6,
    "total_cholesterol": 180, "weight_kg": 80, "loop_diuretic_mg_day": 0,
    "ace_inhibitor": True, "beta_blocker": True
}

def test_api_calculate_reference_and_invalid():
    client = TestClient(app)
    res = client.post("/api/calculate", json=PROFILE)
    assert res.status_code == 200, res.text
    assert res.json()["survival"]["1_year"] == 0.9643
    assert client.post("/api/calculate", json={**PROFILE, "ejection_fraction": 0}).status_code == 422
    assert client.post("/api/calculate", json={**PROFILE, "obsolete_value": 1}).status_code == 422

def test_api_serves_local_ui():
    client = TestClient(app)
    assert "Seattle Heart Failure Model" in client.get("/").text
    assert "0.0405" in client.get("/calculator.js").text

def test_audit_chain_signatures_detect_mutation():
    audit = AuditTrail("strong-test-key")
    audit.log("test", "research", "EVENT", {"case": "SYNTHETIC"})
    assert audit.verify_integrity()
    external = audit.get_trail()
    external[0]["event_type"] = "FORGED"
    assert audit.verify_integrity()  # external modifications cannot mutate the log
    audit.logs[0]["event_type"] = "FORGED"
    assert not audit.verify_integrity()

def test_audit_nested_identifier_rejection():
    client = TestClient(app)
    res = client.post("/api/audit", json={
        "task_id": "TEST-1", "target_identifier": "SPECIMEN-1",
        "primary_metric": 10.0, "attributes": {"note": "Patient MRN-123456"}
    })
    assert res.status_code == 422
    assert "123456" not in res.text
