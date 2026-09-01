# Runbook

Status: Approved
Phase: Deployment and operation

## Local

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
pytest -v
streamlit run src/ui/app.py
```

The dashboard opens on `http://localhost:8501` and seeds fictional demonstration data if the database is empty.

## Public demo

Hosted on Streamlit Community Cloud, tied to the GitHub repository. Entry point: `src/ui/app.py`.

Deployment requires a human action; see B-001 and B-002.

## Data

The SQLite file is disposable. Deleting it and restarting reseeds fictional data.

There is no backup and no migration path. Both are prerequisites before any real use; see T-008.

## Recovery

Every failure mode currently resolves to: delete the database file and restart. This is acceptable only while the data is fictional. The moment a real driving school uses this, that stops being true and T-008 becomes blocking.

## Limits

- Single process, single writer.
- No authentication. Anyone with the URL sees everything.
- No rate limiting.

None of these are defects against the charter. All of them are blockers against real use.
