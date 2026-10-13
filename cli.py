#!/usr/bin/env python3
"""Command-line interface for research SHFM estimates and legacy audit tools."""
import argparse
import json
import sys

from shfm_calc import calculate_shfm_points, calculate_therapy_benefit, DEVICE_TYPES


def _input_values(a):
    return dict(age=a.age, sex=a.sex, nyha_class=a.nyha, ischemic=a.ischemic,
                ejection_fraction=a.ef, systolic_bp=a.sbp, sodium=a.sodium,
                hemoglobin=a.hemoglobin, lymphocyte_percent=a.lymphocyte_percent,
                uric_acid=a.uric_acid, total_cholesterol=a.total_cholesterol,
                weight_kg=a.weight, loop_diuretic_mg_day=a.loop_diuretic_mg_day,
                ace_inhibitor=a.ace_inhibitor, arb=a.arb, beta_blocker=a.beta_blocker,
                statin=a.statin, allopurinol=a.allopurinol,
                potassium_sparing_diuretic=a.potassium_sparing_diuretic,
                device=a.device)


def _print_result(result, as_json=False):
    if as_json:
        print(json.dumps(result, indent=2))
    else:
        print('Original SHFM (2006) | Research / education only')
        print('Score: ', result['total_points'])
        for year in (1, 2, 3, 5):
            print(f'{year}-year survival: {100 * result["survival"][f"{year}_year"]:.1f}%')
        print(result['disclaimer'])


def main(argv=None):
    p = argparse.ArgumentParser(prog='shfm', description='Original 2006 SHFM research calculator')
    p.add_argument('--json', action='store_true', help='Output JSON (before subcommand)')
    sub = p.add_subparsers(dest='command', required=True)
    for name in ('calculate', 'therapy'):
        s = sub.add_parser(name, help='SHFM estimates' if name == 'calculate' else 'Noncausal therapy scenario')
        s.add_argument('--age', type=float, required=True)
        s.add_argument('--sex', choices=['male', 'female'], required=True)
        s.add_argument('--nyha', type=int, choices=[1, 2, 3, 4], required=True)
        s.add_argument('--ischemic', action='store_true')
        s.add_argument('--ef', type=float, required=True)
        s.add_argument('--sbp', type=float, required=True)
        s.add_argument('--sodium', type=float, required=True)
        s.add_argument('--hemoglobin', type=float, required=True)
        s.add_argument('--lymphocyte-percent', type=float, required=True, help='Lymphocytes as % of leukocytes')
        s.add_argument('--uric-acid', type=float, required=True)
        s.add_argument('--total-cholesterol', type=float, required=True, help='mg/dL')
        s.add_argument('--weight', type=float, required=True, help='kg')
        s.add_argument('--loop-diuretic-mg-day', type=float, required=True, help='Furosemide-equivalent mg/day, 0 if none')
        s.add_argument('--ace-inhibitor', action='store_true')
        s.add_argument('--arb', action='store_true')
        s.add_argument('--beta-blocker', action='store_true')
        s.add_argument('--statin', action='store_true')
        s.add_argument('--allopurinol', action='store_true')
        s.add_argument('--potassium-sparing-diuretic', action='store_true')
        s.add_argument('--device', choices=DEVICE_TYPES, default='none')
        if name == 'therapy':
            s.add_argument('--therapy', required=True,
                           choices=['ace_inhibitor','arb','beta_blocker','potassium_sparing_diuretic'])

    audit = sub.add_parser('audit', help='Legacy generic rule demonstration')
    audit.add_argument('--task-id', default='CLI-TASK-01')
    audit.add_argument('--target-id', default='CLI-TARGET')
    audit.add_argument('--primary-metric', type=float, default=10.0)
    audit.add_argument('--secondary-metric', type=float, default=3.0)
    audit.add_argument('--status', default='NOMINAL')
    audit.add_argument('--critical', action='store_true')
    chat = sub.add_parser('chat', help='Deterministic placeholder response only')
    chat.add_argument('query_parts', nargs='+')
    sub.add_parser('verify-audit', help='Verify current process in-memory audit trail')
    a = p.parse_args(argv)
    try:
        if a.command in ('calculate', 'therapy'):
            initial = calculate_shfm_points(**_input_values(a))
            result = initial if a.command == 'calculate' else calculate_therapy_benefit(initial, a.therapy)
            _print_result(result, a.json) if a.command == 'calculate' else print(json.dumps(result, indent=2))
        elif a.command == 'audit':
            from agents.models import SystemTaskPayload
            from agents.supervisor import SystemSupervisor
            data = SystemTaskPayload(task_id=a.task_id, target_identifier=a.target_id,
                                     primary_metric=a.primary_metric, secondary_metric=a.secondary_metric,
                                     status_descriptor=a.status, is_critical_flag=a.critical)
            print(json.dumps(SystemSupervisor().process_task(data).to_dict(), indent=2))
        elif a.command == 'chat':
            from agents.supervisor import SystemSupervisor
            print(SystemSupervisor().query_supervisory_chat(' '.join(a.query_parts)))
        else:
            from agents.base import AuditLogger
            ok = AuditLogger.verify_integrity()
            print(f'In-memory audit trail integrity: {"VERIFIED" if ok else "FAILED"}')
            return 0 if ok else 1
    except ValueError as exc:
        print(f'Input error: {exc}', file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main())
