#!/usr/bin/env python3
"""
CLI for Seattle Heart Failure Model Calculator.

Provides commands for SHFM 1-year mortality prediction, therapy benefit analysis,
and enterprise audit/chat operations.
"""
import argparse
import json
import sys

from shfm_calc import calculate_shfm_points, calculate_therapy_benefit

from agents.supervisor import SystemSupervisor
from agents.base import AuditLogger
from agents.models import SystemTaskPayload


def cmd_calculate(args):
    """Calculate SHFM score and survival."""
    result = calculate_shfm_points(
        age=args.age,
        sex=args.sex,
        nyha_class=args.nyha,
        weight_kg=args.weight,
        ischemic=args.ischemic,
        ejection_fraction=args.ef,
        systolic_bp=args.sbp,
        diastolic_bp=args.dbp,
        sodium=args.sodium,
        creatinine=args.creatinine,
        hemoglobin=args.hemoglobin,
        lymphocytes=args.lymphocytes,
        uric_acid=args.uric_acid,
        bun=args.bun,
        acei_arb=args.acei_arb,
        beta_blocker=args.beta_blocker,
        statin=args.statin,
        allopurinol=args.allopurinol,
        icd=args.icd,
        crt=args.crt,
        lvad=args.lvad,
    )

    print("=" * 60)
    print("  SEATTLE HEART FAILURE MODEL")
    print("=" * 60)
    print(f"  Patient: {args.age} y/o {args.sex}, NYHA Class {args.nyha}")
    print(f"  EF: {args.ef}% | SBP/DBP: {args.sbp}/{args.dbp} mmHg")
    print(f"  Na: {args.sodium} | Cr: {args.creatinine} | Hgb: {args.hemoglobin}")
    print(f"  Lymphocytes: {args.lymphocytes} | UA: {args.uric_acid} | BUN: {args.bun}")

    meds = []
    if args.acei_arb: meds.append("ACEi/ARB")
    if args.beta_blocker: meds.append("Beta-blocker")
    if args.statin: meds.append("Statin")
    if args.allopurinol: meds.append("Allopurinol")
    devices = []
    if args.icd: devices.append("ICD")
    if args.crt: devices.append("CRT")
    if args.lvad: devices.append("LVAD")

    if meds:
        print(f"  Medications: {', '.join(meds)}")
    if devices:
        print(f"  Devices: {', '.join(devices)}")

    print(f"\n  SHFM Score: {result['total_points']:.4f}")
    print(f"\n  SURVIVAL ESTIMATES:")
    print(f"    1-year survival: {result['survival']['1_year']*100:.1f}%")
    print(f"    2-year survival: {result['survival']['2_year']*100:.1f}%")
    print(f"    5-year survival: {result['survival']['5_year']*100:.1f}%")

    print(f"\n  MORTALITY ESTIMATES:")
    print(f"    1-year mortality: {result['mortality']['1_year_percent']:.2f}%")
    print(f"    2-year mortality: {result['mortality']['2_year_percent']:.2f}%")
    print(f"    5-year mortality: {result['mortality']['5_year_percent']:.2f}%")

    print(f"\n  RISK: {result['risk_classification']} - {result['risk_description']}")

    if args.json:
        print("\n" + json.dumps(result, indent=2))
    return 0


def cmd_therapy(args):
    """Calculate therapy benefit."""
    # First calculate baseline
    baseline = calculate_shfm_points(
        age=args.age, sex=args.sex, nyha_class=args.nyha,
        weight_kg=args.weight, ischemic=args.ischemic,
        ejection_fraction=args.ef, systolic_bp=args.sbp,
        diastolic_bp=args.dbp, sodium=args.sodium,
        creatinine=args.creatinine, hemoglobin=args.hemoglobin,
        lymphocytes=args.lymphocytes, uric_acid=args.uric_acid,
        bun=args.bun,
    )

    result = calculate_therapy_benefit(baseline, args.therapy)

    print("=" * 60)
    print(f"  THERAPY BENEFIT ANALYSIS: {args.therapy.upper()}")
    print("=" * 60)
    print(f"  Baseline 1-year mortality: {result['baseline_mortality_1yr']:.2f}%")
    print(f"  Projected 1-year mortality: {result['projected_mortality_1yr']:.2f}%")
    print(f"  Absolute reduction: {result['absolute_reduction']:.2f}%")
    print(f"  Relative reduction: {result['relative_reduction_percent']:.1f}%")

    if args.json:
        print("\n" + json.dumps(result, indent=2))
    return 0


def cmd_audit(args):
    """Run enterprise audit task evaluation."""
    supervisor = SystemSupervisor(model_provider="mock")
    payload = SystemTaskPayload(
        task_id=args.task_id,
        target_identifier=getattr(args, "target_id", "CLI-TARGET"),
        primary_metric=getattr(args, "primary_metric", 10.0),
        secondary_metric=getattr(args, "secondary_metric", 3.0),
        status_descriptor=getattr(args, "status", "NOMINAL"),
        is_critical_flag=getattr(args, "critical", False),
    )
    dossier = supervisor.process_task(payload)
    print(json.dumps(dossier.to_dict(), indent=2))
    return 0


