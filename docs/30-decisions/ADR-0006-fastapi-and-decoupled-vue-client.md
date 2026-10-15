# ADR-0006 — Decoupled FastAPI Gateway and Vue 3 Showcase Client

Status: Proposed
Date: 2026-10-15

## Context

`Gestion-Autoescuela-Python` was initially created with Streamlit as its presentation layer (ADR-0002). While Streamlit enabled rapid prototyping, it exhibited structural limitations:
1. Re-running the entire Python script on every user interaction encouraged data access and arithmetic within rendering code, violating architectural boundaries (ADR-0003).
2. It lacks fine-grained control over markup, WCAG 2.2 AA accessibility, responsive UX, and modern visual design.
3. The broader NainDev portfolio standard (`naindev.com`) features decoupled single-page applications built with Vue 3 + TypeScript, dark glassmorphic styling, and standardized REST API gateways documented via OpenAPI and Scalar.

## Decision

1. Extract an authoritative application service layer (`src/services/driving_school_service.py`) that encapsulates all business orchestration, KPI calculations, and transaction coordination.
2. Build an asynchronous REST API gateway using **FastAPI** (`src/api/`) on port `8150`, exposing clean typed endpoints and interactive documentation at `/docs` using Scalar.
3. Build a decoupled showcase client in **Vue 3 + TypeScript** (`NainDrive.Client/`) pinned to port `5379`, branded commercially as **NainDrive**.
4. Maintain Streamlit (`src/ui/app.py`) on secondary port `8151` refactored to consume the new `DrivingSchoolService` without touching persistence directly, preserving compatibility for zero-dependency local runs.

## Consequences

- The presentation layers (`src/ui/` and `NainDrive.Client`) are strictly decoupled from the database repository.
- Business and financial logic become 100% testable via pytest without rendering runtimes.
- Endpoints are self-documenting via OpenAPI 3.0 and Scalar, aligning with NainDev portfolio conventions.
- Port allocations are managed strictly through `D:/Development/Tools/dev-ports.json` (5379 for client, 8150 for API).

## Rejected Alternatives

- **Replace Streamlit entirely and delete it**: Keeping Streamlit on port 8151 allows existing runbooks and Streamlit Community Cloud deployments to remain functional as secondary administrative tooling.
- **Direct database access from FastAPI endpoints**: Rejected because it would replicate the boundary violation that ADR-0003 addresses.
