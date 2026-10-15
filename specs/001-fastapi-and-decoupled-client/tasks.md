# Tasks: NainDrive Implementation

- [ ] [A] Register client port `5379` and API port `8150` in `D:\Development\Tools\dev-ports.json`.
- [ ] [A] Define `DgtExamAppointment` model in `src/domain/models.py`.
- [ ] [A] Add DGT appointment table and CRUD operations in `src/repository/sqlite_repository.py`.
- [ ] [A] Create `DrivingSchoolService` in `src/services/driving_school_service.py` with figure preparation.
- [ ] [A] Refactor `src/ui/components.py` and `src/ui/app.py` to consume `DrivingSchoolService` and eliminate repository imports.
- [ ] [A] Implement automated unit tests in `tests/test_service_layer.py` for T-001, T-014, and T-015.
- [ ] [A] Build FastAPI REST API gateway in `src/api/main.py` with Scalar `/docs` documentation.
- [ ] [A] Implement API endpoint integration tests in `tests/test_api_endpoints.py`.
- [ ] [A] Scaffold and build decoupled Vue 3 + TypeScript client in `NainDrive.Client/` (port 5379).
- [ ] [A] Verify complete Python test suite and Vue client build.
- [ ] [A] Update `docs/40-tasks.md`, `docs/50-traceability.md`, `README.md`, `CLAUDE.md`, and `SECURITY.md`.
