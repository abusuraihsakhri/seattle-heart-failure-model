# Seattle Heart Failure Model

> **Domain:** Clinical Decision Support & Biomedical Computing  
> **Reference Guidelines & Standards:** `Standard Clinical Formulations & ISO/IEC Quality Frameworks`

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## 📖 What It Does

Seattle Heart Failure Model (SHFM) Calculator

Predicts 1-year mortality in chronic heart failure patients.
The SHFM uses a multivariate Cox proportional hazards model to estimate
survival based on clinical, laboratory, medication, and device variables.

References:
- Levy WC, Mozaffarian D, Linker DT, et al. The Seattle Heart Failure Model:
  Prediction of Survival Without and with Therapies. Circulation. 2006;114(16):1659-1666.
- Mozaffarian D, Anker SD, Anand I, et al. Prediction of mode of death in heart
  failure: the Seattle Heart Failure Model. Circulation. 2007;116(4):392-398.

Author: Medical Calculator Project
License: MIT

---

## ⚙️ Key Capabilities & Algorithmic Modules

### 🔬 Analytical Functions

- **`calculate_shfm_points()`**: Calculate the Seattle Heart Failure Model score.

The SHFM linear predictor (sum_points) is calculated as:
sum = beta_age * age + beta_nyha * nyha + beta_ef * ef + ...

Survival is then: S(t) = S0(t) ^ exp(sum_points - mean_points)
1-year mortality = 1 - S(1)

Args:
    age: Age in years
    sex: "male" or "female"
    nyha_class: NYHA functional class (1-4)
    weight_kg: Body weight in kg
    ischemic: Ischemic etiology
    ejection_fraction: LVEF in %
    systolic_bp: Systolic BP in mmHg
    diastolic_bp: Diastolic BP in mmHg
    sodium: Serum sodium in mEq/L
    creatinine: Serum creatinine in mg/dL
    hemoglobin: Hemoglobin in g/dL
    lymphocytes: Lymphocyte count in 1000 cells/uL
    uric_acid: Uric acid in mg/dL
    bun: Blood urea nitrogen in mg/dL
    acei_arb: On ACE inhibitor or ARB
    beta_blocker: On beta-blocker
    statin: On statin
    allopurinol: On allopurinol
    icd: Has ICD
    crt: Has CRT (CRT-D or CRT-P)
    lvad: Has LVAD

Returns:
    Dictionary with SHFM results
- **`calculate_therapy_benefit()`**: Calculate the benefit of adding a therapy to the current regimen.

Args:
    base_result: Result from calculate_shfm_points (current regimen)
    therapy: Name of therapy to add
    **therapy_params: Additional parameters for recalculation

Returns:
    Dictionary with therapy benefit analysis

---

## 📐 Mathematical Formulation & Logic

```text
  Calculate the Seattle Heart Failure Model score.
  The SHFM linear predictor (sum_points) is calculated as:
  Calculate linear predictor (sum of points)
  Calculate survival using: S(t) = S0(t) ^ exp(sum_points - mean_points)
  Calculate the benefit of adding a therapy to the current regimen.
```

---

## 💻 CLI Quickstart & Usage

### 1. Guided Interactive Mode
```bash
python cli.py
```

### 2. Direct Parameterized Evaluation
```bash
python cli.py --json <value> --age <value> --sex <value> --nyha <value>
```

### Parameter Reference
- `--json`: Specifies input measurement or parameter value.
- `--age`: Specifies input measurement or parameter value.
- `--sex`: Specifies input measurement or parameter value.
- `--nyha`: Specifies input measurement or parameter value.
- `--weight`: Specifies input measurement or parameter value.
- `--ischemic`: Specifies input measurement or parameter value.
- `--ef`: Specifies input measurement or parameter value.
- `--sbp`: Specifies input measurement or parameter value.
- `--dbp`: Specifies input measurement or parameter value.
- `--sodium`: Specifies input measurement or parameter value.

### Input Data Schema

| Field | Description | Requirement |
|:------|:------------|:------------|
| `Patient_ID` | Parameter / observation metric | Required |
| `v1` | Parameter / observation metric | Required |
| `v2` | Parameter / observation metric | Required |
| `v3` | Parameter / observation metric | Required |

---

## 🛡️ Security & Enterprise Architecture

* **Zero-PHI Outbound Interceptor:** Active AST and regex inspection blocking SSNs, MRNs, phone numbers, and patient identifiers.
* **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs for every evaluation and state transition.
* **Air-Gapped LLM Reasoning Adapter:** Agnostic integration for local Ollama instances (`llama3`, `mistral`), Claude 3.5 Sonnet, GPT-4o, and deterministic test mocks.
* **Active Learning Bayesian Calibration:** Dynamic tracker updating worker reliability weights and monitoring Brier calibration drift.
* **FastAPI & Prometheus Telemetry:** Exposes OpenAPI 3.1 REST endpoints and operational Prometheus metrics (`/metrics`).

---

## 🧪 Testing & Verification

Run the automated test suite:

```bash
pytest -v
```

Execute high-throughput batch simulation benchmarks:

```bash
python simulator.py --tasks 1000 --concurrency 8
```

---

## 🐳 Container Deployment

```bash
docker build -t seattle-heart-failure-model .
docker run -p 8000:8000 seattle-heart-failure-model
```
