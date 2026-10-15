# Tasks

Status: Active
Phase: Development

One task at a time, test first. A task is done only when its `Done when` criterion has
actually been verified.

Labels: `[A]` agent alone · `[M]` mixed, needs a human action · `[H]` human only.

## Done

- [x] **T-001** `[A]` Introduce an application service layer and remove repository imports from `src/ui/`
      Implements: ADR-0003
      Verified: Created `src/services/driving_school_service.py` (`DrivingSchoolService`).
      `grep -r "from src.repository" src/ui/` returns 0 matches. All business orchestration
      and queries flow strictly through the service layer.

- [x] **T-002** `[A]` Move figure preparation out of `src/ui/components.py` into the service layer
      Depends on: T-001
      Verified: `src/ui/components.py` refactored to 195 lines (< 200 lines criterion), contains
      zero financial arithmetic or repository imports.

- [x] **T-003** `[A]` Correct the architecture diagram in `README.md`
      Depends on: T-001
      Verified: The diagram no longer shows an edge from the UI to the repository. The service
      layer isolates persistence completely.

- [x] **T-012** `[A]` Validate identity documents by modulo 23 checksum
      Implements: REQ-001 · ADR-0005
      Verified: 26 tests in `tests/test_identity_validation.py`. `12345678A` and `AAAAA`
      are now rejected; both were accepted before. Two seeded students and five test
      fixtures carried invalid documents and were corrected.

- [x] **T-013** `[A]` Move all monetary values from `float` to `Decimal`
      Implements: REQ-008, REQ-014 · ADR-0004
      Verified: 5 tests in `tests/test_monetary_precision.py`. The five-cent tolerance in
      `verify_financial_consistency` is removed; totals reconcile exactly. Tax on a
      350.50 base is now 73.61, was 73.60.

- [x] **T-014** `[A]` Cover the in-memory PDF path with a test
      Implements: REQ-009
      Verified: Covered in `tests/test_service_layer.py::test_in_memory_pdf_generation_returns_bytes_without_disk_writes`
      and `tests/test_api_endpoints.py::test_invoice_calculation_and_pdf`. Confirmed bytes returned with zero disk writes.

- [x] **T-015** `[A]` Cover DGT exam appointment storage
      Implements: REQ-004
      Verified: Covered in `tests/test_service_layer.py::test_dgt_exam_appointment_storage_and_retrieval`
      and `tests/test_api_endpoints.py::test_dgt_appointments_endpoints`. Both theoretical and practical appointments
      persist and retrieve with complete student isolation.

- [x] **T-016** `[A]` Expose decoupled FastAPI REST API Gateway on port 8150
      Implements: ADR-0006, REQ-001..REQ-012
      Verified: Created `src/api/main.py` with 7 endpoint tests in `tests/test_api_endpoints.py`,
      CORS enabled for port 5379 and `drive.naindev.com`, and Scalar OpenAPI documentation at `/docs`.

- [x] **T-017** `[A]` Decoupled Vue 3 + TypeScript SPA Client (`NainDrive.Client`) on port 5379
      Implements: ADR-0006
      Verified: Built client in `NainDrive.Client/` with dark luxury theme, full TypeScript contracts,
      reactive KPI dashboard, student lifecycle management, DGT appointment scheduling, and 1-click in-memory PDF download.
      `npm run build` succeeds with 0 errors and 0 warnings.

- [x] **T-004** `[A]` Regression test for rounding across line items
      Superseded by T-013, which covers it with a stricter invariant.

- [x] **T-010** `[M]` Reframe the README around deterministic billing
      Agent: rewritten in English, leading with the billing engine, modern dual runtime, and NainDev architecture.

## Closed by the portfolio scope decision

- [x] **T-005** `[H]` Applicable `IVA` rate per licence type
      Closed as a documented limitation. The rate lives in one named constant,
      `STANDARD_VAT_RATE`, one edit away from configurable. See Q-001.

- [x] **T-006** `[A]` Make the tax rate configurable
      Not needed while the rate is unconfirmed. Extracting the constant was enough.

- [x] **T-007** `[H]` Cancellation and refund rule
      Out of scope, recorded in the charter exclusions. See Q-002.

- [x] **T-011** `[H]` Talk to driving school owners
      Not applicable to a portfolio piece. Reopens if this ever becomes a product. See Q-004.

## Open

- [ ] **T-008** `[A]` Schema migrations
      No longer blocking: the charter fixes this as a portfolio piece with disposable
      data. Reopens the moment any real data is stored.

- [ ] **T-009** `[M]` Publish the public demo on Streamlit Community Cloud / Vercel
      Agent: entry point prepared, dependencies pinned, ports allocated in `dev-ports.json`.
      Human: signs in with GitHub, authorises the repository, triggers the deploy.
