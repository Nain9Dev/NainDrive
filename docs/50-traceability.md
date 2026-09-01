# Traceability

Status: Active
Phase: Testing

Each requirement maps to the test that proves it. A requirement with no test is not done,
whatever the code says.

| Requirement | Test | Status |
| :--- | :--- | :--- |
| REQ-001 identity checksum | `tests/test_identity_validation.py` | Covered, 26 cases |
| REQ-002 package and instructor assignment | `tests/test_repository.py` | Covered |
| REQ-003 lesson count attribution | `tests/test_repository.py` | Partial: the count is tested, instructor attribution is not |
| REQ-004 DGT appointment storage | none | **Not covered** — T-015 |
| REQ-005 package versus extra lessons | `tests/test_billing_calculations.py` | Covered |
| REQ-006 advance payment subtraction | `tests/test_billing_calculations.py` | Covered |
| REQ-007 `IVA` breakdown | `tests/test_billing_calculations.py` | Covered at 21 percent; rate limitation documented in Q-001 |
| REQ-008 rounding and exact reconciliation | `tests/test_monetary_precision.py` | Covered, including the half-cent boundary |
| REQ-009 in-memory PDF generation | none | **Not covered** — T-014 |
| REQ-010 dashboard figures | none | **Not covered** — blocked by T-001 |
| REQ-011 dashboard is read-only | none | **Not covered** — blocked by T-001 |
| REQ-012 demo seeding | `tests/test_repository.py` | Covered |
| REQ-013 no real personal data | none | Enforced by review, not by test |
| REQ-014 overpayment yields a credit | `tests/test_monetary_precision.py` | Covered |

## Summary

43 tests passing, 9 of 14 requirements covered. Was 12 tests and 7 of 13.

The remaining gap is concentrated in the presentation and PDF paths. Two of the five
uncovered requirements are blocked by ADR-0003: logic that lives inside rendering code
cannot be tested without a UI runtime. T-001 unblocks them.
