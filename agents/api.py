"""FastAPI entry point. Browser calculator also runs independently on static hosting."""
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, ConfigDict, Field

from shfm_calc import calculate_shfm_points
from .base import AuditLogger
from .models import SystemTaskPayload
from .supervisor import SystemSupervisor

supervisor = SystemSupervisor(model_provider="mock")
app = FastAPI(title="Seattle Heart Failure Model — Research API", version="3.1.0",
              description="Independent original-2006 educational implementation, not clinical advice.")


class SHFMRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)

    age: float = Field(ge=18, le=120)
    sex: Literal["male", "female"]
    nyha_class: Literal[1, 2, 3, 4]
    ischemic: bool
    ejection_fraction: float = Field(gt=0, le=100)
    systolic_bp: float = Field(gt=0, le=300)
    sodium: float = Field(gt=0, le=200)
    hemoglobin: float = Field(gt=0, le=25)
    lymphocyte_percent: float = Field(ge=0, le=100)
    uric_acid: float = Field(ge=0, le=30)
    total_cholesterol: float = Field(gt=0, le=1000)
    weight_kg: float = Field(gt=0, le=500)
    loop_diuretic_mg_day: float = Field(ge=0, le=1000)
    ace_inhibitor: bool = False
    arb: bool = False
    beta_blocker: bool = False
    statin: bool = False
    allopurinol: bool = False
    potassium_sparing_diuretic: bool = False
    device: Literal["none", "icd", "biv_pacemaker", "biv_icd"] = "none"


class ChatRequest(BaseModel):
    query: str = Field(min_length=1, max_length=1000)


@app.get("/", include_in_schema=False)
def home():
    return FileResponse(Path(__file__).resolve().parent.parent / "web" / "index.html")


@app.get("/calculator.js", include_in_schema=False)
def calculator_js():
    return FileResponse(Path(__file__).resolve().parent.parent / "web" / "calculator.js",
                        media_type="application/javascript")


@app.get("/health")
def health():
    return {"status": "ok", "service": "seattle-heart-failure-model", "model": "original-2006"}


@app.get("/metrics")
def metrics():
    # In-process counts, not a Prometheus-format endpoint.
    return {"dossiers_processed_total": len(supervisor.dossier_registry),
            "audit_blocks_total": len(AuditLogger.get_trail())}


@app.post("/api/calculate")
def api_calculate(payload: SHFMRequest):
    try:
        return calculate_shfm_points(**payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/api/audit")
def api_audit(payload: SystemTaskPayload):
    # This legacy rule demo is unrelated to the SHFM prognosis engine.
    return supervisor.process_task(payload).to_dict()


@app.post("/api/chat")
def api_chat(req: ChatRequest):
    try:
        return {"response": supervisor.query_supervisory_chat(req.query),
                "note": "Deterministic placeholder response, not a medical interpretation."}
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.get("/api/audit/logs")
def api_audit_logs():
    return {"audit_trail": AuditLogger.get_trail(),
            "verified": AuditLogger.verify_integrity(),
            "scope": "Current process memory only; no durable audit storage"}
