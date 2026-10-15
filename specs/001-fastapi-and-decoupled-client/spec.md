# Specification: NainDrive Decoupled Architecture & FastAPI Gateway

Feature Branch: `main`
Status: Approved
Commercial Brand: **NainDrive** (`drive.naindev.com`)

## 1. Overview
NainDrive modernizes `Gestion-Autoescuela-Python` into an enterprise-grade driving school management and deterministic billing platform. The project introduces an application service layer resolving ADR-0003, exposes a typed FastAPI REST gateway on port `8150`, and delivers a decoupled Vue 3 + TypeScript client on port `5379` with a modern dark glassmorphic design system.

## 2. Requirements & Traced Tasks
- **REQ-001**: Identity documents must be verified using Spanish DNI/NIE modulo 23 checksum.
- **REQ-002**: Persist student registration with license package and assigned instructor.
- **REQ-003**: Lesson attribution and count increments.
- **REQ-004**: DGT exam appointment storage and retrieval (Tasks `T-015`).
- **REQ-005 - REQ-008**: Exact deterministic billing with `Decimal`, 21% IVA, and half-up rounding.
- **REQ-009**: In-memory PDF invoice generation without disk writes (Task `T-014`).
- **REQ-010**: Read-only KPI calculation for dashboard revenue, tax, and student distribution (Task `T-001`, `T-002`).
- **REQ-011**: Read-only dashboard integrity.
- **REQ-012**: Automated seeding of synthetic fictional profiles on empty database.
- **REQ-013**: Zero personal identifying information (PII) leakage.
- **REQ-014**: Negative pending balance preserved for student overpayments.

## 3. Port Allocation
- **Client (Vue 3 + TypeScript)**: Port `5379` (strictPort).
- **API Gateway (FastAPI)**: Port `8150` (`/docs` for Scalar OpenAPI).
- **Streamlit Admin**: Port `8151` (secondary internal console).
