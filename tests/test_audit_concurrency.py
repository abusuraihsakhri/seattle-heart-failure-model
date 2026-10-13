"""Concurrency and input safety for the retained generic demonstration."""
from concurrent.futures import ThreadPoolExecutor
import pytest
from agents.base import AuditTrail
from simulator import run_simulation

def test_parallel_hmac_chain():
    audit = AuditTrail("test-key")
    with ThreadPoolExecutor(max_workers=12) as pool:
        list(pool.map(lambda i: audit.log("test", "demo", "TASK", {"iteration": i}), range(100)))
    assert len(audit.get_trail()) == 100
    assert audit.verify_integrity()

@pytest.mark.parametrize("iterations,concurrency", [(0,1), (-1,1), (5,0), (5,100), (100001,1)])
def test_simulation_bounds(iterations, concurrency):
    with pytest.raises(ValueError):
        run_simulation(iterations, concurrency)
