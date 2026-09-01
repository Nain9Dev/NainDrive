# ADR-0003 — The presentation layer must not reach persistence

Status: Proposed
Date: 2026-08-30

## Context

`src/ui/app.py` instantiates `SQLiteRepository` and passes it into every rendering function. `src/ui/components.py` imports the repository, the domain models and the services together, and is 383 lines long, larger than any other module.

The README documents `UI --> REPO` in its architecture diagram, presenting the violation as if it were the intended design. The docstring in `app.py` describes the module as a "dumb renderer" while it does the opposite.

Consequences observed today:

- Business figures are prepared inside rendering code, so they cannot be tested without a UI runtime.
- The same calculation can drift between the dashboard and the invoice, because neither goes through a single service.
- Replacing Streamlit would require rewriting business logic, not just the views.

## Decision

Introduce an application service that exposes every read and write the interface needs, and forbid `src/ui/` from importing `src/repository/`.

The presentation layer receives plain data structures. It renders, formats and captures input. Nothing else.

## Consequences

- Business figures become testable without Streamlit.
- One extra layer to maintain, and a mechanical refactor of `components.py`.
- The architecture diagram in the README becomes accurate rather than aspirational.

## Rejected alternatives

- **Leave it and document it.** Cheapest, but the codebase is a portfolio piece: an architecture that contradicts its own diagram is worse than no diagram.
- **Rewrite as FastAPI plus a separate frontend.** Correct long-term, out of proportion today. Covered by ADR-0002.

## Reconsider when

Never for the boundary itself. The implementation may change; the rule does not.
