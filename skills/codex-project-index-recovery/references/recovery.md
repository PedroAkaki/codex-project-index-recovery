# Recovery of a missing sidebar cache

The observed legacy Windows layout stores projects in `state_5.sqlite` and caches visibility in `.codex-global-state.json`. This is an internal, version-dependent layout, not a promised public API.

## Candidate scope

For a verified compatible schema, reconstruct only:

- `local-projects`: current SQL id, name, ordered root paths and millisecond timestamps.
- `thread-project-assignments`: current SQL local assignments, including archived chats. Preserve existing unrelated entries; a nonempty assignment map requires manual conflict review and is unsupported by the candidate helper.
- `project-order`: current SQL ordering.

Do not alter SQLite, migration flags, projectless classifications, pending deletions, remote mappings or `.bak`. Preserve projectless IDs when they are disjoint from current SQL assignments; reject conflicting classifications. Reject orphan roots/assignments, unexpected schema, existing nonempty target fields and unresolved pending deletions. If JSON is corrupt, retain the raw evidence; do not invent the unrelated settings. Recover a validated baseline with user review before proposing any merge.

## Live execution design

The diagnostic helper deliberately contains no live write mode. The agent must prepare a version-specific external runner after reviewing current evidence. Derive version and state guards from the current incident; never remove a guard merely to make an incompatible incident pass.

Before live repair, show the exact candidate diff, a fresh snapshot, rollback route and current app version. Obtain approval for the actual state change. Verify closed processes rather than trusting window closure. Use manual app exit by default; if the user explicitly authorizes automatic closure, follow the scoped opt-in closure procedure in `SKILL.md`. Block on any unclosed app-server/CLI writer. A persistent sandbox service may be exempted only by its current registered service name, executable path and PID; no blanket `codex*` exemption. Do not reopen the app automatically without user authorization.

Take a fresh offline snapshot and regenerate the candidate from it; an online diagnostic candidate is not ready for direct live installation. Check hashes of JSON, database and WAL/SHM immediately before replacement. Abort on any change, schema drift or unavailable process/version verification. Write a temporary JSON in the same directory, flush/fsync, parse and validate it, then atomically replace the target. Retain timestamped backups and a manifest outside the application directory. Check that database/WAL/SHM, unrelated JSON fields, migration flags and `.bak` are unchanged.

If post-write validation fails, keep the app closed and report the exact backup and failure. Recheck state and obtain appropriate authorization before rollback; do not overwrite concurrent changes. After success, the user reopens Codex and checks projects, order and sample chat associations. Offline success alone is insufficient for visual acceptance.

## Product prevention

For an upstream implementation, investigate durable writes, validated last-known-good generations, transactional project catalog storage, cache rebuild from authoritative state, migration idempotency, deletion preservation and restart fault injection. These are proposed improvements, not verified current product behavior. A plugin can orchestrate recovery; only app-level changes can address the internal persistence failure directly.
