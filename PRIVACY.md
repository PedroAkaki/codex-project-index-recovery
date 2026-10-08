# Privacy

The bundled Python scripts run locally and contain no telemetry or network client. They read the selected Codex profile and create a focused private snapshot outside it. That snapshot is not a full application backup.

Snapshot JSON, SQLite/WAL/SHM files, private analysis copies and recovery candidates may contain project names, filesystem paths, conversation records and identifiers. Do not publish these files, screenshots of private sidebars, raw incident plans or account credentials.

`share_summary.py` exports only explicitly allowed aggregate counts, booleans and known status strings. It does not copy file fingerprints, schemas, raw exception strings, names, paths or IDs. Review the summary before publication; counts may still be information you prefer to keep private. A regex scan alone is not a privacy guarantee.

Only synthetic test fixtures and a redacted case narrative are included in this repository. Issue reports and any files you choose to upload to GitHub are handled by GitHub; social posts by the relevant platform. The plugin itself does not collect those reports.

Keep backups needed for rollback. After recovery acceptance, remove unneeded private snapshots according to your own retention policy. The skill does not silently delete evidence.
