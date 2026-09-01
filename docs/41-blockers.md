# Blockers

Status: Active
Phase: Development

Every external dependency this project needs, listed before the work starts rather than when a task stalls.

Rule: while a blocker is open, the agent does not fake the credential, does not silently mock the dependency, and does not mark the dependent task as done. It stops and says so.

## B-001 — Streamlit Community Cloud account

Label: `[H]`
Blocks: T-009
What is needed: a Streamlit Community Cloud account linked to the GitHub account that owns the repository.
Where: https://share.streamlit.io/
How it is stored: no credential enters this repository. The link is authorised in the Streamlit interface.
Done when: the app appears in the Streamlit dashboard and its public URL returns the dashboard.

## B-002 — Public GitHub repository

Label: `[H]`
Blocks: T-009, B-001
What is needed: the repository published under the owner's GitHub account, with `.venv/`, `__pycache__/` and the SQLite database file excluded.
Done when: `git remote -v` resolves and the working tree is clean.

## B-003 — Tax rate confirmation

Label: `[H]`
Blocks: T-006, REQ-007
What is needed: the applicable `IVA` rate for driving school tuition per licence type, or an explicit decision to keep 21 percent as a documented demo limitation.
Where: an accountant, or the Spanish tax agency guidance on training services.
Done when: the rate and its source are recorded in ADR form.

## B-004 — Evidence of willingness to pay

Label: `[H]`
Blocks: any extension of scope beyond the current showcase.
What is needed: three conversations with driving school owners about how they bill today and what it costs them.
Done when: the findings are written into `00-charter.md` and either confirm or retire the product hypothesis.
