#!/usr/bin/env python3
"""
Tests for Seattle Heart Failure Model Calculator.
"""
import math
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from shfm_calc import calculate_shfm_points, calculate_therapy_benefit, COEFFICIENTS


# =============================================================================
# Basic Calculation Tests
# =============================================================================

def test_shfm_returns_required_keys():
    """Result must contain all required keys."""
    result = calculate_shfm_points(age=65, ejection_fraction=35)
    assert "total_points" in result
    assert "survival" in result
    assert "mortality" in result
    assert "risk_classification" in result
    assert "point_breakdown" in result


def test_shfm_survival_range():
    """Survival must be between 0 and 1."""
    result = calculate_shfm_points(age=65, ejection_fraction=35)
    for key in ("1_year", "2_year", "5_year"):
        assert 0 <= result["survival"][key] <= 1


def test_shfm_mortality_range():
    """Mortality must be between 0 and 100%."""
    result = calculate_shfm_points(age=65, ejection_fraction=35)
    for key in ("1_year_percent", "2_year_percent", "5_year_percent"):
        assert 0 <= result["mortality"][key] <= 100


def test_shfm_survival_plus_mortality_equals_one():
    """Survival + mortality = 1."""
    result = calculate_shfm_points(age=65, ejection_fraction=35)
    for yr in ("1_year", "2_year", "5_year"):
        assert abs(result["survival"][yr] + result["mortality"][yr] - 1.0) < 0.001


# =============================================================================
# Age Effect Tests
# =============================================================================

def test_older_age_higher_mortality():
    """Older patients should have higher mortality."""
    young = calculate_shfm_points(age=40, ejection_fraction=35)
    old = calculate_shfm_points(age=80, ejection_fraction=35)
    assert old["mortality"]["1_year_percent"] > young["mortality"]["1_year_percent"]


def test_age_coefficient():
    """Age coefficient should be negative (more points = worse)."""
    assert COEFFICIENTS["age"] < 0


# =============================================================================
# NYHA Class Tests
# =============================================================================

def test_nyha_worse_with_higher_class():
    """Higher NYHA class -> higher mortality."""
    nyha1 = calculate_shfm_points(age=65, ejection_fraction=35, nyha_class=1)
    nyha4 = calculate_shfm_points(age=65, ejection_fraction=35, nyha_class=4)
    assert nyha4["mortality"]["1_year_percent"] > nyha1["mortality"]["1_year_percent"]


def test_nyha_4_highest_points():
    """NYHA IV should contribute the most points."""
    assert COEFFICIENTS["nyha_4"] > COEFFICIENTS["nyha_3"]
    assert COEFFICIENTS["nyha_3"] > COEFFICIENTS["nyha_2"]
    assert COEFFICIENTS["nyha_2"] > COEFFICIENTS["nyha_1"]


def test_nyha_invalid():
    """Invalid NYHA class should raise ValueError."""
    try:
        calculate_shfm_points(age=65, ejection_fraction=35, nyha_class=5)
        assert False
    except ValueError:
        pass


# =============================================================================
# Ejection Fraction Tests
# =============================================================================

def test_lower_ef_higher_mortality():
    """Lower EF -> higher mortality."""
    high_ef = calculate_shfm_points(age=65, ejection_fraction=50)
    low_ef = calculate_shfm_points(age=65, ejection_fraction=20)
    assert low_ef["mortality"]["1_year_percent"] > high_ef["mortality"]["1_year_percent"]


# =============================================================================
# Laboratory Values Tests
# =============================================================================

def test_low_sodium_higher_mortality():
    """Lower sodium -> higher mortality."""
    normal_na = calculate_shfm_points(age=65, ejection_fraction=35, sodium=140)
    low_na = calculate_shfm_points(age=65, ejection_fraction=35, sodium=130)
    assert low_na["mortality"]["1_year_percent"] > normal_na["mortality"]["1_year_percent"]


def test_high_creatinine_higher_mortality():
    """Higher creatinine -> higher mortality."""
    normal_cr = calculate_shfm_points(age=65, ejection_fraction=35, creatinine=1.0)
    high_cr = calculate_shfm_points(age=65, ejection_fraction=35, creatinine=3.0)
    assert high_cr["mortality"]["1_year_percent"] > normal_cr["mortality"]["1_year_percent"]


def test_low_hemoglobin_higher_mortality():
    """Lower hemoglobin -> higher mortality."""
    normal_hgb = calculate_shfm_points(age=65, ejection_fraction=35, hemoglobin=14)
    low_hgb = calculate_shfm_points(age=65, ejection_fraction=35, hemoglobin=9)
    assert low_hgb["mortality"]["1_year_percent"] > normal_hgb["mortality"]["1_year_percent"]


def test_high_bun_higher_mortality():
    """Higher BUN -> higher mortality."""
    normal_bun = calculate_shfm_points(age=65, ejection_fraction=35, bun=15)
    high_bun = calculate_shfm_points(age=65, ejection_fraction=35, bun=50)
    assert high_bun["mortality"]["1_year_percent"] > normal_bun["mortality"]["1_year_percent"]


# =============================================================================
# Medication Tests
# =============================================================================

