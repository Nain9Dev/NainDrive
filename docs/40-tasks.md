# Tasks

Status: Active
Phase: Development

One task at a time, test first. A task is done only when its `Done when` criterion has
actually been verified.

Labels: `[A]` agent alone · `[M]` mixed, needs a human action · `[H]` human only.

## Done

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

- [x] **T-004** `[A]` Regression test for rounding across line items
      Superseded by T-013, which covers it with a stricter invariant.

- [x] **T-010** `[M]` Reframe the README around deterministic billing
      Agent: rewritten in English, leading with the billing engine and stating the
      mock-up limitation explicitly.
      Human: your approval of the commercial angle is still pending.

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

- [ ] **T-001** `[A]` Introduce an application service layer and remove repository imports from `src/ui/`
      Implements: ADR-0003
      Done when: `grep -r "from src.repository" src/ui/` returns nothing and the suite passes
      Unblocks: T-002, T-003, and REQ-010 and REQ-011 in the traceability table
      This is now the single largest gap. Three requirements cannot be tested until the
      logic leaves the rendering layer.

- [ ] **T-002** `[A]` Move figure preparation out of `src/ui/components.py` into the service layer
      Depends on: T-001
      Done when: `components.py` is under 200 lines and holds no arithmetic on amounts

- [ ] **T-003** `[A]` Correct the architecture diagram in `README.md`
      Depends on: T-001
      Done when: the diagram no longer shows an edge from the UI to the repository

- [ ] **T-014** `[A]` Cover the in-memory PDF path with a test
      Implements: REQ-009
      Done when: a test asserts the generator returns bytes and writes nothing to disk

- [ ] **T-015** `[A]` Cover DGT exam appointment storage
      Implements: REQ-004

- [ ] **T-008** `[A]` Schema migrations
      No longer blocking: the charter fixes this as a portfolio piece with disposable
      data. Reopens the moment any real data is stored.

- [ ] **T-009** `[M]` Publish the public demo on Streamlit Community Cloud
      Agent: prepares the entry point, pins dependencies, verifies a clean install
      Human: signs in with GitHub, authorises the repository, triggers the deploy
      See: 41-blockers.md B-001
      Done when: the public URL loads the dashboard with seeded demo data
