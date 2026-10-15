# Security Policy

## 1. Data Protection & Fictional Data Guarantees
- **No Real Personal Identifiable Information (PII)**: All seeded and test fixture profiles use fictional names, synthetic DNI/NIEs with valid control letters, and non-routable placeholder contact numbers (`600000000`).
- **In-Memory Document Generation**: Official invoice documents are created entirely in memory via `fpdf2` and returned as byte streams directly to the HTTP response, preventing sensitive billing data from lingering on persistent storage or shared temporary directories.

## 2. Input Validation & Identity Integrity
- **Spanish Identity Card Checksum**: Natural person registration strictly validates DNI and NIE documents using the official Modulo 23 algorithm. Arbitrary alphanumeric inputs and forged checksums are rejected before reaching business logic or database persistence.
- **Strict Pydantic v2 Models**: All inbound API payloads and domain state transitions are bounded by Pydantic validators, enforcing non-negative lesson counts, positive monetary deposits, and exact string boundaries.

## 3. Financial Determinism
- **Decimal Accounting**: Every financial operation utilizes `Decimal` with explicit half-up rounding (`ROUND_HALF_UP`), eliminating floating-point drift.
- **Invariant Enforcement**: Invoices are self-reconciling; any mismatch between the itemized subtotal, VAT amount, and the stated total causes an immediate domain validation failure.

## 4. Reporting Security Vulnerabilities
If you discover a potential security vulnerability within this repository, please report it via private security advisory or contact `security@naindev.com`.
