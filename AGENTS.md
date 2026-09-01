# Project constitution

Driving school management and billing platform. Python 3.12, Clean Architecture, Streamlit presentation, SQLite persistence.

This file is the operational contract for any AI agent working on this repository. Read `docs/README.md` before proposing anything.

## Authority

- `docs/` is the canonical source of truth. Code that contradicts an `Approved` document is a defect, not a decision.
- Only the owner approves a decision. An agent may draft one as `Proposed`; never record it as `Approved`.
- A document marked `Superseded` or `Draft` never drives an implementation.

## Non-negotiable architecture

Layer boundaries, strictest first:

1. **Presentation** (`src/ui/`) renders and captures input. It must not calculate business figures, enforce domain rules, or reach persistence.
2. **Services** (`src/services/`) hold business logic and orchestration. This is the only layer the presentation may call.
3. **Domain** (`src/domain/`) holds entities, invariants and validation. It depends on nothing.
4. **Repository** (`src/repository/`) is the only layer that touches the database.

The presentation layer must never import from `src/repository/`. See ADR-0003.

## Stack

Locked unless an approved ADR says otherwise: Python 3.12, Pydantic v2, SQLAlchemy 2.0, Streamlit, FPDF2, pytest.

Do not introduce frameworks, services or dependencies as a side effect of another task.

## Working rules

- Smallest correct change. No unrelated refactors.
- One task at a time, from `docs/40-tasks.md`. Test first.
- A task is done only when its `Done when` criterion is verifiable and verified.
- Stop and ask when a `[M]` or `[H]` task blocks progress. Never fake a credential or silently mock an external dependency.
- Never write real personal data into fixtures, tests or seed data.

## Language

Everything in this repository is written in English: code, identifiers, folder and file names, branches, commit messages, comments, docstrings, documentation and tests.

Two exceptions:
- End-user facing strings use the product locale (Spanish for this product).
- Spanish legal and tax terms with no exact English equivalent (`IVA`, `DNI`, `NIF`, `NIE`, `DGT`) keep their original form as values or constants, with an English comment explaining them.

## Commits

Conventional Commits, subject in English: `<type>(<scope>): <description>`.
Contract breaks use `!`. No dates in the message. Never commit or push unless explicitly asked.
