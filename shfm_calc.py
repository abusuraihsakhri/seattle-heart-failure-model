"""Original (2006) Seattle Heart Failure Model, using Levy et al. Table 2.

This is a research implementation, not the revised UW web calculator or a
validated clinical decision support device. All required predictors are explicit.
DOI: 10.1161/CIRCULATIONAHA.105.584102
"""
from __future__ import annotations

import math
from typing import Any

BASELINE_HAZARD_PER_YEAR = 0.0405
HAZARD_RATIOS = {
    "age_per_decade": 1.090, "male": 1.089, "nyha_class": 1.600,
    "inverse_ef": 1.030, "ischemic": 1.354,
    "sbp_per_10": 0.877, "loop_diuretic_mg_kg_day": 1.178,
    "allopurinol": 1.571, "sodium_below_138": 1.050,
    "inverse_cholesterol": 2.206, "hemoglobin_below_16": 1.124,
    "hemoglobin_above_16": 1.336, "lymphocyte_pct_per_5": 0.897,
    "uric_acid": 1.064, "ace_inhibitor": 0.77,
    "beta_blocker": 0.66, "arb": 0.85,
    "potassium_sparing_diuretic": 0.74, "statin": 0.63,
    "icd": 0.73, "biv_pacemaker": 1.00, "biv_icd": 0.79,
}
DEVICE_TYPES = ("none", "icd", "biv_pacemaker", "biv_icd")


def _number(label: str, value: float, minimum: float, maximum: float, *, inclusive_min: bool = True) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label} must be a numeric value")
    value = float(value)
    if not math.isfinite(value) or value > maximum or (value < minimum if inclusive_min else value <= minimum):
        op = ">=" if inclusive_min else ">"
        raise ValueError(f"{label} must be finite and {op} {minimum} and <= {maximum}")
    return value


