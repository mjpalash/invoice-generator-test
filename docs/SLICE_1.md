# Slice 1 — Create and save clients

**Status:** Implemented in the repository (baseline for later TDD cycles).  
**User story:** As an invoice issuer, I want to register clients and find them later.

## Functionality
- Enter client name, billing address, place of supply, state, optional email.
- Show GSTIN input only when GST-registered is selected; validate GSTIN when required.
- Allocate a unique internal client ID; save details in a local SQLite database.
- List saved clients after creation and after restarting the application.
- No email or bank connections. Agreed service prices, invoices and payments are out of scope.

## Acceptance criteria

| ID | Given / When / Then | Verification |
| --- | --- | --- |
| AC1.1 | Given valid client details, when saved, then client has an ID and appears in the list | `test_save_and_list_valid_client` |
| AC1.2 | Given a blank name or another missing required field, when saving, then reject without writing | `test_required_name_is_rejected_without_writing`, `test_other_required_fields` |
| AC1.3 | Given GST registration selected, when GSTIN is missing/invalid, then reject; when valid, save it | `test_registered_client_requires_valid_gstin` |
| AC1.4 | Given GST registration not selected, when saving, then GSTIN is not required or stored | `test_unregistered_client_does_not_require_or_store_gstin` |
| AC1.5 | Given a saved client, when the database is reopened, then the same client details remain | `test_clients_survive_store_reopen` |
| AC1.6 | Given the local API, when creating/listing a client, then HTTP responses contain the expected data | `test_api_create_and_list`, `test_api_validation_error` |
| AC1.7 | Given the client form, when displayed, then it has the conditional GST controls | `test_ui_serves_gst_conditional_form` |

## Code and tests
- Production: `invoice_app/clients.py` and `invoice_app/app.py`
- Unit/integration/UI-markup tests: `tests/test_clients.py`
- Existing TDD history: [SLICE1-TDD.md](SLICE1-TDD.md)

Run: `python3 -m pytest tests/test_clients.py -q`

**Limit:** HTML markup tests do not constitute a complete interactive browser test. Do not claim full UI acceptance without browser verification.

**Next:** In the agreed repository backlog, client read-only selection/editing is Slice 2 and agreed service rates are Slice 3. The separate rate RED exercise is documented in `SLICE_2_TEST_PLAN.md` to preserve the previously prepared test handoff without silently renumbering the backlog.
