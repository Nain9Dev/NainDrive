# Open questions

Status: Resolved
Phase: Analysis

The charter fixes this project as a portfolio piece, not a product to be sold. That
decision closes all four questions: none of them can be answered without a real client,
and none of them needs to be answered to demonstrate the engineering.

What matters is that the limitation is stated rather than hidden.

## Q-001 — Is the 21 percent `IVA` rate fixed?

**Closed as documented limitation.** Driving school tuition may qualify for a reduced or
exempt rate depending on the licence type and the training's official status. The
implementation applies 21 percent through a single named constant,
`STANDARD_VAT_RATE`, so the rate is one edit away from being configurable when a real
rate is confirmed. Not confirming it does not weaken the demonstration; claiming it were
confirmed would.

## Q-002 — What happens when a student cancels mid-package?

**Closed as out of scope.** Recorded in the charter's exclusions. Refund and proration
rules are business policy, and inventing one would be inventing a requirement.

## Q-003 — Is the invoice a legally valid document?

**Closed: no, and it says so.** The generated PDF has no sequential invoice series, no
issuer tax details and no retention policy. It is a commercial mock-up. The README states
this explicitly so no reader assumes otherwise.

## Q-004 — Who is the buyer?

**Closed as not applicable.** The project is a portfolio piece. The audience is a
technical reviewer or a prospective client evaluating engineering practice, not a driving
school. If it is ever revisited as a product, this question reopens first.
