# Activation and acceptance inventory

These are review scenarios, not a claim that model activation evaluations have already passed.

| Request | Expected behavior |
| --- | --- |
| My Codex projects disappeared after a restart | Diagnose selected local profile; compare SQL and cache |
| The Projects sidebar is empty but my chats remain | Distinguish local from cloud; inspect current evidence |
| Can you recover the missing project list? | Read-only snapshot first; reviewed candidate only if supported |
| Run recovery on another profile | Resolve which profile before collecting or mutating it |
| Close Codex yourself and repair the index | Use scoped authorized closure only with a reviewed executor; retain writer checks |
| I deleted my source code | Do not route this to index reconstruction as file recovery |
| Move Codex to a new computer | Use a migration workflow instead |
| Create a new project | Ordinary project creation; no recovery scan |
| Candidate encounters pending deletions | Block and report; do not resurrect deleted projects |
| App writes while copying | Reject unstable snapshot; inspect blockers and use fresh offline evidence |

For live acceptance, distinguish application-state validation from user-visible confirmation. Check sidebar entries, ordering and representative associations after reopening. Never equate candidate preparation with successful recovery.
