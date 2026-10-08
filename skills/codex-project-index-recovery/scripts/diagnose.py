"""Private, read-only Codex snapshot and legacy recovery candidate. No live writes."""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import sqlite3
from contextlib import nullcontext
from datetime import datetime, timezone

NAMES = ['.codex-global-state.json', '.codex-global-state.json.bak',
         'state_5.sqlite', 'state_5.sqlite-wal', 'state_5.sqlite-shm']
KEYS = ('local-projects', 'thread-project-assignments', 'project-order')

def fingerprint(path):
    if not path.exists():
        return None
    s = path.stat()
    with path.open('rb') as f:
        digest = hashlib.file_digest(f, 'sha256').hexdigest()
    if (s.st_size, s.st_mtime_ns) != (path.stat().st_size, path.stat().st_mtime_ns):
        raise RuntimeError('Source changed during hashing')
    return {'bytes': s.st_size, 'mtime_ns': s.st_mtime_ns, 'sha256': digest}

def unique(pairs):
    result = {}
    for k, v in pairs:
        if k in result:
            raise ValueError('Duplicate JSON key')
        result[k] = v
    return result

def make_candidate(j, projects, roots, threads):
    if not isinstance(j, dict):
        raise ValueError('Global JSON is not an object')
    for key in ('local-projects', 'thread-project-assignments'):
        if key in j and not isinstance(j[key], dict):
            raise ValueError('Invalid recovery field type')
    if 'project-order' in j and not isinstance(j['project-order'], list):
        raise ValueError('Invalid project order type')
    if any(j.get(k) for k in KEYS):
        raise ValueError('Nonempty recovery fields require conflict review')
    if j.get('app-server-pending-project-deletions-by-host'):
        raise ValueError('Pending deletions require review')
    for k, v in j.items():
        if 'project' in k.lower() and ('delet' in k.lower() or 'tombstone' in k.lower()) and v:
            raise ValueError('Deletion metadata requires review')
    ids = {p['id'] for p in projects}
    if len(ids) != len(projects) or not ids:
        raise ValueError('Empty or duplicate SQL project ids')
    if any(r['project_id'] not in ids for r in roots):
        raise ValueError('Orphan root')
    if any(pid is not None and pid not in ids for _, pid in threads):
        raise ValueError('Orphan assignment')
    projectless = j.get('projectless-thread-ids', [])
    if not isinstance(projectless, list) or any(not isinstance(t, str) for t in projectless):
        raise ValueError('Invalid projectless classifications')
    assigned = {t for t, pid in threads if pid is not None}
    if assigned.intersection(projectless):
        raise ValueError('Projectless classification conflicts with SQL assignment')
    result = copy.deepcopy(j)
    catalog = {}
    for p in projects:
        if not isinstance(p['id'], str) or not isinstance(p['name'], str):
            raise ValueError('Invalid project id/name')
        if any(type(p[k]) is not int for k in ('created_at_ms', 'updated_at_ms')):
            raise ValueError('Invalid project timestamps')
        paths = [r['path'] for r in roots if r['project_id'] == p['id']]
        if any(not isinstance(pth, str) for pth in paths):
            raise ValueError('Invalid root path')
        catalog[p['id']] = dict(id=p['id'], name=p['name'], rootPaths=paths,
                                createdAt=p['created_at_ms'], updatedAt=p['updated_at_ms'])
    result.update({'local-projects': catalog, 'project-order': list(catalog),
                   'thread-project-assignments': {t: {'projectKind': 'local', 'projectId': pid}
                                                  for t, pid in threads if pid is not None}})
    assert {k:v for k,v in result.items() if k not in KEYS} == {k:v for k,v in j.items() if k not in KEYS}
    return result

