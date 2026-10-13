# Seattle Heart Failure Model

Independent, educational implementation of the **original 2006 Seattle Heart Failure Model (SHFM)** survival equation. Includes a local browser calculator, Python library, CLI, and FastAPI endpoint. This is **not** the official or later-recalibrated University of Washington calculator.

> **Clinical limitation:** Research and education only. This implementation has not undergone independent clinical validation, regulatory review, or external calibration. Do not use it for patient-care or treatment decisions. Only enter de-identified or synthetic data.

## Use in the browser

Open `web/index.html` in a modern browser, or serve the `web/` directory as a static site. The calculator runs entirely in JavaScript, without an API, cookies, or persistence. No clinical input is sent over the network by the calculator. A GitHub Pages deployment workflow is provided; availability of a public live URL must be verified independently.

Choose **Load synthetic example** to reproduce the reference scenario (score approximately −0.1089; one-year survival approximately 96.43%). All required numerical predictors must otherwise be supplied explicitly. Results include 1-, 2-, 3-, and 5-year survival.

## Python installation

Requires Python 3.10 or later.

```bash
git clone https://github.com/abusuraihsakhri/seattle-heart-failure-model.git
cd seattle-heart-failure-model
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
python -m pytest -q
node --test tests/test_browser_model.cjs
```

Run the API and local web frontend:

```bash
uvicorn agents.api:app --reload
# Open http://127.0.0.1:8000/
# Interactive documentation: http://127.0.0.1:8000/docs
```

Start a standalone static server instead:

```bash
python -m http.server 8080 --directory web
# Open http://127.0.0.1:8080/
```

For the CLI, run `python cli.py calculate --help`. Unlike earlier versions, the original SHFM predictors are **required** rather than silently imputed. Example:

```bash
python cli.py calculate \
  --age 60 --sex male --nyha 2 --ef 30 --sbp 120 \
  --sodium 140 --hemoglobin 14 --lymphocyte-percent 25 \
  --uric-acid 6 --total-cholesterol 180 --weight 80 \
  --loop-diuretic-mg-day 0 --ace-inhibitor --beta-blocker
```

The installed `shfm` command accepts the same options. For the REST API, send the equivalent JSON predictor fields to `POST /api/calculate`. The schema is available in FastAPI's generated `/openapi.json`.

## Calculation and scope

The original SHFM Cox score is the sum of published log-hazard-ratio contributions, with estimated survival at time `t` years:

```text
SHFM score = sum[ln(hazard ratio) × covariate]
S(t) = exp[-0.0405 × t × exp(SHFM score)]
```

The implementation includes age, sex, NYHA, systolic pressure, LVEF, ischemic etiology, loop-diuretic dose per kg, laboratory predictors (sodium, cholesterol, hemoglobin, **lymphocyte percentage**, uric acid), and medication/device associations from the original model. Required diuretic input is oral **furosemide-equivalent mg/day**; divide by the entered weight in kg to obtain the model covariate. Furosemide 80 mg, torsemide 40 mg, and bumetanide 3 mg are the original source's approximate dose equivalences.

The original model truncates systolic blood pressure above 160 mmHg and lymphocyte percentage above 47%; sodium contributes only below 138 mEq/L. The 5-year result is **extrapolated** from the original constant-hazard equation and is **not** the revised University of Washington 5-year estimate. The displayed low/moderate/high/very-high categories are informal mortality bands, not published validated SHFM strata.

The original observational coefficients **must not** be interpreted as causal treatment efficacy. CLI therapy comparisons are mathematical scenarios, not recommendations. Statin or LVAD scenarios are deliberately excluded; the University of Washington later revised its treatment and device assumptions. The patient selection and calibration of the original study do not necessarily generalize to contemporary care, HFpEF, hospitalized patients, or different populations.

Reference: Levy WC, Mozaffarian D, Linker DT, et al. The Seattle Heart Failure Model: prediction of survival in heart failure. *Circulation*. 2006;113(11):1424–1433. [doi:10.1161/CIRCULATIONAHA.105.584102](https://doi.org/10.1161/CIRCULATIONAHA.105.584102). See also the [University of Washington model update notes](https://depts.washington.edu/shfm/update.php).

## Other repository components

The `agents/` folder retains an independent, **generic rule-based demonstration** with `audit`, `chat`, and `verify-audit` CLI commands and their corresponding API endpoints. It does not constitute a clinically validated multi-agent SHFM inference engine. Chat responses are deterministic placeholders, not real LLM outputs.

The audit demonstration signs each record with HMAC-SHA256 and verifies its chain within the current process. It is **in-memory only**; restarting discards records. When no `AUDIT_SECRET_KEY` is supplied, a fresh random per-process key is generated. Its pattern-based identifier screening is incomplete and **must not** be described as HIPAA de-identification or PHI-safe clinical storage. Do not submit identifiable data to API or demonstration endpoints.

## Docker and testing

```bash
docker build -t seattle-heart-failure-model .
docker run --rm -p 8000:8000 seattle-heart-failure-model
```

`docker compose up --build` is also supported. The application serves the UI at `/`, JSON API at `/api/calculate`, and health endpoint at `/health`. GitHub Actions runs Python tests across 3.10–3.12 and Node browser-math tests. The static application requires only JavaScript and works in current Chrome, Firefox, Edge, and Safari; browser compatibility has not been formally certified.

## License

[MIT](LICENSE).
