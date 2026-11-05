# Invoice Manager — Slice 1: Client Creation

Test-first implementation of Slice 1. Only client creation, validation and listing are implemented; see [the backlog](docs/SLICES.md) for later features.

## Run locally

Requires Python 3.10+; no third-party runtime packages.

```bash
python -m invoice_app.app
```

Open http://127.0.0.1:8765. Records persist in `~/.invoice-manager/invoice.sqlite3`. Optionally set `INVOICE_DB` for a different database path or `INVOICE_PORT` for another port.

## Test

```bash
python -m pip install pytest
python -m pytest -q
```

## TDD evidence

Tests were written and executed first: initial Red phase failed at collection with `ModuleNotFoundError: No module named 'invoice_app.app'`. The Green run passed all 11 tests (`11 passed in 0.15s`) in the development workspace. This initial red run establishes the absence of implementation, not individual assertion failures.

See [Slice 1 TDD notes](docs/SLICE1-TDD.md).

## Scope

Create/list clients, validate required fields and optional email, conditionally show and require GSTIN, store in SQLite and reload after restart. Editing, pricing, invoice creation and payments are intentionally not implemented.
