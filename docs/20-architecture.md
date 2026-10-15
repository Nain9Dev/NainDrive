# Architecture

Status: Approved
Phase: Design

## Layers

Dependencies point inward. The domain depends on nothing.

```mermaid
graph TD
    CLIENT[Decoupled Client - Vue 3 + TS :5379] --> API[API Gateway - FastAPI :8150]
    UI[Legacy Presentation - Streamlit :8151] --> SVC[Services - DrivingSchoolService]
    API --> SVC
    SVC --> DOM[Domain - entities, money, identity]
    SVC --> REPO[Repository - SQLAlchemy over SQLite]
    REPO --> DOM
    SVC --> PDF[PDF generation - in memory ReportLab]

    style DOM fill:#182B49,stroke:#fff,stroke-width:2px,color:#fff
    style CLIENT fill:#10B981,stroke:#fff,stroke-width:2px,color:#fff
    style API fill:#0284C7,stroke:#fff,stroke-width:2px,color:#fff
    style UI fill:#64748B,stroke:#fff,stroke-width:2px,color:#fff
    style SVC fill:#8B5CF6,stroke:#fff,stroke-width:2px,color:#fff
```

## Layer contracts

| Layer | Path | May depend on | Must never |
| :--- | :--- | :--- | :--- |
| Client | `NainDrive.Client/` | FastAPI REST Gateway (`/api/v1`) | Direct database access |
| API Gateway | `src/api/` | Services, Domain | Import repository directly |
| Legacy UI | `src/ui/` | Services | Import the repository, calculate figures, enforce domain rules |
| Services | `src/services/` | Domain, Repository | Import presentation concerns (FastAPI or Streamlit) |
| Domain | `src/domain/` | Nothing | Import any other layer |
| Repository | `src/repository/` | Domain | Contain business rules |

## Boundary Debt Resolution (ADR-0003 & ADR-0006)

The architectural debt identified in ADR-0003 (`UI --> REPO` direct access) has been completely resolved:
- `DrivingSchoolService` was introduced in `src/services/driving_school_service.py`.
- All repository calls were removed from `src/ui/app.py` and `src/ui/components.py`.
- `src/ui/components.py` was refactored from 383 lines down to 195 lines, acting as a pure renderer.
- `src/api/main.py` provides a REST API gateway on port `8150`, documented with Scalar at `/docs`.
- `NainDrive.Client` provides a decoupled, accessible Vue 3 + TypeScript client on port `5379`.

## Deliberate simplicity

Single process, single SQLite file, no cloud bill. This respects the zero-cost constraint of the charter while providing full decoupling and headless API readiness.
