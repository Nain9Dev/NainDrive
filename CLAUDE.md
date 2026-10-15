@AGENTS.md

## NainDrive Guidelines

- Read `docs/README.md` and `docs/40-tasks.md` before any change.
- Architecture: Clean Architecture with decoupled layers. The presentation layer (`src/ui/` or `NainDrive.Client`) must never import or touch `src/repository/`. All operations go through `DrivingSchoolService`.
- Ports allocated in `D:\Development\Tools\dev-ports.json`:
  - Frontend SPA: `5379` (`NainDrive.Client`)
  - FastAPI Gateway: `8150` (`src/api/main.py`)
  - Streamlit UI: `8151` (`src/ui/app.py`)
- Test verification: Run `.venv/Scripts/python -m pytest -v` before reporting any backend task as done.
- Frontend verification: Run `npm --prefix NainDrive.Client run build` before reporting any client task as done.
- Money precision: Always use `Decimal` with `ROUND_HALF_UP` from `src/domain/money.py`. Never cast to `float`.
- Identity validation: Use `src/domain/identity.py` for modulo 23 checksum calculation.
