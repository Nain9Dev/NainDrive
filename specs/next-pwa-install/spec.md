# Spec next-pwa-install — Installable public demo (Android and iOS)

Status: Active
Scope: `NainDrive.Client/` only. No API, service, domain or repository change.

## Problem

`https://drive.naindev.com/` is the Vite build of `NainDrive.Client/`, published to GitHub Pages by
`.github/workflows/deploy.yml` (artifact path `NainDrive.Client/dist`). The page publishes no web app
manifest, so a phone offers no install: no icon of its own, no standalone window.

The criteria (Chrome install criteria, iOS home-screen tags, maskable safe zone) and the shared contract of
all product sites are verified in the portfolio spec `specs/next-pwa-install/spec.md` of
`Nain9Dev/Nain9Dev.github.io`; they are not repeated here.

## Requirements (EARS)

- **REQ-016** When a visitor opens the public page on Android Chrome or iOS Safari, the site shall be
  installable as a standalone app, as detailed below.
  - **REQ-016.1** The site shall serve `manifest.webmanifest` at its root, linked from `index.html`, with
    `id`, `start_url` and `scope` equal to `./`, `display` `standalone`, `name` `NainDrive · Autoescuela`,
    `short_name` `NainDrive`, `lang` `es`, `dir` `ltr`, the page meta description as `description`, and
    `theme_color` and `background_color` equal to the page `theme-color` (`#070b16`). It shall not declare
    `prefer_related_applications`.
  - **REQ-016.2** The manifest shall declare three PNG icons in `icons/` that exist at the declared size:
    192 px and 512 px with purpose `any`, and 512 px with purpose `maskable`, one purpose per entry.
  - **REQ-016.3** The maskable icon and the 180 px `apple-touch-icon.png` shall be opaque edge to edge.
  - **REQ-016.4** The page shall carry `apple-touch-icon`, `mobile-web-app-capable`,
    `apple-mobile-web-app-capable`, `apple-mobile-web-app-title` equal to the `short_name`, and
    `apple-mobile-web-app-status-bar-style` `black` (the page is dark).
  - **REQ-016.5** The site shall register no service worker and offer no install button.

## Edge cases

- Paths are relative (`./`), as `vite.config.ts` sets `base: './'`; the build copies `public/` unchanged.
- The page has no Content-Security-Policy and GitHub Pages serves the files directly: no SPA fallback and no
  workflow change are needed.
- Offline: without a service worker an installed window shows the browser's own offline screen.

## Non-goals

- A service worker, offline page, cache or in-page install button (owner decision of 2026-11-13).
- Changing the visual design or copy of the client.

## Acceptance criteria

- `tests/test_pwa_install.py` passes in the Python suite CI already runs.
- `npm run build` puts the manifest and icons at the root of `dist/`.
- Chrome reports no installability error on the built `dist/`.
- After the deploy, the live manifest answers 200 and the owner installs the app on Android and on an iPhone.

## Session state

- Last updated: 2026-11-14.
- Done: T1 to T3. Verified: 72 tests pass; build copies the files; Chrome reports no installability error.
- Next: T4 after the merge (live check and install on real phones). Blocked: T4 needs the owner's phones.
