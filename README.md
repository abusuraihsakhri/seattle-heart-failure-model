# Seattle Heart Failure Model (SHFM)

> **Cardiology - Heart Failure**  
> Reference: Levy WC et al. Circulation. 2006;114(16):1659-1666

![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB.svg)

---

## Overview

A real implementation of the Seattle Heart Failure Model, which predicts 1-year, 2-year, and 5-year mortality in chronic heart failure patients.

**Inputs include:**
- Demographics: age, sex, weight
- Clinical: NYHA class, ischemic etiology, ejection fraction, blood pressure
- Laboratory: sodium, creatinine, hemoglobin, lymphocytes, uric acid, BUN
- Medications: ACEi/ARB, beta-blocker, statin, allopurinol
- Devices: ICD, CRT, LVAD

**Survival function:** S(t) = S₀(t)^exp(sum_points - mean_points)

**No external dependencies** - uses only Python standard library.

---

## Quick Start

```bash
# Calculate SHFM for a typical HF patient
python cli.py calculate --age 65 --sex male --nyha 3 --ef 25 --sbp 110 --sodium 135 --creatinine 1.5 --hemoglobin 11.5 --ischemic --acei-arb --beta-blocker

# Calculate with devices
python cli.py calculate --age 70 --ef 20 --nyha 3 --icd --crt --acei-arb --beta-blocker --statin

# Evaluate therapy benefit
python cli.py therapy --therapy beta_blocker --age 65 --ef 25 --nyha 3
```

---

## Python API

```python
from shfm_calc import calculate_shfm_points, calculate_therapy_benefit

# Basic calculation
result = calculate_shfm_points(
    age=65, sex="male", nyha_class=3, ejection_fraction=25,
    systolic_bp=110, sodium=135, creatinine=1.5, hemoglobin=11.5,
    ischemic=True, acei_arb=True, beta_blocker=True,
)
print(f"1-year mortality: {result['mortality']['1_year_percent']:.1f}%")
print(f"Risk: {result['risk_classification']}")

# Therapy benefit
benefit = calculate_therapy_benefit(result, "icd")
print(f"ICD benefit: {benefit['absolute_reduction']:.1f}% absolute reduction")
```

---

## Clinical Reference

### SHFM Coefficients
| Variable | Coefficient | Direction |
|----------|------------|-----------|
| Age (per year) | -0.0246 | Worse with age |
| NYHA II | +0.7 | vs NYHA I |
| NYHA III | +1.5 | vs NYHA I |
| NYHA IV | +2.4 | vs NYHA I |
| EF (per %) | -0.0205 | Better with higher EF |
| Sodium (per mEq/L) | -0.0499 | Better with higher Na |
| Creatinine (per mg/dL) | +0.56 | Worse with higher Cr |
| ACEi/ARB | -0.18 | Beneficial |
| Beta-blocker | -0.27 | Beneficial |
| ICD | -0.16 | Beneficial |
| CRT | -0.22 | Beneficial |
| LVAD | -0.70 | Beneficial |

### Risk Classification
| 1-Year Mortality | Risk Level |
|-----------------|------------|
| <5% | Low risk |
| 5-15% | Moderate risk |
| 15-30% | High risk |
| >30% | Very high risk |

---

## Disclaimer

This tool is for **educational and clinical decision support purposes only**. It does not replace professional medical judgment. Always correlate with clinical context.

## License

MIT License. See [LICENSE](LICENSE) for details.
