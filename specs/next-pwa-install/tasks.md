# Tasks next-pwa-install

- [x] [A] T1 Write `tests/test_pwa_install.py`. Done when it fails on the unmodified tree.
  - Result: 1 failed, 3 errors (manifest missing) before the change.
- [x] [A] T2 Add `manifest.webmanifest` and `icons/` to `NainDrive.Client/public/`. Done when the icon
  checks pass and the PNG files look right.
- [x] [A] T3 Add the manifest link and iOS tags to `NainDrive.Client/index.html`. Done when the full suite
  passes (72 tests), `npm run build` succeeds and `dist/` holds the manifest and icons.
  - Chrome installability probe on `dist/`: no error.
- [ ] [M] T4 Verify after the deploy. Done when the live manifest answers 200 and the owner has installed the
  app on Android and iOS and confirmed icon, label and window.
  - Needs from owner: merge the pull request, then install from Chrome on Android and Safari on an iPhone.

Done when: the full suite is green and the build output contains the manifest and the four icons.
