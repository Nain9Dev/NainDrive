# Documentation map

Canonical documentation for this project. Numbered by lifecycle phase; each phase closes before the next opens.

| Phase | Document | Status |
| :--- | :--- | :--- |
| Planning | [00-charter.md](00-charter.md) | Draft |
| Analysis | [10-requirements.md](10-requirements.md) | Draft |
| Analysis | [11-open-questions.md](11-open-questions.md) | Open |
| Design | [20-architecture.md](20-architecture.md) | Draft |
| Design | [21-data-model.md](21-data-model.md) | Draft |
| Design | [30-decisions/](30-decisions/) | Draft |
| Development | [40-tasks.md](40-tasks.md) | Active |
| Development | [41-blockers.md](41-blockers.md) | Active |
| Testing | [50-traceability.md](50-traceability.md) | Active |
| Deployment | [60-runbook.md](60-runbook.md) | Draft |

## How to work here

1. Any change starts in the specification, never in the code.
2. Add or amend a requirement in `10-requirements.md`, with an ID.
3. Record a significant decision as an ADR under `30-decisions/`, status `Proposed`.
4. Break the work into tasks in `40-tasks.md`, each labelled `[A]`, `[M]` or `[H]`.
5. List every external dependency in `41-blockers.md` before writing code.
6. Implement one task at a time, test first.
7. Map each requirement to its test in `50-traceability.md`. A requirement with no test is not done.

## Task labels

| Label | Meaning |
| :--- | :--- |
| `[A]` | The agent completes it alone. |
| `[M]` | Mixed: the agent does its part but needs a human action to close it. |
| `[H]` | Human only: accounts, credentials, payments, terms, business decisions. |

If a `[M]` or `[H]` task is open and blocks progress, the agent stops and says so.
