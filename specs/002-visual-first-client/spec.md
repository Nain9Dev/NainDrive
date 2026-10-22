# Spec 002 — Visual-first client shell

Status: Active
Scope: `NainDrive.Client/` only. No API, service, domain or repository change.

## Problem

The public demo at `drive.naindev.com` renders every entity as a dense table with long
Spanish captions. The sticky header overlaps the ecosystem bar, the dashboard is a wall
of labels, and the only way to act on a student is a row of five text buttons.

## Requirements (EARS)

- **UI-001** When the client loads, the shell shall render a persistent navigation rail
  with four destinations (Panel, Alumnos, Exámenes, Flota), each identified by an icon
  and a one-word label, and shall keep the ecosystem bar fully visible.
- **UI-002** When the dashboard is shown, the system shall present revenue, `IVA`,
  outstanding balance and lessons as four stat tiles, the licence distribution as a
  donut, the outstanding share as a bar, and the next scheduled exams as a short agenda,
  using only figures returned by the API.
- **UI-003** When the students view is shown, each student shall be a card with initials,
  licence colour, a lesson progress ring (completed against the package allowance), exam
  pips, advances paid, and icon actions for lesson, payment, exam and invoice.
- **UI-004** When a student card is opened, a side drawer shall show the invoice breakdown
  returned by `/students/{dni}/invoice` and offer the in-memory PDF download.
- **UI-005** When the exams view is shown, appointments shall be grouped by month in a
  timeline, with status and type as colour chips, filterable by status.
- **UI-006** When the fleet view is shown, each instructor shall be a card with a styled
  Spanish plate, an ITV validity gauge, and fuel total; tariffs shall be three package
  cards.
- **UI-007** When any action succeeds or fails, feedback shall be a non-blocking toast,
  never `alert()`.
- **UI-008** The layout shall work from 360 px width upwards, with the rail collapsing
  to a bottom bar, and every icon-only control shall carry an accessible name.
- **UI-009** The presentation layer shall not compute business figures. Ratios used for
  rings and bars are display proportions of API-returned values only.

## Non-goals

- New endpoints, new fields, or changes to the mock store's arithmetic.
- New runtime dependencies (charts are inline SVG).
- Authentication, routing library, state library.

## Handoff

- Done: shell, dashboard, students, drawer, exams, fleet, toasts, responsive, build.
- Verified: `npm run build` clean; views checked in the browser at desktop and mobile widths.
- Next: none in scope. Deploy happens through the existing Pages workflow on push.
