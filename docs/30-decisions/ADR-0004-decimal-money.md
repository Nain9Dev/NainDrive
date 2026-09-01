# ADR-0004 — Money is Decimal, never float

Status: Approved
Date: 2026-08-30

## Context

Every monetary field was a `float`, and every calculation went through Python's built-in
`round`. Two defects followed from that, and both were live:

1. **Wrong rounding mode.** `round` breaks ties toward the even digit. Invoicing rounds
   ties away from zero. On a taxable base of 350.50 the tax is exactly 73.605: the code
   produced 73.60, the correct figure is 73.61.
2. **Binary representation error.** Most decimal amounts have no exact binary form, so
   sums drifted. The domain masked this with a tolerance of five cents in
   `InvoiceCalculation.verify_financial_consistency`, which meant the model accepted an
   invoice whose parts did not add up to its total.

A tolerance on a financial invariant is not a safeguard. It is a declaration that the
arithmetic is untrusted.

## Decision

All monetary values are `Decimal`, quantised to two places with `ROUND_HALF_UP`, through
a single module: `src/domain/money.py`.

The consistency validator now requires exact equality, both for the taxable base and for
the total. The five-cent tolerance is removed.

Floats are still accepted at the boundary and converted through their string form, so
callers that read a number from a form or a database do not need to change.

## Consequences

- The stated total always equals the sum of its parts, verified without tolerance.
- Comparisons in tests must use `Decimal`, since `Decimal("113.40") != 113.4`.
- Any new arithmetic must go through `money.py` or it reintroduces the drift.
- Slight performance cost, irrelevant at this scale.

## Rejected alternatives

- **Integer cents.** Immune to representation error and common in payment systems, but
  every read and write needs conversion, and the tax rate multiplication still needs a
  rounding policy. More invasive for the same guarantee.
- **Keep floats, widen the tolerance.** Hides the defect and makes the invoice legally
  meaningless.

## Reconsider when

Multi-currency support arrives, where a currency with a different minor unit would make
the fixed two-place quantisation wrong.
