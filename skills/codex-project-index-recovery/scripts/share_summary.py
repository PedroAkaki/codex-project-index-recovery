"""Export a conservative aggregate allowlist from a private diagnostic report."""
import argparse
import json
from pathlib import Path

COUNTS = ('sql_projects', 'sql_roots', 'sql_assignments', 'cache_projects',
          'cache_assignments', 'json_nul_bytes', 'foreign_key_errors')
FLAGS = ('source_files_unchanged_during_copy', 'json_valid', 'integrity_ok',
         'legacy_schema_compatible', 'cache_gap_observed', 'candidate_requested',
         'live_repair_applied')
STATUSES = {'PREPARED_PRIVATE_NOT_APPLIED', 'BLOCKED', 'BLOCKED_SCHEMA_OR_INTEGRITY'}

def summarize(report):
    if not isinstance(report, dict):
        raise ValueError('Report must be an object')
    output = {'summary_format': 1, 'scope': 'Aggregate diagnostic summary; raw evidence excluded'}
    for key in COUNTS:
        value = report.get(key)
        if type(value) is int and value >= 0:
            output[key] = value
    for key in FLAGS:
        value = report.get(key)
        if type(value) is bool:
            output[key] = value
    status = report.get('candidate_status')
    if isinstance(status, str) and status in STATUSES:
        output['candidate_status'] = status
    return output

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    if args.out.resolve() == args.report.resolve():
        raise ValueError('Summary must not overwrite the private report')
    data = summarize(json.loads(args.report.read_text(encoding='utf-8-sig')))
    with args.out.open('x', encoding='utf-8') as handle:
        json.dump(data, handle, indent=2)
        handle.write('\n')
    print('Aggregate summary created. Review before sharing.')

if __name__ == '__main__':
    main()
