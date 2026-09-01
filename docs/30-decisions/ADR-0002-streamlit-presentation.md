# ADR-0002 — Streamlit as the presentation layer

Status: Approved
Date: 2026-08-02

## Context

The project needs a visual interface fast, deployable for free, and written in the same language as the backend so it stays a single-stack showcase.

## Decision

Use Streamlit for presentation, deployed on Streamlit Community Cloud.

## Consequences

- One language across the stack, no separate frontend build.
- Free public hosting tied to the GitHub repository.
- Streamlit re-runs the whole script on every interaction, which pushes developers toward putting data access inside rendering functions. This is the direct cause of the deviation recorded in ADR-0003, and it needs active discipline rather than a one-off fix.
- No control over markup or accessibility. Not suitable if the product is ever sold to end clients.

## Rejected alternatives

- **FastAPI plus React.** Matches the target architecture better and matches the owner's professional profile, but doubles the surface for a demonstration project and needs two deployments.

## Reconsider when

The project stops being a showcase and acquires a paying user, or when the interface becomes a selling point rather than a viewer.
