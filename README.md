# Codex Project Index Recovery

**Projects vanished from your Codex Desktop sidebar after a crash or restart? Diagnose the index before recreating anything.**

A local agent skill with a read-only diagnostic helper, reviewed candidate generation and an explicit recovery workflow. Community beta; independent of OpenAI. No directory approval is claimed.

## What it does

- Captures a stable private JSON/SQLite snapshot without modifying application state.
- Checks database integrity and compares the project catalog with sidebar metadata.
- Prepares a candidate only for a compatible legacy schema and empty recovery fields.
- Preserves unrelated settings and blocks deletion or association conflicts.
- Exports aggregate summaries without project names, paths, hashes or conversation IDs.

**The public scripts do not apply a live repair or close applications.** A live repair requires a reviewed executor adapted to the installed version, authorization, a fresh offline snapshot and verification. This is not deleted-file recovery.

## Install the skill

Requires a local Codex session with filesystem access and Python 3.11+. Download or clone this repository, review the source, and copy `skills/codex-project-index-recovery` into your personal skills directory (`$CODEX_HOME/skills`, or `~/.codex/skills` when unset). Reload Codex to discover it.

Invoke:

> Use $codex-project-index-recovery. My local projects disappeared from the Codex Desktop sidebar after a restart. Diagnose first and show me a recovery plan.

The root `plugin.json` also packages the skill as a portable plugin. Public-directory submission requires separate developer verification, scan and review; this repository is not evidence of acceptance.

## Verified case and compatibility

The workflow was developed through a real Windows incident on Codex Desktop **26.1002.7124.0**. A separate, private, version-specific executor reconstructed the index; the user confirmed recovery worked. That incident is not proof of universal compatibility. See [the sanitized case](docs/case-study.md).

Candidate generation checks the observed `state_5.sqlite` schema at runtime. Unknown layouts, a damaged database, nonempty caches and unresolved deletion metadata block automated candidate generation. macOS and Linux live recovery have not been verified.

## Privacy

No telemetry, network calls or account credentials are required by the scripts. The diagnostic **creates a sensitive local snapshot**, including application state. Keep it private. Do not attach databases, candidates, raw logs or your `.codex` folder to public issues. Read [PRIVACY.md](PRIVACY.md) before sharing evidence.

## Test and contribute

Run `python -m unittest discover -s tests -v`. Tests use synthetic state only. Report a redacted symptom, OS, app version, Python version and reviewed aggregate summary; never attach raw state. Contributions should preserve fail-closed schema checks, current deletion state and the no-live-write diagnostic boundary.

Licensed under MIT. OpenAI and Codex are trademarks of their respective owners; this is an independent community project.
