# Implementation Plan: NainDrive Modernization

## Phase 1: Service Layer Extraction & ADR-0003 Resolution
1. Add `DgtExamAppointment` model to `src/domain/models.py`.
2. Add table and persistence operations for DGT appointments in `src/repository/sqlite_repository.py`.
3. Create `src/services/driving_school_service.py` (`DrivingSchoolService`):
   - Extract figure calculation (`get_kpi_dashboard_summary`).
   - Implement student progress, exam registration, and advance deposit orchestration.
   - Implement in-memory PDF export workflow.
4. Refactor `src/ui/components.py` and `src/ui/app.py` to consume `DrivingSchoolService` and remove direct repository imports (`T-001`, `T-002`).

## Phase 2: Comprehensive Test Coverage (T-001, T-002, T-014, T-015)
1. Create `tests/test_service_layer.py`:
   - Verify KPI summary calculations match deterministic expectations (REQ-010, REQ-011).
   - Verify in-memory PDF generator returns valid PDF bytes without writing files to disk (REQ-009, T-014).
   - Verify DGT exam appointment storage and retrieval (REQ-004, T-015).
2. Run pytest suite and confirm 100% pass rate.

## Phase 3: FastAPI Gateway (`src/api/`)
1. Create `src/api/main.py`:
   - FastAPI application instance with CORS for `localhost:5379` and `drive.naindev.com`.
   - Endpoints for dashboard KPIs, student management, invoice calculation, PDF download, and DGT appointments.
   - Interactive Scalar OpenAPI documentation mounted at `/docs`.
2. Create `tests/test_api_endpoints.py` testing the API via Starlette/FastAPI TestClient.

## Phase 4: Decoupled Vue 3 Showcase Client (`NainDrive.Client/`)
1. Scaffold Vue 3 + TypeScript project configured with Vite on port `5379`.
2. Implement dark glassmorphism CSS theme and typography (`Outfit`, `Inter`, `JetBrains Mono`).
3. Build components:
   - `HeaderNav.vue`: Branding, status indicator, OpenAPI link, portfolio link.
   - `DashboardKpis.vue`: Financial and operational metric cards.
   - `LicenseDistribution.vue`: Distribution of students by license type.
   - `StudentsManager.vue`: Student enrollment, lesson increment, advance payments.
   - `DgtAppointments.vue`: Exam scheduling and date tracking.
   - `InvoiceBillingModal.vue`: Calculation breakdown and 1-click in-memory PDF download.
   - `InstructorsFleet.vue`: Fleet vehicles, ITV expiration alerts, fuel expenses.
4. Verify client production build with `vue-tsc -b && vite build`.

## Phase 5: Documentation & Governance
1. Update `docs/40-tasks.md`, `docs/50-traceability.md`, and `README.md`.
2. Create `SECURITY.md` and update `CLAUDE.md`.
