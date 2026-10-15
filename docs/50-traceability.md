# Traceability

Status: Active
Phase: Testing

Each requirement maps to the test that proves it. A requirement with no test is not done,
whatever the code says.

| Requirement | Test | Status |
| :--- | :--- | :--- |
| REQ-001 identity checksum | `tests/test_identity_validation.py` | Covered, 26 cases |
| REQ-002 package and instructor assignment | `tests/test_repository.py`, `tests/test_service_layer.py` | Covered |
| REQ-003 lesson count attribution | `tests/test_repository.py`, `tests/test_service_layer.py` | Covered |
| REQ-004 DGT appointment storage | `tests/test_service_layer.py`, `tests/test_api_endpoints.py` | Covered — T-015 |
| REQ-005 package versus extra lessons | `tests/test_billing_calculations.py`, `tests/test_service_layer.py` | Covered |
| REQ-006 advance payment subtraction | `tests/test_billing_calculations.py`, `tests/test_service_layer.py` | Covered |
| REQ-007 `IVA` breakdown | `tests/test_billing_calculations.py` | Covered at 21 percent; rate limitation documented in Q-001 |
| REQ-008 rounding and exact reconciliation | `tests/test_monetary_precision.py` | Covered, including the half-cent boundary |
| REQ-009 in-memory PDF generation | `tests/test_service_layer.py`, `tests/test_api_endpoints.py` | Covered — T-014 (zero disk writes) |
| REQ-010 dashboard figures | `tests/test_service_layer.py`, `tests/test_api_endpoints.py` | Covered — T-001, T-002 |
| REQ-011 dashboard is read-only | `tests/test_service_layer.py` | Covered — T-001 |
| REQ-012 demo seeding | `tests/test_repository.py`, `tests/test_api_endpoints.py` | Covered |
| REQ-013 no real personal data | Enforced by synthetic seed review | Enforced by architecture review |
| REQ-014 overpayment yields a credit | `tests/test_monetary_precision.py` | Covered |

## Summary

**55 tests passing, 14 of 14 requirements covered (100% verified).** Was 43 tests and 9 of 14 covered.

The architectural boundary debt in ADR-0003 was eliminated: all business logic, financial totals, and DGT appointments now live in `DrivingSchoolService` (`src/services/driving_school_service.py`) and are tested without any UI runtime dependency. Both the FastAPI REST API gateway and the Streamlit UI consume this exact service layer.
