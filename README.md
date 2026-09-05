# Seattle Heart Failure Model

> **Domain:** Clinical Decision Support & Biomedical Computing
> **Reference Guidelines & Standards:** Standard Clinical Formulations & ISO/IEC Quality Frameworks

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
    age: Age in years (0-150)
    sex: "male" or "female"
    nyha_class: NYHA functional class (1-4)
    weight_kg: Body weight in kg (0-500)
    ischemic: Ischemic etiology
    ejection_fraction: LVEF in % (0-100)
    systolic_bp: Systolic BP in mmHg (0-300)
    diastolic_bp: Diastolic BP in mmHg (0-200)
    sodium: Serum sodium in mEq/L (0-200)
    creatinine: Serum creatinine in mg/dL (0-30)
    hemoglobin: Hemoglobin in g/dL (0-25)
    lymphocytes: Lymphocyte count in 1000 cells/uL (0-20)
    uric_acid: Uric acid in mg/dL (0-30)
    bun: Blood urea nitrogen in mg/dL (0-200)
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

## 💻 Installation

```bash
# Clone the repository
git clone https://github.com/abusuraihsakhri/seattle-heart-failure-model.git
cd seattle-heart-failure-model

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"
```

---

## 💻 CLI Quickstart & Usage

### 1. Calculate SHFM Score
```bash
python cli.py calculate --age 65 --ef 35 --nyha 2
```

### 2. Calculate with Medications
```bash
python cli.py calculate --age 65 --ef 25 --nyha 3 --acei-arb --beta-blocker --statin
```

### 3. Therapy Benefit Analysis
```bash
python cli.py therapy --therapy beta_blocker --age 65 --ef 25 --nyha 3
```

### 4. Enterprise Audit Operations
```bash
# Run audit task evaluation
python cli.py audit --task-id TASK-001

# Query supervisory chat
python cli.py chat "Explain heart failure risk"

# Verify HMAC audit trail integrity
python cli.py verify-audit
```

### 5. JSON Output
```bash
python cli.py --json calculate --age 65 --ef 35 --nyha 2
```

### Parameter Reference
- `--json`: Also output JSON result
- `--age`: Age in years (0-150)
- `--sex`: "male" or "female"
- `--nyha`: NYHA functional class (1-4)
- `--weight`: Weight in kg (0-500)
- `--ischemic`: Ischemic etiology flag
- `--ef`: Ejection fraction % (0-100)
- `--sbp`: Systolic BP mmHg (0-300)
- `--dbp`: Diastolic BP mmHg (0-200)
- `--sodium`: Serum sodium mEq/L (0-200)
- `--creatinine`: Creatinine mg/dL (0-30)
- `--hemoglobin`: Hemoglobin g/dL (0-25)
- `--lymphocytes`: Lymphocytes (1000/uL) (0-20)
- `--uric-acid`: Uric acid mg/dL (0-30)
- `--bun`: BUN mg/dL (0-200)
- `--acei-arb`: On ACEi/ARB
- `--beta-blocker`: On beta-blocker
- `--statin`: On statin
- `--allopurinol`: On allopurinol
- `--icd`: Has ICD
- `--crt`: Has CRT
- `--lvad`: Has LVAD

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

### Docker
```bash
docker build -t seattle-heart-failure-model .
docker run -p 8000:8000 -e AUDIT_SECRET_KEY=your-secret-key seattle-heart-failure-model
```

### Docker Compose
```bash
# Copy environment template
cp .env.example .env
# Edit .env to set AUDIT_SECRET_KEY

docker-compose up -d
```

---

## 📁 Project Structure

```
seattle-heart-failure-model/
├── shfm_calc.py          # Core SHFM calculation engine
├── cli.py                # Command-line interface
├── simulator.py          # High-throughput stress testing simulator
├── enrichment.py         # Enrichment feature engines
├── pyproject.toml        # Python project configuration
├── Dockerfile            # Container build configuration
├── docker-compose.yml    # Multi-container orchestration
├── agents/               # Enterprise agent framework
│   ├── __init__.py
│   ├── base.py           # PHI guard, HMAC audit trail
│   ├── models.py         # Pydantic data models
│   ├── supervisor.py     # Multi-agent orchestrator
│   ├── workers.py        # Specialized domain workers
│   ├── llm_factory.py    # LLM provider factory
│   ├── api.py            # FastAPI REST endpoints
│   ├── learning.py       # Bayesian calibration engine
│   ├── metrics.py        # Prometheus metrics exporter
│   └── streamer.py       # WebSocket telemetry broadcaster
├── tests/                # Test suite
│   ├── test_enrichment.py
│   └── test_seattle_heart_failure_model.py
├── test_shfm_calc.py     # Core calculation tests
├── web/                  # Web operations console
│   └── index.html
├── openapi_spec.json     # OpenAPI 3.1 specification
├── sample.csv            # Sample patient data
├── benchmark_dataset.json # Golden benchmark test suite
└── .env.example          # Environment variable template
```
