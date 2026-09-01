# Requirements

Status: Approved
Phase: Analysis

Notation: *When `<trigger>`, the system shall `<response>`.* Each requirement carries an ID used by tasks and tests.

## Student management

**REQ-001** When a user submits a student registration, the system shall reject any identity document whose control letter does not match the modulo 23 checksum for a Spanish `DNI` or `NIE`.

A student is a natural person, so corporate `NIF` is out of scope. Shape alone is not sufficient: `12345678A` has valid shape and an invalid checksum, and must be rejected. See ADR-0005.

**REQ-002** When a student is registered, the system shall persist their assigned licence package and instructor.

**REQ-003** When a practical lesson is recorded, the system shall increase that student's completed lesson count by one and attribute it to the instructor who delivered it.

**REQ-004** When a DGT exam appointment is registered (DGT is the Spanish traffic authority), the system shall store its date against the student.

## Billing

**REQ-005** When an invoice is calculated, the system shall charge only the lessons exceeding the package allowance, and shall not charge for lessons within it.

**REQ-006** When an invoice is calculated, the system shall subtract any advance payment already made by the student from the amount due.

**REQ-007** When an invoice is calculated, the system shall present the taxable base, the `IVA` amount at 21 percent, and the gross total as separate figures.

**REQ-008** When an invoice total is computed, the system shall round each amount to two decimal places, breaking ties away from zero, and the stated total shall equal the sum of its parts exactly, with no tolerance. See ADR-0004.

**REQ-009** When a user requests an invoice document, the system shall generate the PDF in memory and stream it to the browser without writing any file to disk.

**REQ-014** When a student has paid more than the invoice total, the system shall report a negative pending balance rather than clamping it to zero, since the difference is money owed back to the student.

## Dashboard

**REQ-010** When the dashboard is opened, the system shall display projected gross revenue, collected `IVA`, outstanding balance, and the distribution of students by licence type.

**REQ-011** The dashboard shall be read-only. It shall not modify persisted data.

## Data lifecycle

**REQ-012** When the application starts against an empty database, the system shall seed fictional demonstration records.

**REQ-013** The system shall never persist, log or seed real personal data.
