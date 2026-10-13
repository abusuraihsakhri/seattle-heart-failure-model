"""Published-reference and regression tests for the original 2006 SHFM."""
import math
import pytest
from shfm_calc import calculate_shfm_points, calculate_therapy_benefit

BASE = dict(age=60, sex="male", nyha_class=2, ischemic=False, ejection_fraction=30,
            systolic_bp=120, sodium=140, hemoglobin=14, lymphocyte_percent=25,
            uric_acid=6, total_cholesterol=180, weight_kg=80, loop_diuretic_mg_day=0,
            ace_inhibitor=True, beta_blocker=True)

def run(**changes):
    return calculate_shfm_points(**{**BASE, **changes})

def test_published_reference():
    result = run()
    assert result["total_points"] == pytest.approx(-0.1089, abs=0.0001)
    assert result["survival"]["1_year"] == pytest.approx(0.9643, abs=0.0001)
    assert result["survival"]["2_year"] == pytest.approx(0.9300, abs=0.0002)
    assert result["survival"]["3_year"] == pytest.approx(0.897, abs=0.001)

def test_survival_monotonic_and_complementary():
    result = run()
    assert 1 >= result["survival"]["1_year"] >= result["survival"]["2_year"] >= result["survival"]["3_year"] >= result["survival"]["5_year"] >= 0
    for year in (1, 2, 3, 5):
        key = f"{year}_year"
        assert result["survival"][key] + result["mortality"][key] == pytest.approx(1, abs=0.0001)

def test_factors_and_truncations():
    assert run(age=80)["mortality"]["1_year"] > run(age=40)["mortality"]["1_year"]
    assert run(nyha_class=4)["mortality"]["1_year"] > run(nyha_class=2)["mortality"]["1_year"]
    assert run(ejection_fraction=20)["mortality"]["1_year"] > run(ejection_fraction=45)["mortality"]["1_year"]
    assert run(sodium=129)["mortality"]["1_year"] > run(sodium=140)["mortality"]["1_year"]
    assert run(allopurinol=True)["mortality"]["1_year"] > run(allopurinol=False)["mortality"]["1_year"]
    assert run(loop_diuretic_mg_day=80)["mortality"]["1_year"] > run(loop_diuretic_mg_day=0)["mortality"]["1_year"]
    assert run(lymphocyte_percent=48)["total_points"] == run(lymphocyte_percent=80)["total_points"]
    assert run(systolic_bp=161)["total_points"] == run(systolic_bp=190)["total_points"]

@pytest.mark.parametrize("name,value", [
    ("age", math.nan), ("age", math.inf), ("weight_kg", 0),
    ("ejection_fraction", 0), ("systolic_bp", -10), ("hemoglobin", 0),
    ("total_cholesterol", 0), ("lymphocyte_percent", 101),
    ("loop_diuretic_mg_day", -1), ("nyha_class", 1.5), ("sex", "invalid"),
    ("device", "lvad"), ("age", True),
])
def test_bad_inputs(name, value):
    with pytest.raises(ValueError):
        run(**{name: value})

def test_therapy_benefit_is_noncausal():
    initial = run(beta_blocker=False)
    projected = calculate_therapy_benefit(initial, "beta_blocker")
    assert projected["absolute_reduction"] > 0
    assert "not a causal" in projected["interpretation"]
    with pytest.raises(ValueError):
        calculate_therapy_benefit(initial, "statin")
    with pytest.raises(ValueError):
        calculate_therapy_benefit(run(), "beta_blocker")

def test_cli_published_case():
    from cli import main
    args = ["calculate", "--age", "60", "--sex", "male", "--nyha", "2", "--ef", "30",
            "--sbp", "120", "--sodium", "140", "--hemoglobin", "14",
            "--lymphocyte-percent", "25", "--uric-acid", "6",
            "--total-cholesterol", "180", "--weight", "80",
            "--loop-diuretic-mg-day", "0", "--ace-inhibitor", "--beta-blocker"]
    assert main(args) == 0
