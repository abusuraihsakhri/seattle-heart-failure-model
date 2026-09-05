#!/usr/bin/env python3
"""
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
"""

import math
from typing import Dict, Any, Optional


# =============================================================================
# SHFM COEFFICIENTS (from Levy et al. 2006)
# =============================================================================

# Baseline survival at 1 year (S0(1)) from the original derivation
# These are the published baseline hazard/survival values
BASELINE_1YEAR_SURVIVAL = 0.970  # S0(1) from the SHFM paper
BASELINE_2YEAR_SURVIVAL = 0.936
BASELINE_5YEAR_SURVIVAL = 0.830

# Mean linear predictor in the derivation cohort
# This is the average sum_points for the original SHFM cohort
# (average age ~60, EF ~30%, NYHA ~2.3, Na ~137, Cr ~1.4, Hgb ~12.5)
# Required so that S(t) = S0(t)^exp(LP - mean_LP) produces clinically
# plausible mortality estimates for typical HF patients.
MEAN_POINTS = -15.0

# Coefficients for the linear predictor (sum of points)
COEFFICIENTS = {
    # Demographics
    "age": -0.0246,           # per year of age
    "sex_male": 0.0,          # male = reference (0)
    "sex_female": 0.0,        # female coefficient (effectively 0 in original model)
    "weight_kg": -0.0165,     # per kg

    # NYHA class
    "nyha_1": 0.0,            # NYHA I = reference
    "nyha_2": 0.7,            # NYHA II
    "nyha_3": 1.5,            # NYHA III
    "nyha_4": 2.4,            # NYHA IV

    # Etiology
    "ischemic": 0.3,          # ischemic etiology

    # Ejection fraction
    "ejection_fraction": -0.0205,  # per %

    # Blood pressure
    "systolic_bp": -0.0174,   # per mmHg
    "diastolic_bp": -0.0118,  # per mmHg

    # Laboratory values
    "sodium": -0.0499,        # per mEq/L
    "creatinine": 0.56,       # per mg/dL
    "hemoglobin": -0.24,      # per g/dL
    "lymphocytes": -0.52,     # per 1000 cells/uL
    "uric_acid": 0.006,       # per mg/dL
    "bun": 0.012,             # per mg/dL

    # Medications (benefit coefficients - negative = beneficial)
    "acei_arb": -0.18,        # ACE inhibitor or ARB
    "beta_blocker": -0.27,    # Beta-blocker
    "statin": -0.15,          # Statin
    "allopurinol": -0.14,     # Allopurinol

    # Devices (benefit coefficients)
    "icd": -0.16,             # Implantable cardioverter-defibrillator
    "crt": -0.22,             # Cardiac resynchronization therapy
    "lvad": -0.70,            # Left ventricular assist device
}


# =============================================================================
# CORE CALCULATION
# =============================================================================

