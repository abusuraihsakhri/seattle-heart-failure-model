"""Deterministic cross-runtime consistency checks for Python and browser SHFM."""
import json
import random
import shutil
import subprocess

import pytest
from shfm_calc import calculate_shfm_points

@pytest.mark.skipif(shutil.which("node") is None, reason="Node.js not installed")
def test_browser_python_parity():
    gen = random.Random(385)
    scenarios = []
    for _ in range(40):
        scenarios.append({
            "age": gen.uniform(35, 90), "sex": gen.choice(["male", "female"]),
            "nyha_class": gen.randint(1, 4), "ischemic": bool(gen.getrandbits(1)),
            "ejection_fraction": gen.uniform(15, 60), "systolic_bp": gen.uniform(90, 180),
            "sodium": gen.uniform(120, 150), "hemoglobin": gen.uniform(8, 18),
            "lymphocyte_percent": gen.uniform(7, 60), "uric_acid": gen.uniform(3, 13),
            "total_cholesterol": gen.uniform(100, 260), "weight_kg": gen.uniform(45, 135),
            "loop_diuretic_mg_day": gen.uniform(0, 160),
            "ace_inhibitor": bool(gen.getrandbits(1)), "arb": bool(gen.getrandbits(1)),
            "beta_blocker": bool(gen.getrandbits(1)), "statin": bool(gen.getrandbits(1)),
            "allopurinol": bool(gen.getrandbits(1)),
            "potassium_sparing_diuretic": bool(gen.getrandbits(1)),
            "device": gen.choice(["none", "icd", "biv_pacemaker", "biv_icd"]),
        })
    script = ("const fs=require('node:fs');"
              "const {calculate}=require('./web/calculator.js');"
              "const input=JSON.parse(fs.readFileSync(0,'utf8'));"
              "process.stdout.write(JSON.stringify(input.map(calculate)));" )
    proc = subprocess.run(["node", "-e", script], input=json.dumps(scenarios),
                          capture_output=True, text=True, check=True)
    browser_results = json.loads(proc.stdout)
    for profile, browser in zip(scenarios, browser_results):
        py = calculate_shfm_points(**profile)
        assert browser["score"] == pytest.approx(py["total_points"], abs=0.000051)
        for year in (1, 2, 3, 5):
            assert browser["survival"][str(year)] == pytest.approx(
                py["survival"][f"{year}_year"], abs=0.000051)