def cmd_chat(args):
    """Query the supervisory chat system."""
    supervisor = SystemSupervisor(model_provider="mock")
    query = " ".join(args.query_parts)
    response = supervisor.query_supervisory_chat(query)
    print(response)
    return 0


def cmd_verify_audit(args):
    """Verify HMAC audit trail integrity."""
    verified = AuditLogger.verify_integrity()
    trail = AuditLogger.get_trail()
    print(f"Audit trail integrity: {'VERIFIED' if verified else 'COMPROMISED'}")
    print(f"Total audit blocks: {len(trail)}")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="shfm",
        description="Seattle Heart Failure Model Calculator",
    )
    parser.add_argument("--json", action="store_true", help="Also output JSON")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Calculate
    p_calc = subparsers.add_parser("calculate", help="Calculate SHFM score")
    p_calc.add_argument("--age", type=float, required=True, help="Age in years")
    p_calc.add_argument("--sex", choices=["male", "female"], default="male", help="Sex")
    p_calc.add_argument("--nyha", type=int, choices=[1, 2, 3, 4], default=2, help="NYHA class")
    p_calc.add_argument("--weight", type=float, default=80, help="Weight in kg")
    p_calc.add_argument("--ischemic", action="store_true", help="Ischemic etiology")
    p_calc.add_argument("--ef", type=float, required=True, help="Ejection fraction %%")
    p_calc.add_argument("--sbp", type=float, default=120, help="Systolic BP mmHg")
    p_calc.add_argument("--dbp", type=float, default=80, help="Diastolic BP mmHg")
    p_calc.add_argument("--sodium", type=float, default=140, help="Serum sodium mEq/L")
    p_calc.add_argument("--creatinine", type=float, default=1.2, help="Creatinine mg/dL")
    p_calc.add_argument("--hemoglobin", type=float, default=13, help="Hemoglobin g/dL")
    p_calc.add_argument("--lymphocytes", type=float, default=1.5, help="Lymphocytes (1000/uL)")
    p_calc.add_argument("--uric-acid", type=float, default=6.0, help="Uric acid mg/dL")
    p_calc.add_argument("--bun", type=float, default=20, help="BUN mg/dL")
    p_calc.add_argument("--acei-arb", action="store_true", help="On ACEi/ARB")
    p_calc.add_argument("--beta-blocker", action="store_true", help="On beta-blocker")
    p_calc.add_argument("--statin", action="store_true", help="On statin")
    p_calc.add_argument("--allopurinol", action="store_true", help="On allopurinol")
    p_calc.add_argument("--icd", action="store_true", help="Has ICD")
    p_calc.add_argument("--crt", action="store_true", help="Has CRT")
    p_calc.add_argument("--lvad", action="store_true", help="Has LVAD")

    # Therapy benefit
    p_therapy = subparsers.add_parser("therapy", help="Calculate therapy benefit")
    p_therapy.add_argument("--therapy", required=True,
                          choices=["acei_arb", "beta_blocker", "statin", "icd", "crt", "lvad"],
                          help="Therapy to evaluate")
    p_therapy.add_argument("--age", type=float, required=True, help="Age")
    p_therapy.add_argument("--sex", choices=["male", "female"], default="male")
    p_therapy.add_argument("--nyha", type=int, choices=[1, 2, 3, 4], default=2)
    p_therapy.add_argument("--weight", type=float, default=80)
    p_therapy.add_argument("--ischemic", action="store_true")
    p_therapy.add_argument("--ef", type=float, required=True, help="EF %%")
    p_therapy.add_argument("--sbp", type=float, default=120)
    p_therapy.add_argument("--dbp", type=float, default=80)
    p_therapy.add_argument("--sodium", type=float, default=140)
    p_therapy.add_argument("--creatinine", type=float, default=1.2)
    p_therapy.add_argument("--hemoglobin", type=float, default=13)
    p_therapy.add_argument("--lymphocytes", type=float, default=1.5)
    p_therapy.add_argument("--uric-acid", type=float, default=6.0)
    p_therapy.add_argument("--bun", type=float, default=20)

    # Audit
    p_audit = subparsers.add_parser("audit", help="Run enterprise audit task evaluation")
    p_audit.add_argument("--task-id", default="CLI-TASK-01", help="Task identifier")
    p_audit.add_argument("--target-id", default="CLI-TARGET", help="Target identifier")
    p_audit.add_argument("--primary-metric", type=float, default=10.0, help="Primary metric")
    p_audit.add_argument("--secondary-metric", type=float, default=3.0, help="Secondary metric")
    p_audit.add_argument("--status", default="NOMINAL", help="Status descriptor")
    p_audit.add_argument("--critical", action="store_true", help="Critical flag")

    # Chat
    p_chat = subparsers.add_parser("chat", help="Query supervisory chat")
    p_chat.add_argument("query_parts", nargs="+", help="Query text")

    # Verify audit
    p_verify = subparsers.add_parser("verify-audit", help="Verify HMAC audit trail integrity")

    args = parser.parse_args(argv)

    if args.command == "calculate":
        return cmd_calculate(args)
    elif args.command == "therapy":
        return cmd_therapy(args)
    elif args.command == "audit":
        return cmd_audit(args)
    elif args.command == "chat":
        return cmd_chat(args)
    elif args.command == "verify-audit":
        return cmd_verify_audit(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