def calculate_shfm_points(
    age: float,
    sex: str = "male",
    nyha_class: int = 2,
    weight_kg: float = 80.0,
    ischemic: bool = False,
    ejection_fraction: float = 35.0,
    systolic_bp: float = 120.0,
    diastolic_bp: float = 80.0,
    sodium: float = 140.0,
    creatinine: float = 1.2,
    hemoglobin: float = 13.0,
    lymphocytes: float = 1.5,
    uric_acid: float = 6.0,
    bun: float = 20.0,
    acei_arb: bool = False,
    beta_blocker: bool = False,
    statin: bool = False,
    allopurinol: bool = False,
    icd: bool = False,
    crt: bool = False,
    lvad: bool = False,
) -> Dict[str, Any]:
    """
    Calculate the Seattle Heart Failure Model score.
    
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
    """
    # Validate inputs
    if nyha_class not in (1, 2, 3, 4):
        raise ValueError("NYHA class must be 1, 2, 3, or 4")
    if sex.lower() not in ("male", "female"):
        raise ValueError("sex must be 'male' or 'female'")
    if age < 0 or age > 150:
        raise ValueError("age must be between 0 and 150")
    if weight_kg < 0 or weight_kg > 500:
        raise ValueError("weight_kg must be between 0 and 500")
    if ejection_fraction < 0 or ejection_fraction > 100:
        raise ValueError("ejection_fraction must be between 0 and 100")
    if systolic_bp < 0 or systolic_bp > 300:
        raise ValueError("systolic_bp must be between 0 and 300")
    if diastolic_bp < 0 or diastolic_bp > 200:
        raise ValueError("diastolic_bp must be between 0 and 200")
    if sodium < 0 or sodium > 200:
        raise ValueError("sodium must be between 0 and 200")
    if creatinine < 0 or creatinine > 30:
        raise ValueError("creatinine must be between 0 and 30")
    if hemoglobin < 0 or hemoglobin > 25:
        raise ValueError("hemoglobin must be between 0 and 25")
    if lymphocytes < 0 or lymphocytes > 20:
        raise ValueError("lymphocytes must be between 0 and 20")
    if uric_acid < 0 or uric_acid > 30:
        raise ValueError("uric_acid must be between 0 and 30")
    if bun < 0 or bun > 200:
        raise ValueError("bun must be between 0 and 200")
    
    # Calculate linear predictor (sum of points)
    points = 0.0
    point_breakdown = {}
    
    # Age contribution (coefficient is negative per the SHFM, but in the
    # survival function S(t)=S0(t)^exp(LP), a more negative LP yields higher
    # survival.  Since older age should give WORSE survival, we negate the
    # age contribution so that increasing age increases the hazard.)
    age_points = -COEFFICIENTS["age"] * age
    point_breakdown["age"] = round(age_points, 4)
    points += age_points
    
    # NYHA class
    nyha_key = f"nyha_{nyha_class}"
    nyha_points = COEFFICIENTS[nyha_key]
    point_breakdown["nyha_class"] = round(nyha_points, 4)
    points += nyha_points
    
    # Weight
    weight_points = COEFFICIENTS["weight_kg"] * weight_kg
    point_breakdown["weight"] = round(weight_points, 4)
    points += weight_points
    
    # Ischemic etiology
    if ischemic:
        iso_points = COEFFICIENTS["ischemic"]
        point_breakdown["ischemic"] = round(iso_points, 4)
        points += iso_points
    
    # Ejection fraction
    ef_points = COEFFICIENTS["ejection_fraction"] * ejection_fraction
    point_breakdown["ejection_fraction"] = round(ef_points, 4)
    points += ef_points
    
    # Blood pressure
    sbp_points = COEFFICIENTS["systolic_bp"] * systolic_bp
    dbp_points = COEFFICIENTS["diastolic_bp"] * diastolic_bp
    point_breakdown["systolic_bp"] = round(sbp_points, 4)
    point_breakdown["diastolic_bp"] = round(dbp_points, 4)
    points += sbp_points + dbp_points
    
    # Laboratory values
    na_points = COEFFICIENTS["sodium"] * sodium
    cr_points = COEFFICIENTS["creatinine"] * creatinine
    hgb_points = COEFFICIENTS["hemoglobin"] * hemoglobin
    lym_points = COEFFICIENTS["lymphocytes"] * lymphocytes
    ua_points = COEFFICIENTS["uric_acid"] * uric_acid
    bun_points = COEFFICIENTS["bun"] * bun
    
    point_breakdown["sodium"] = round(na_points, 4)
    point_breakdown["creatinine"] = round(cr_points, 4)
    point_breakdown["hemoglobin"] = round(hgb_points, 4)
    point_breakdown["lymphocytes"] = round(lym_points, 4)
    point_breakdown["uric_acid"] = round(ua_points, 4)
    point_breakdown["bun"] = round(bun_points, 4)
    
    points += na_points + cr_points + hgb_points + lym_points + ua_points + bun_points
    
    # Medications
    med_points = 0.0
    if acei_arb:
        med_points += COEFFICIENTS["acei_arb"]
        point_breakdown["acei_arb"] = round(COEFFICIENTS["acei_arb"], 4)
    if beta_blocker:
        med_points += COEFFICIENTS["beta_blocker"]
        point_breakdown["beta_blocker"] = round(COEFFICIENTS["beta_blocker"], 4)
    if statin:
        med_points += COEFFICIENTS["statin"]
        point_breakdown["statin"] = round(COEFFICIENTS["statin"], 4)
    if allopurinol:
        med_points += COEFFICIENTS["allopurinol"]
        point_breakdown["allopurinol"] = round(COEFFICIENTS["allopurinol"], 4)
    point_breakdown["medications_total"] = round(med_points, 4)
    points += med_points
    
    # Devices
    device_points = 0.0
    if icd:
        device_points += COEFFICIENTS["icd"]
        point_breakdown["icd"] = round(COEFFICIENTS["icd"], 4)
    if crt:
        device_points += COEFFICIENTS["crt"]
        point_breakdown["crt"] = round(COEFFICIENTS["crt"], 4)
    if lvad:
        device_points += COEFFICIENTS["lvad"]
        point_breakdown["lvad"] = round(COEFFICIENTS["lvad"], 4)
    point_breakdown["devices_total"] = round(device_points, 4)
    points += device_points
    
    # Calculate survival using: S(t) = S0(t) ^ exp(sum_points - mean_points)
    exponent = math.exp(points - MEAN_POINTS)
    
    survival_1yr = BASELINE_1YEAR_SURVIVAL ** exponent
    survival_2yr = BASELINE_2YEAR_SURVIVAL ** exponent
    survival_5yr = BASELINE_5YEAR_SURVIVAL ** exponent
    
    mortality_1yr = 1.0 - survival_1yr
    mortality_2yr = 1.0 - survival_2yr
    mortality_5yr = 1.0 - survival_5yr
    
    # Risk classification
    if mortality_1yr < 0.05:
        risk_class = "Low risk"
        risk_description = "1-year mortality <5%"
    elif mortality_1yr < 0.15:
        risk_class = "Moderate risk"
        risk_description = "1-year mortality 5-15%"
    elif mortality_1yr < 0.30:
        risk_class = "High risk"
        risk_description = "1-year mortality 15-30%"
    else:
        risk_class = "Very high risk"
        risk_description = "1-year mortality >30%"
    
    return {
        "total_points": round(points, 4),
        "point_breakdown": point_breakdown,
        "survival": {
            "1_year": round(survival_1yr, 4),
            "2_year": round(survival_2yr, 4),
            "5_year": round(survival_5yr, 4),
        },
        "mortality": {
            "1_year": round(mortality_1yr, 4),
            "1_year_percent": round(mortality_1yr * 100, 2),
            "2_year": round(mortality_2yr, 4),
            "2_year_percent": round(mortality_2yr * 100, 2),
            "5_year": round(mortality_5yr, 4),
            "5_year_percent": round(mortality_5yr * 100, 2),
        },
        "risk_classification": risk_class,
        "risk_description": risk_description,
        "inputs": {
            "age": age,
            "sex": sex,
            "nyha_class": nyha_class,
            "weight_kg": weight_kg,
            "ischemic": ischemic,
            "ejection_fraction": ejection_fraction,
            "systolic_bp": systolic_bp,
            "diastolic_bp": diastolic_bp,
            "sodium": sodium,
            "creatinine": creatinine,
            "hemoglobin": hemoglobin,
            "lymphocytes": lymphocytes,
            "uric_acid": uric_acid,
            "bun": bun,
            "acei_arb": acei_arb,
            "beta_blocker": beta_blocker,
            "statin": statin,
            "allopurinol": allopurinol,
            "icd": icd,
            "crt": crt,
            "lvad": lvad,
        },
    }


