# ADR-0001 — SQLite as the only persistence engine

Status: Approved
Date: 2026-08-02

## Context

The charter fixes a zero infrastructure cost constraint. The project must run on a free tier and be demonstrable from a public URL without provisioning a database server.

## Decision

Use SQLite through SQLAlchemy 2.0, as a single file created on first run.

## Consequences

- No hosting cost, no connection configuration, no external dependency.
- Concurrent writes are effectively serialised. Acceptable for a single driving school; not acceptable for multi-tenant use.
- No managed backup. The demonstration data is disposable by design.

## Rejected alternatives

- **PostgreSQL on a free tier.** More realistic, but free tiers expire or sleep, which breaks a portfolio demo that must be reachable at any time.
- **In-memory only.** Loses state between sessions, which makes the dashboard meaningless.

## Reconsider when

Real client data is stored, or more than one driving school shares a deployment.