def diagnose(home, out, candidate=False):
    home, out = home.resolve(), out.resolve()
    if out == home or home in out.parents:
        raise ValueError('Snapshot output must be outside Codex home')
    out.mkdir(parents=True, exist_ok=False)
    before = {n: fingerprint(home/n) for n in NAMES}
    for n in NAMES:
        if before[n] is not None:
            shutil.copy2(home/n, out/n)
    after = {n: fingerprint(home/n) for n in NAMES}
    if before != after or any(fingerprint(out/n) != before[n] for n in NAMES):
        raise RuntimeError('State changed while copying; snapshot rejected. Close app and retry with a new output.')
    report = {'captured_at_utc': datetime.now(timezone.utc).isoformat(),
              'scope': 'Focused project-state snapshot; not a full Codex backup',
              'source_files_unchanged_during_copy': True, 'files': before,
              'candidate_requested': candidate, 'live_repair_applied': False}
    j = None
    if before[NAMES[0]] is not None:
        raw = (out/NAMES[0]).read_bytes()
        report['json_nul_bytes'] = raw.count(b'\x00')
        try:
            j = json.loads(raw.decode('utf-8-sig'), object_pairs_hook=unique)
            if not isinstance(j, dict):
                raise ValueError('Global JSON is not an object')
            report['json_valid'] = True
            report['cache_projects'] = len(j.get('local-projects', {}))
            report['cache_assignments'] = len(j.get('thread-project-assignments', {}))
        except (ValueError, TypeError, UnicodeError):
            report['json_valid'] = False
            report['json_error'] = 'Invalid JSON or unsupported recovery field types'
            j = None
    else:
        report['json_valid'] = False
        report['json_error'] = 'Global state file missing'
    if before['state_5.sqlite'] is None:
        report['database_error'] = 'Database missing; do not infer project deletion'
    else:
        # Work on a second copy: SQLite may update private SHM, never snapshot evidence.
        # Ordinary inherited ACLs avoid Windows sandbox failures from chmod(0700).
        analysis = out/'sqlite-analysis'
        analysis.mkdir()
        with nullcontext(analysis) as scratch:
            scratch = Path(scratch)
            for n in NAMES[2:]:
                if before[n] is not None:
                    shutil.copy2(out/n, scratch/n)
            c = sqlite3.connect((scratch/'state_5.sqlite').as_uri()+'?mode=ro', uri=True)
            c.row_factory = sqlite3.Row
            try:
                c.execute('PRAGMA query_only=ON')
                c.execute('BEGIN')
                report['integrity_ok'] = [r[0] for r in c.execute('PRAGMA integrity_check')] == ['ok']
                report['foreign_key_errors'] = len(list(c.execute('PRAGMA foreign_key_check')))
                schema = {r[0]: [v[1] for v in c.execute('PRAGMA table_info("'+r[0]+'")')]
                          for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'")
                          if r[0] in ('projects', 'project_roots', 'threads')}
                report['project_schema'] = schema
                required = {'projects': {'id','name','position','created_at_ms','updated_at_ms'},
                            'project_roots': {'project_id','path','position'},
                            'threads': {'id','project_id'}}
                compatible = all(cols <= set(schema.get(t, [])) for t, cols in required.items())
                report['legacy_schema_compatible'] = compatible
                if compatible and report['integrity_ok'] and not report['foreign_key_errors']:
                    projects = [dict(r) for r in c.execute('SELECT id,name,position,created_at_ms,updated_at_ms FROM projects ORDER BY position,id')]
                    roots = [dict(r) for r in c.execute('SELECT project_id,path,position FROM project_roots ORDER BY project_id,position')]
                    threads = [(r[0],r[1]) for r in c.execute('SELECT id,project_id FROM threads ORDER BY id')]
                    report.update(sql_projects=len(projects), sql_roots=len(roots),
                                  sql_assignments=sum(pid is not None for _,pid in threads))
                    report['cache_gap_observed'] = j is not None and len(j.get('local-projects', {})) == 0 and len(projects) > 0
                    if candidate:
                        try:
                            proposed = make_candidate(j, projects, roots, threads)
                            (out/'candidate-global-state.json').write_text(json.dumps(proposed, ensure_ascii=False, indent=2), encoding='utf-8')
                            report['candidate_status'] = 'PREPARED_PRIVATE_NOT_APPLIED'
                            report['candidate_changed_fields'] = list(KEYS)
                        except ValueError as e:
                            report['candidate_status'] = 'BLOCKED'
                            report['candidate_reason'] = str(e)
                elif candidate:
                    report['candidate_status'] = 'BLOCKED_SCHEMA_OR_INTEGRITY'
            finally:
                c.close()
    (out/'report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    return report

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--codex-home', type=Path, default=Path(os.environ.get('CODEX_HOME', str(Path.home()/'.codex'))))
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--candidate', action='store_true')
    a = p.parse_args()
    print(json.dumps(diagnose(a.codex_home, a.out, a.candidate), indent=2))

if __name__ == '__main__':
    main()