def test_acei_reduces_mortality():
    """ACEi/ARB should reduce mortality."""
    no_med = calculate_shfm_points(age=65, ejection_fraction=35)
    with_med = calculate_shfm_points(age=65, ejection_fraction=35, acei_arb=True)
    assert with_med["mortality"]["1_year_percent"] < no_med["mortality"]["1_year_percent"]


def test_beta_blocker_reduces_mortality():
    """Beta-blocker should reduce mortality."""
    no_med = calculate_shfm_points(age=65, ejection_fraction=35)
    with_med = calculate_shfm_points(age=65, ejection_fraction=35, beta_blocker=True)
    assert with_med["mortality"]["1_year_percent"] < no_med["mortality"]["1_year_percent"]


def test_statin_reduces_mortality():
    """Statin should reduce mortality."""
    no_med = calculate_shfm_points(age=65, ejection_fraction=35)
    with_med = calculate_shfm_points(age=65, ejection_fraction=35, statin=True)
    assert with_med["mortality"]["1_year_percent"] < no_med["mortality"]["1_year_percent"]


def test_all_meds_best():
    """All medications together should give lowest mortality."""
    no_med = calculate_shfm_points(age=65, ejection_fraction=35)
    all_med = calculate_shfm_points(
        age=65, ejection_fraction=35, acei_arb=True, beta_blocker=True, statin=True
    )
    assert all_med["mortality"]["1_year_percent"] < no_med["mortality"]["1_year_percent"]


# =============================================================================
# Device Tests
# =============================================================================

def test_icd_reduces_mortality():
    """ICD should reduce mortality."""
    no_dev = calculate_shfm_points(age=65, ejection_fraction=35)
    with_dev = calculate_shfm_points(age=65, ejection_fraction=35, icd=True)
    assert with_dev["mortality"]["1_year_percent"] < no_dev["mortality"]["1_year_percent"]


def test_crt_reduces_mortality():
    """CRT should reduce mortality."""
    no_dev = calculate_shfm_points(age=65, ejection_fraction=35)
    with_dev = calculate_shfm_points(age=65, ejection_fraction=35, crt=True)
    assert with_dev["mortality"]["1_year_percent"] < no_dev["mortality"]["1_year_percent"]


def test_lvad_reduces_mortality():
    """LVAD should reduce mortality significantly."""
    no_dev = calculate_shfm_points(age=65, ejection_fraction=35)
    with_dev = calculate_shfm_points(age=65, ejection_fraction=35, lvad=True)
    assert with_dev["mortality"]["1_year_percent"] < no_dev["mortality"]["1_year_percent"]


# =============================================================================
# Risk Classification Tests
# =============================================================================

def test_risk_classification_low():
    """Young, healthy patient -> low risk."""
    result = calculate_shfm_points(
        age=40, ejection_fraction=55, nyha_class=1, sodium=142, creatinine=0.8,
        hemoglobin=14, acei_arb=True, beta_blocker=True,
    )
    assert result["risk_classification"] == "Low risk"


def test_risk_classification_very_high():
    """Elderly, sick patient -> very high risk."""
    result = calculate_shfm_points(
        age=80, ejection_fraction=15, nyha_class=4, sodium=128, creatinine=3.0,
        hemoglobin=9, bun=60, ischemic=True,
    )
    assert result["risk_classification"] == "Very high risk"


# =============================================================================
# Therapy Benefit Tests
# =============================================================================

def test_therapy_benefit_beta_blocker():
    """Beta-blocker should show absolute mortality reduction."""
    baseline = calculate_shfm_points(age=65, ejection_fraction=25, nyha_class=3)
    benefit = calculate_therapy_benefit(baseline, "beta_blocker")
    assert benefit["absolute_reduction"] > 0
    assert benefit["therapy"] == "beta_blocker"


def test_therapy_benefit_icd():
    """ICD should show mortality reduction."""
    baseline = calculate_shfm_points(age=65, ejection_fraction=25, nyha_class=3)
    benefit = calculate_therapy_benefit(baseline, "icd")
    assert benefit["absolute_reduction"] > 0


# =============================================================================
# Point Breakdown Tests
# =============================================================================

def test_point_breakdown_has_age():
    result = calculate_shfm_points(age=65, ejection_fraction=35)
    assert "age" in result["point_breakdown"]
    # Age coefficient is negated in the model so older = worse
    expected_age = -COEFFICIENTS["age"] * 65
    assert abs(result["point_breakdown"]["age"] - expected_age) < 0.001


def test_point_breakdown_has_ef():
    result = calculate_shfm_points(age=65, ejection_fraction=35)
    assert "ejection_fraction" in result["point_breakdown"]


# =============================================================================
# CLI Tests
# =============================================================================

def test_cli_calculate():
    from cli import main
    rc = main(["calculate", "--age", "65", "--ef", "35", "--nyha", "2"])
    assert rc == 0


def test_cli_calculate_with_meds():
    from cli import main
    rc = main(["calculate", "--age", "65", "--ef", "25", "--nyha", "3",
               "--acei-arb", "--beta-blocker", "--statin"])
    assert rc == 0


def test_cli_therapy():
    from cli import main
    rc = main(["therapy", "--therapy", "beta_blocker", "--age", "65", "--ef", "25", "--nyha", "3"])
    assert rc == 0
