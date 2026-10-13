"""
Distributed Component High-Throughput Traffic & Stress Testing Simulator for Seattle Heart Failure Model.
"""
import argparse
import time
import random
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from agents.models import SystemTaskPayload
from agents.supervisor import SystemSupervisor
from agents.base import PHIGuard, SecurityException, AuditLogger


def process_single_task(supervisor: SystemSupervisor, i: int) -> str:
    """Process a single simulation task and return its urgency classification."""
    p_val = random.uniform(5.0, 40.0)
    s_val = random.uniform(1.0, 20.0)
    is_crit = random.random() < 0.15
    descriptor = random.choice(["NOMINAL", "DISCORDANT_ANOMALY", "MUTANT_VARIANT", "OPTIMAL"])

    payload = SystemTaskPayload(
        task_id=f"SIM-{i+1:04d}",
        target_identifier=f"SPECIMEN-{random.randint(100, 999)}",
        primary_metric=round(p_val, 2),
        secondary_metric=round(s_val, 2),
        status_descriptor=descriptor,
        is_critical_flag=is_crit
    )

    dossier = supervisor.process_task(payload)
    return dossier.overall_urgency.value


def run_simulation(iterations: int = 100, concurrency: int = 1):
    """Run simulation with configurable concurrency."""
    if not isinstance(iterations, int) or not 1 <= iterations <= 100000:
        raise ValueError("iterations must be an integer between 1 and 100000")
    if not isinstance(concurrency, int) or not 1 <= concurrency <= 32:
        raise ValueError("concurrency must be an integer between 1 and 32")
    print(f"Starting generic rule-engine simulation ({iterations} tasks, concurrency={concurrency})...")
    supervisor = SystemSupervisor(model_provider="mock")
    start_time = time.time()
    nominal_count = 0
    elevated_count = 0
    critical_count = 0
    phi_blocked_count = 0

    if concurrency <= 1:
        # Sequential execution
        for i in range(iterations):
            urgency = process_single_task(supervisor, i)
            if urgency == "CRITICAL_STAT_PANIC":
                critical_count += 1
            elif urgency == "ELEVATED_RISK":
                elevated_count += 1
            else:
                nominal_count += 1

            # Adversarial PHI test injection (every 25 iterations)
            if (i + 1) % 25 == 0:
                try:
                    PHIGuard.assert_no_phi(f"Patient John Doe MRN-{random.randint(100000, 999999)} test")
                except SecurityException:
                    phi_blocked_count += 1
    else:
        # Concurrent execution
        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            futures = {executor.submit(process_single_task, supervisor, i): i for i in range(iterations)}
            for future in as_completed(futures):
                i = futures[future]
                urgency = future.result()
                if urgency == "CRITICAL_STAT_PANIC":
                    critical_count += 1
                elif urgency == "ELEVATED_RISK":
                    elevated_count += 1
                else:
                    nominal_count += 1

                # Adversarial PHI test injection (every 25 iterations)
                if (i + 1) % 25 == 0:
                    try:
                        PHIGuard.assert_no_phi(f"Patient John Doe MRN-{random.randint(100000, 999999)} test")
                    except SecurityException:
                        phi_blocked_count += 1

    elapsed = time.time() - start_time
    print("\n" + "=" * 70)
    print(f"  GENERIC RULE DEMONSTRATION — SIMULATION SUMMARY")
    print("=" * 70)
    print(f"  Total Tasks Processed:     {iterations}")
    print(f"  Concurrency:               {concurrency}")
    print(f"  Elapsed Time:              {elapsed:.3f} seconds ({iterations/max(0.001, elapsed):.1f} tasks/sec)")
    print(f"  Routine Outcomes:          {nominal_count} ({nominal_count/iterations*100:.1f}%)")
    print(f"  Elevated Risk Outcomes:    {elevated_count} ({elevated_count/iterations*100:.1f}%)")
    print(f"  Critical Interventions:    {critical_count} ({critical_count/iterations*100:.1f}%)")
    print(f"  Synthetic identifier pattern detections: {phi_blocked_count}")
    print(f"  HMAC Audit Ledger Blocks:  {len(AuditLogger.get_trail())}")
    print(f"  HMAC Cryptographic Check:  {AuditLogger.verify_integrity()}")
    print("=" * 70)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seattle Heart Failure Model Simulator")
    parser.add_argument("--tasks", type=int, default=100, help="Number of tasks to simulate")
    parser.add_argument("--concurrency", type=int, default=1, help="Number of concurrent workers")
    args = parser.parse_args()
    run_simulation(args.tasks, args.concurrency)
