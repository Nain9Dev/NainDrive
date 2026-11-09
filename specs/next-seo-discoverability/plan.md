# Plan next-seo-discoverability

1. `tests/test_seo_discoverability.py` checks REQ-015 against `NainDrive.Client/index.html` and
   `NainDrive.Client/public/*` (Vite copies `public/` verbatim to `dist/`).
2. Add canonical, author link, Open Graph, Twitter card and JSON-LD to `index.html`.
3. Add `robots.txt`, `sitemap.xml` and `llms.txt` to `NainDrive.Client/public/`.