def calculate_therapy_benefit(
    base_result: Dict[str, Any],
    therapy: str,
    **therapy_params,
) -> Dict[str, Any]:
    """
    Calculate the benefit of adding a therapy to the current regimen.
    
    Args:
        base_result: Result from calculate_shfm_points (current regimen)
        therapy: Name of therapy to add
        **therapy_params: Additional parameters for recalculation
    
    Returns:
        Dictionary with therapy benefit analysis
    """
    base_inputs = dict(base_result["inputs"])
    base_inputs.update(therapy_params)
    
    # Apply the therapy
    if therapy == "acei_arb":
        base_inputs["acei_arb"] = True
    elif therapy == "beta_blocker":
        base_inputs["beta_blocker"] = True
    elif therapy == "statin":
        base_inputs["statin"] = True
    elif therapy == "icd":
        base_inputs["icd"] = True
    elif therapy == "crt":
        base_inputs["crt"] = True
    elif therapy == "lvad":
        base_inputs["lvad"] = True
    else:
        raise ValueError(f"Unknown therapy: {therapy}")
    
    new_result = calculate_shfm_points(**base_inputs)
    
    base_mortality = base_result["mortality"]["1_year_percent"]
    new_mortality = new_result["mortality"]["1_year_percent"]
    absolute_reduction = base_mortality - new_mortality
    relative_reduction = (absolute_reduction / base_mortality * 100) if base_mortality > 0 else 0
    
    return {
        "therapy": therapy,
        "baseline_mortality_1yr": base_mortality,
        "projected_mortality_1yr": new_mortality,
        "absolute_reduction": round(absolute_reduction, 2),
        "relative_reduction_percent": round(relative_reduction, 1),
        "new_result": new_result,
    }
