# Data model

Status: Approved
Phase: Design

Entities are defined with Pydantic v2 in `src/domain/models.py` and persisted through SQLAlchemy 2.0 in `src/repository/sqlite_repository.py`.

## Entities

| Entity | Key fields | Invariants |
| :--- | :--- | :--- |
| `Student` | identity document, name, licence package, instructor, completed lessons, advance paid | Identity document passes the `DNI` or `NIE` modulo 23 checksum; completed lessons is never negative |
| `Instructor` | name, licence categories taught | Must teach at least one category |
| `LicensePackage` | licence type, included lessons, base price | Included lessons and price are non-negative |

## Persistence

- SQLite, single file, created on first run.
- Schema changes are applied by recreating the demonstration database. There is no migration tooling: acceptable while no real data exists, and a blocker before any real deployment. See T-008.
- Monetary values are `Decimal` throughout, quantised to two places with half-up rounding by `src/domain/money.py`. Never `float`. See ADR-0004.

## Data protection

Seed data is fictional by construction. No real identity document, name, address or contact detail is ever written, in any environment. See REQ-013.
