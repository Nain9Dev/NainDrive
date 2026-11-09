# Spec next-seo-discoverability — Search and AI-engine discoverability

Status: Active
Scope: `NainDrive.Client/` only. No API, service, domain or repository change.

## Problem

`https://drive.naindev.com/` is the Vite build of `NainDrive.Client/`, published to GitHub
Pages by `.github/workflows/deploy.yml` (artifact path `NainDrive.Client/dist`). The page had
no canonical URL, social metadata, structured data, sitemap, `robots.txt` or `llms.txt`.

## Requirements (EARS)

- **REQ-015** The public page shall declare one canonical URL, a 70 to 160 character
  description, Open Graph and Twitter card metadata and `SoftwareApplication` JSON-LD naming
  its author, and the deployed site shall serve `robots.txt` (advertising the sitemap),
  `sitemap.xml` and `llms.txt` from its root.

## Non-goals

- Changing the visual design or copy of the client.
- Restructuring the single-page app: the static HTML has only the `#app` mount point and no
  `<h1>`; the headings are rendered by Vue.
