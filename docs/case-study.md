# A real recovery, with its limits

After an interruption and restart, a Windows Codex Desktop installation showed no local projects in its sidebar. Reopening the app and waiting did not resolve the symptom.

Investigation distinguished retained project records in SQLite from missing sidebar metadata. An initial helper stopped with its parent app; a later independent worker also revealed that closing the window did not close every writer. The final private executor verified ownership, used explicitly authorized scoped closure and guarded the repair with backups and state checks.

The executor reconstructed **39 projects and 173 chat associations** using current records. Only the project catalog, project order and chat-to-project association fields were changed. Post-write checks reported database files, migration flags and unrelated settings unchanged. The user then confirmed that recovery worked.

Observed application version: **Windows Codex Desktop 26.1002.7124.0**. One successful incident demonstrates feasibility, not reliability across versions or operating systems. Exhaustive verification of ordering and representative associations was not separately documented. No claim is made that the outage was the physical cause of corruption.

The private incident executor and snapshots are not distributed. The public skill supplies diagnosis, guarded candidate preparation and guidance for a reviewed version-specific live executor.
