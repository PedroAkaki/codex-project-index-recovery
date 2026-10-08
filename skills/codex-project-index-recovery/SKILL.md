---
name: codex-project-index-recovery
description: Diagnose missing local Codex Desktop projects after a crash, restart, or power loss; distinguish sidebar index loss from database loss and prepare a reviewed recovery candidate. Use when projects disappeared from the sidebar. Does not recover deleted source files or migrate computers.
---

# Codex Project Index Recovery

Restore project visibility from current evidence while preserving intentional deletions. Follow explicit user instructions over workflow defaults; authorization does not waive integrity or concurrency checks.

## 1. Diagnose

- Resolve the selected local profile (`CODEX_HOME` or the user's profile). Confirm local versus cloud scope with available app tools. An empty cloud response does not prove local deletion.
- Run `python <skill-dir>/scripts/diagnose.py --codex-home <home> --out <new-private-directory>` using Python 3.11+. Output must be outside Codex home. The script copies stable JSON/SQLite/WAL/SHM files and analyzes a second private SQLite copy read-only; it never writes live state.
- Compare `sql_projects`, `cache_projects`, JSON validity, integrity and schema compatibility. Inspect current app version and relevant local logs before attributing a cause. An outage preceding the symptom does not prove corruption was caused by the outage.
- If copying is unstable, inspect writers and arrange an offline snapshot. Do not bypass stability checks. Window closure alone does not prove process termination.

## 2. Prepare

When SQL still contains projects and the compatible JSON cache is empty, read [references/recovery.md](references/recovery.md). Run the diagnostic again with `--candidate` and a fresh output directory. A candidate is private and is not a live repair.

Stop for unknown schemas, corrupt JSON without a validated baseline, nonempty recovery fields, pending deletions, orphan associations, or conflicting projectless classifications. Report the specific guard; do not invent settings, reset migrations or restore historical catalogs to bypass it.

## 3. Execute a reviewed repair

The bundle has no live repair or app-closure executable. Prepare a version-specific executor only when requested and supported by current evidence. Present the exact three-field diff, current counts, backup and rollback route; obtain authorization if it has not already been given for this repair. Read the live-execution section of the reference for process, fresh-snapshot, atomic-write and preservation checks.

If automatic app closure is explicitly authorized, use an independent one-shot worker and a visible save countdown. Verify ownership by executable, ancestry and process creation time; attempt normal closure first. Force remaining exact owned identities only within that authorization. External CLI writers block repair. Persist blockers on timeout, distinguish waiting from writing, and remove the temporary task when finished. Do not ask the user to repeat blind timed waits.

## 4. Verify and report

Report one of: `DIAGNOSED`, `PREPARED_PRIVATE_NOT_APPLIED`, `BLOCKED`, `APPLIED_UI_VERIFICATION_PENDING`, `UI_VERIFIED`. Include evidence and any remaining check. Accept UI recovery only after reopening Codex and checking visible projects, order and representative chat associations; confirm those checks rather than inferring them from a successful write.

## Privacy and sharing

Snapshots, candidates, databases and logs remain private; they can contain conversations, paths and project names. For an external summary, run `scripts/share_summary.py --report <private-report.json> --out <new-summary.json>` and review the aggregate result. It exports an allowlist of counts, booleans and known statuses, excluding paths, hashes, names, IDs and raw errors. Never upload the snapshot directory. No telemetry or network access is built into the scripts.