def calculate_shfm_points(
    *, age: float, sex: str, nyha_class: int, ischemic: bool,
    ejection_fraction: float, systolic_bp: float, sodium: float,
    hemoglobin: float, lymphocyte_percent: float, uric_acid: float,
    total_cholesterol: float, weight_kg: float, loop_diuretic_mg_day: float,
    ace_inhibitor: bool = False, arb: bool = False,
    beta_blocker: bool = False, statin: bool = False,
    allopurinol: bool = False, potassium_sparing_diuretic: bool = False,
    device: str = "none",
) -> dict[str, Any]:
    """Return the original-model score and 1/2/3/5-year estimates.

    loop_diuretic_mg_day is oral furosemide-equivalent mg/day, based on the
    original paper's conversion (furosemide 80 = torsemide 40 = bumetanide 3).
    Five-year output extrapolates the original constant hazard model; it is
    *not* the 2013-recalibrated University of Washington five-year estimate.
    """
    age = _number("age", age, 18, 120)
    weight_kg = _number("weight_kg", weight_kg, 0, 500, inclusive_min=False)
    ejection_fraction = _number("ejection_fraction", ejection_fraction, 0, 100, inclusive_min=False)
    systolic_bp = _number("systolic_bp", systolic_bp, 0, 300, inclusive_min=False)
    sodium = _number("sodium", sodium, 0, 200, inclusive_min=False)
    hemoglobin = _number("hemoglobin", hemoglobin, 0, 25, inclusive_min=False)
    lymphocyte_percent = _number("lymphocyte_percent", lymphocyte_percent, 0, 100)
    uric_acid = _number("uric_acid", uric_acid, 0, 30)
    total_cholesterol = _number("total_cholesterol", total_cholesterol, 0, 1000, inclusive_min=False)
    loop_diuretic_mg_day = _number("loop_diuretic_mg_day", loop_diuretic_mg_day, 0, 1000)
    if not isinstance(sex, str) or sex.lower() not in ("male", "female"):
        raise ValueError("sex must be 'male' or 'female'")
    if type(nyha_class) is not int or nyha_class not in (1, 2, 3, 4):
        raise ValueError("nyha_class must be an integer from 1 to 4")
    if device not in DEVICE_TYPES:
        raise ValueError(f"device must be one of: {', '.join(DEVICE_TYPES)}")
    flags = ("ischemic", "ace_inhibitor", "arb", "beta_blocker", "statin",
             "allopurinol", "potassium_sparing_diuretic")
    for name in flags:
        if type(locals()[name]) is not bool:
            raise ValueError(f"{name} must be a boolean")

    contributions = {
        "age": (age / 10) * math.log(HAZARD_RATIOS["age_per_decade"]),
        "male": (sex.lower() == "male") * math.log(HAZARD_RATIOS["male"]),
        "nyha_class": nyha_class * math.log(HAZARD_RATIOS["nyha_class"]),
        "inverse_ef": (100 / ejection_fraction) * math.log(HAZARD_RATIOS["inverse_ef"]),
        "ischemic": ischemic * math.log(HAZARD_RATIOS["ischemic"]),
        "systolic_bp": (min(systolic_bp, 160) / 10) * math.log(HAZARD_RATIOS["sbp_per_10"]),
        "loop_diuretic": (loop_diuretic_mg_day / weight_kg) * math.log(HAZARD_RATIOS["loop_diuretic_mg_kg_day"]),
        "allopurinol": allopurinol * math.log(HAZARD_RATIOS["allopurinol"]),
        "low_sodium": max(138 - sodium, 0) * math.log(HAZARD_RATIOS["sodium_below_138"]),
        "inverse_cholesterol": (100 / total_cholesterol) * math.log(HAZARD_RATIOS["inverse_cholesterol"]),
        "hemoglobin": ((16 - hemoglobin) * math.log(HAZARD_RATIOS["hemoglobin_below_16"])
                       if hemoglobin < 16 else (hemoglobin - 16) * math.log(HAZARD_RATIOS["hemoglobin_above_16"])),
        "lymphocytes": (min(lymphocyte_percent, 47) / 5) * math.log(HAZARD_RATIOS["lymphocyte_pct_per_5"]),
        "uric_acid": max(uric_acid, 3.4) * math.log(HAZARD_RATIOS["uric_acid"]),
        "ace_inhibitor": ace_inhibitor * math.log(HAZARD_RATIOS["ace_inhibitor"]),
        "arb": arb * math.log(HAZARD_RATIOS["arb"]),
        "beta_blocker": beta_blocker * math.log(HAZARD_RATIOS["beta_blocker"]),
        "potassium_sparing_diuretic": potassium_sparing_diuretic * math.log(HAZARD_RATIOS["potassium_sparing_diuretic"]),
        "statin": statin * math.log(HAZARD_RATIOS["statin"]),
        "device": 0.0 if device == "none" else math.log(HAZARD_RATIOS[device]),
    }
    score = sum(contributions.values())
    risk_multiplier = math.exp(min(score, 700))
    survival = {f"{yr}_year": round(math.exp(-BASELINE_HAZARD_PER_YEAR * yr * risk_multiplier), 4)
                for yr in (1, 2, 3, 5)}
    mortality = {key: round(1 - value, 4) for key, value in survival.items()}
    mortality.update({key + "_percent": round(value * 100, 2) for key, value in mortality.items()})
    risk = mortality["1_year"]
    risk_class = ("Low risk" if risk < .05 else "Moderate risk" if risk < .15
                  else "High risk" if risk < .30 else "Very high risk")
    return {
        "total_points": round(score, 4), "point_breakdown": {k: round(v, 6) for k, v in contributions.items()},
        "survival": survival, "mortality": mortality,
        "risk_classification": risk_class,
        "risk_description": "Descriptive mortality band; not a published SHFM classification",
        "model": "Original Levy 2006; constant baseline hazard (not the revised UW web model)",
        "disclaimer": "Research/education only; not independently clinically validated. Do not use for individual treatment decisions.",
        "inputs": {
            "age": age, "sex": sex.lower(), "nyha_class": nyha_class, "ischemic": ischemic,
            "ejection_fraction": ejection_fraction, "systolic_bp": systolic_bp,
            "sodium": sodium, "hemoglobin": hemoglobin,
            "lymphocyte_percent": lymphocyte_percent, "uric_acid": uric_acid,
            "total_cholesterol": total_cholesterol, "weight_kg": weight_kg,
            "loop_diuretic_mg_day": loop_diuretic_mg_day,
            "ace_inhibitor": ace_inhibitor, "arb": arb, "beta_blocker": beta_blocker,
            "statin": statin, "allopurinol": allopurinol,
            "potassium_sparing_diuretic": potassium_sparing_diuretic, "device": device,
        },
    }


def calculate_therapy_benefit(base_result: dict[str, Any], therapy: str, **therapy_params: Any) -> dict[str, Any]:
    """Illustrate coefficient-based scenarios, **not causal treatment benefit**.

    Statins, LVAD, and device upgrades are deliberately not available as
    intervention scenarios; observational associations are not efficacy data.
    """
    if therapy not in ("ace_inhibitor", "arb", "beta_blocker", "potassium_sparing_diuretic"):
        raise ValueError("Unsupported intervention scenario: " + str(therapy))
    inp = dict(base_result["inputs"])
    if therapy_params:
        unexpected = set(therapy_params) - set(inp)
        if unexpected:
            raise ValueError("Unknown parameters: " + ", ".join(sorted(unexpected)))
        inp.update(therapy_params)
    if inp[therapy]:
        raise ValueError(f"{therapy} is already selected")
    inp[therapy] = True
    new_result = calculate_shfm_points(**inp)
    baseline = base_result["mortality"]["1_year_percent"]
    projected = new_result["mortality"]["1_year_percent"]
    absolute = baseline - projected
    return {
        "therapy": therapy,
        "baseline_mortality_1yr": baseline,
        "projected_mortality_1yr": projected,
        "absolute_reduction": round(absolute, 2),
        "relative_reduction_percent": round(absolute / baseline * 100, 1) if baseline else 0.0,
        "interpretation": "Mathematical association only, not a causal estimate or prescribing recommendation",
        "new_result": new_result,
    }
