# Personal Invoice Management System — Requirements v1.0

**Status:** Approved baseline for incremental development  
**Date:** 2026-11-05  
**Repository:** https://github.com/mjpalash/invoice-generator-test

## 1. Purpose and scope

A single-user application running **locally on the user's computer** to create, download, track, and manage monthly invoices for Inspiria Knowledge Campus and other clients. The user emails generated PDFs outside the application and manually confirms receipt of payments. No email, bank, GST portal, or cloud integration.

The application should present a compact, consistently aligned dashboard and invoice workflow with an obvious way to add a client while drafting an invoice.

## 2. Functional requirements

### FR-01 Client management

- Create, list, view, and edit client records.
- Each client has a name, billing address, place of supply, state, optional email address, and GST-registration choice. Show the GSTIN input only when GST registration is enabled.
- Reject missing required fields; give actionable validation errors.
- Existing client details are **read-only when selected**, unless Edit is explicitly chosen.
- Add a new client from the invoice-creation workflow without losing draft inputs.
- Persist clients across application restarts; do not silently duplicate an existing client.

### FR-02 Client-specific service prices

- Exactly two initial service types: **Teaching** and **Travel**.
- Store the **fixed, pre-agreed teaching amount and travel amount per client**. Each can be configured independently and must be non-negative.
- Invoices select the applicable service(s); unselected services contribute zero.
- Updating client rates affects future invoices only, not previously finalised invoices.

### FR-03 Tax and amounts

- Charge **18% GST on both Teaching and Travel** for v1.0, as explicitly decided by the user.
- Compute line taxable amounts, tax, subtotal and total using decimal/fixed-point arithmetic, not binary floating-point currency calculations.
- Apply a documented, consistent rounding policy to two decimal places. CGST/SGST versus IGST presentation must be resolved from issuer and place-of-supply details before final invoice output; total GST stays 18%.
- Do not silently change the 18% decision; legal/tax validation remains outside the software.

### FR-04 Draft and finalise invoices

- Select client, invoice date, billing period, and one or both service types.
- Populate agreed amounts from the client record and show a live review of calculations.
- Allow preview before finalisation.
- On finalisation, allocate a unique invoice number, persist the invoice and its **immutable snapshot** of issuer/client identity, addresses, place of supply, service amounts, tax and total.
- Previously finalised invoices are not edited in place, including if a client or rate changes later.
- Reject incomplete invoices and invalid amounts.

### FR-05 PDF and manual delivery

- Generate a readable, professional PDF from a finalised invoice with: issuer details (including GSTIN where applicable), invoice number/date, client details, place of supply, billing period, services, taxable charges, GST breakdown and grand total.
- Allow PDF preview/download and repeated download from history.
- No direct email integration. User manually emails PDF externally and may mark an invoice as **Sent** with a sent date. Sent state is separate from payment state.

### FR-06 Manual payment status

- A newly finalised invoice is initially **Unpaid**.
- User manually marks a verified full payment as **Paid** and records payment date.
- No bank access, transaction matching, or automatic marking.
- Prevent invalid transitions/duplicate paid actions; preserve audit information for payment changes.
- Partial payments are out of scope.

### FR-07 Invoice history and dashboard

- Show invoice number, client, billing period, invoice date, amount, delivery status, payment status, and revision status.
- Filter by client, billing period, paid/unpaid status; open any saved invoice and download its PDF.
- Show total invoiced, total received, and current outstanding balance. Do not double count superseded invoices in outstanding balance.

### FR-08 Revisions

- Correction of finalised invoice creates a **new invoice linked to the original**; original PDF and data remain accessible and immutable.
- Show links between revision and original, and distinguish active/superseded invoices.
- Prevent double-counting replaced invoices. Precise statutory correction/credit-note and numbering policy must be settled before implementing Slice 11.

### FR-09 Local settings and backup

- Store issuer details locally and use them for invoice generation.
- Persist records locally and offer a documented way to back up/restore application data.

## 3. Non-functional requirements

| ID | Requirement |
| --- | --- |
| NFR-01 | Runs locally on a single computer; no hosted service required. |
| NFR-02 | Core workflows function offline. |
| NFR-03 | Persistent local data across restarts. |
| NFR-04 | Compact, well-aligned UI; minimal navigation; clear Add Client in invoice workflow. |
| NFR-05 | Exact monetary calculations and consistent rounding. |
| NFR-06 | Separation of client, rate, invoice, payment, and persistence responsibilities for unit testing. |
| NFR-07 | Unique invoice numbers and immutable finalised snapshots; safe storage updates. |
| NFR-08 | Automated regression tests for every completed slice. |
| NFR-09 | PDF re-download reproduces the stored finalised values. |
| NFR-10 | Local backup/restore procedure documented and tested before release. |

## 4. Exclusions

No automated email, Gmail/Outlook connection, bank connection, payment reconciliation, GST filing, cloud sync, multi-user access, recurring automatic invoicing, automated reminders, or partial payments.

## 5. Development and acceptance process

Use **Test-Driven Development (Red → Green → Refactor)** and **thin vertical slices**. Each slice must provide user-observable value across relevant UI, business logic, and persistence layers. Before implementation:
1. Read the user story and Gherkin acceptance scenarios in [docs/SLICES.md](docs/SLICES.md).
2. Write small tests first, run them, and verify they fail for the expected reason (Red).
3. Implement only enough to pass (Green).
4. Refactor and rerun unit, integration, and acceptance tests.
5. Demonstrate the working interface **in-chat**, without requiring a download to inspect changes.
6. Mark a slice done only when all acceptance criteria and regression tests pass.

Use Gherkin for stakeholder-readable acceptance criteria; unit tests may use direct pytest functions with descriptive names (not forced to use Gherkin).

**Suggested, not yet committed architecture:** Python local web UI, independent Python business modules, SQLite, pytest and pytest-bdd, local PDF generation.

## 6. Release completion criteria

User can create/select/edit clients, save their fixed teaching/travel amounts, create/finalise invoices with 18% GST, preview/download PDFs, manually record sending and full payment, browse history/dashboard, and issue traceable revisions—all locally. Complete regression suite passes and backup procedure works.

## 7. Deferred decisions and explicit interpretations

- Tax display: determine IGST versus CGST+SGST based on configured issuer state and client place of supply before PDF slice. GST on both services is nevertheless fixed at 18% for this project.
- Invoice number format, mandatory invoice fields, rounding granularity, and date rules will be specified in their respective slice before writing the first test.
- Fixed client prices are stored for both services. Whether a price may be zero is initially permitted (for a client who has no agreed amount for a service); invoice creation must explicitly select at least one service with a positive taxable amount.
- Revision mechanics must comply with applicable invoice correction practice; preserve originals in all cases.
- This is a software specification, not a determination of GST compliance.

See [docs/SLICES.md](docs/SLICES.md) for the full ordered backlog and acceptance criteria.
