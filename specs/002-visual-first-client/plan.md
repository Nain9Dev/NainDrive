# Plan 002 — Visual-first client shell

## Structure

```
NainDrive.Client/src/
  App.vue                     shell: ecosystem offset, rail, topbar, view switch, drawer host
  style.css                   tokens, base, utilities (dark glass, aurora backdrop)
  store/driveData.ts          reactive client state + refresh (calls services/api only)
  composables/useToast.ts     toast queue
  utils/format.ts             euro / date formatting, es-ES date parsing
  utils/identityHint.ts       live DNI/NIE checksum hint (UX only, server validates)
  components/
    AppIcon.vue               inline SVG icon set by name
    NavRail.vue               rail (desktop) / bottom bar (mobile)
    TopBar.vue                brand, health dot, reset, links
    ToastHost.vue
    ui/StatTile.vue           big-number tile with accent
    ui/DonutChart.vue         SVG donut
    ui/ProgressRing.vue       SVG ring
    ui/ModalDialog.vue        teleported dialog, Escape to close
    ui/LicencePlate.vue       Spanish plate
    students/StudentCard.vue
    students/StudentDrawer.vue  detail + invoice + PDF + quick actions
    students/EnrollModal.vue
  views/
    DashboardView.vue
    StudentsView.vue
    ExamsView.vue
    FleetView.vue
```

## Rules kept

- Views and components import only `services/api`, `store/driveData`, `utils`, `composables`.
- `services/api.ts` and `services/mockDriveStore.ts` untouched except for no changes.
- Contracts in `types/contracts.ts` untouched.
- No new npm dependencies.

## Visual system

- Base `#070b16`, surfaces layered with 1px white borders at 6 to 14 percent alpha.
- One accent per licence: B blue, A2 emerald, C amber. Status: scheduled blue,
  passed emerald, failed rose, cancelled slate.
- Display numerals in Outfit, data in JetBrains Mono, text in Inter.
- Motion limited to 150 to 250 ms and disabled under `prefers-reduced-motion`.
