# Project charter

Status: Approved
Phase: Planning

## Purpose

A management and billing platform for driving schools, built as a commercial and technical showcase of deterministic backend design in Python.

## Why it exists

One goal: **portfolio**. Demonstrate deterministic financial calculation, verifiable
validation and disciplined layering to prospective clients and employers.

It is not a product and is not being sold. That decision is what closes the open
questions in `11-open-questions.md`: without a real client there is no way to answer
them, and answering them is not needed to demonstrate the engineering.

The driving school is the setting, not the subject. What is on display is the billing
engine: exact arithmetic, checksum-verified identity, and totals that reconcile without
tolerance.

## In scope

- Student registration with Spanish identity document validation.
- Practical lesson tracking per instructor.
- DGT exam appointment records.
- Invoice calculation: package lessons versus extra lessons, less advance payments.
- `IVA` breakdown at 21 percent (Spanish value-added tax).
- Invoice PDF generated in memory, never written to disk.
- Read-only executive dashboard.

## Out of scope

- Multi-tenant isolation. Single driving school per deployment.
- Authentication and user roles.
- Payment processing.
- Fleet telemetry or vehicle maintenance.
- Refunds and mid-package cancellation. See Q-002.
- Legally valid invoicing: no invoice series, issuer details or retention. See Q-003.
- Integration with any official DGT system.

## Constraints

- Zero infrastructure cost. Must run on a free tier.
- No third-party database server.
- No real personal data at any point, including demo seeds.

## Success criteria

- Every financial requirement covered by a passing test.
- A public demo URL reachable without credentials.
- No layer boundary violation in the codebase.
