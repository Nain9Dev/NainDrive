# Plan next-pwa-install

1. `tests/test_pwa_install.py` checks REQ-016 against `NainDrive.Client/index.html` and
   `NainDrive.Client/public/` (Vite copies `public/` verbatim to `dist/`). The CI job `test-backend` runs it
   with `pytest tests/`; the client has no test runner of its own.
2. Add `public/manifest.webmanifest` and the four PNG files in `public/icons/`.
3. Add the manifest link and the iOS tags to `index.html`, next to the existing `theme-color` meta.

## Decisions

- Static manifest in `public/`. No plugin and no generated manifest.
- No service worker: Chrome and iOS install without one (owner decision of 2026-11-13).
- Relative paths (`./`): the project builds with `base: './'`, and the manifest and links stay valid on
  the custom domain.
- Status bar style `black`: the page is dark.

## Icons

Rendered from `NainDrive.Client/public/favicon.svg` (the steering wheel on its dark tile). Regenerate with:

```
node make-install-icons.mjs --source NainDrive.Client/public/favicon.svg \
  --out NainDrive.Client/public/icons --bg "#080d1a" --maskable-scale 0.56
```

The maskable icon fits the whole tile inside the centred circle of radius 40% of the width.

## Publishing

`deploy.yml` uploads `NainDrive.Client/dist`; the build copies `public/` to its root, so no workflow change.
There is no Content-Security-Policy and no SPA rewrite.

## Test strategy

- Python test: manifest members and exact names, icon files at their declared size, opacity of the maskable
  and Apple icons (PNG decoded with the standard library), head tags, no service worker.
- Manual: Chrome `Page.getInstallabilityErrors` on the built `dist/`; after the deploy, the owner's phones.
