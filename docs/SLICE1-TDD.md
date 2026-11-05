# Slice 1 — TDD execution log

## Red (before implementation)

Tests were created first under `tests/test_clients.py`. Executed `python -m pytest -q`. Test collection failed with `ModuleNotFoundError: No module named 'invoice_app.app'`, because no application implementation existed. This is the initial red phase; it does not demonstrate individual assertions failing.

## Green

Added client validation, SQLite store, WSGI API and client form. Executed `python -m pytest -q` in the development workspace. Output: `11 passed in 0.15s`.

## Tests covered

- Valid client creation and listing
- Required name, address, place of supply, and state
- Conditional GSTIN requirement and basic format
- No GSTIN saved for unregistered clients
- Local data persistence after reopening the database
- API POST and GET
- HTTP validation error prevents invalid records
- HTML form includes GST controls

## Remaining verification

Manual browser-interaction testing and automated headless browser tests are not included in this first slice. The application UI must be reviewed interactively before claiming UI acceptance. GSTIN format checks do not validate the tax authority's checksum or registration existence.

## Run

`python -m pip install pytest && python -m pytest -q`
