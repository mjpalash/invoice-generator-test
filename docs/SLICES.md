# Thin Vertical Slice Backlog and Acceptance Criteria

**Version:** 1.0 | **Status:** Agreed backlog, implementation not started  
**Source requirements:** [../REQUIREMENTS.md](../REQUIREMENTS.md)

## Working agreement

For each numbered slice: write tests first (**Red**), implement minimum functionality (**Green**), refactor, rerun the full regression suite, and show an **in-chat working interface preview**. A slice is not complete merely because a screenshot looks right: it needs working user interaction, persistent storage where relevant, passing unit/integration/acceptance tests, and a demonstrable result. Keep business logic separate from interface/database integration. Use readable Gherkin for acceptance behaviour, plus focused code-level unit tests.

Slices are deliberately incremental; features not yet in scope may be absent from early builds. Do not implement future slices as a prerequisite unless necessary to preserve correct architecture. Track completion and test evidence alongside the implementation.

---

## Slice 1 — Create and list clients

**User story:** As an invoice issuer, I want to create a client and see it in a saved client list so that I can reuse the client later.

**Minimum end-to-end scope:** Local form → validation → persistence → list after save and after restarting. Client fields: name, billing address, place of supply, state, GST-registered checkbox (GSTIN required only if checked), optional email. Client identifier is internal and stable. No invoice creation.

```gherkin
Feature: Client creation
  Scenario: Save a valid client
    Given I am on the client screen
    When I enter a client name, billing address, place of supply and state
    And I leave GST registration unchecked
    And I save the client
    Then the client appears in my client list
    And its data is stored locally

  Scenario: Reject missing required client details
    Given I am on the client screen
    When I try to save a client with no name
    Then the client is not saved
    And I see a validation error explaining the missing name

  Scenario: Require GSTIN only when registered
    Given I am creating a client
    When I check "GST registered"
    Then the GSTIN field becomes visible
    And saving without a GSTIN is rejected

  Scenario: Hide GSTIN for an unregistered client
    Given I am creating a client
    When I leave "GST registered" unchecked
    Then I do not see a GSTIN input
    And I can save the client without GSTIN

  Scenario: Persistence across restarts
    Given I have saved a client
    When I restart the local application
    Then the client still appears with the same details
```

**Unit/integration checks:** required field validators; conditional GSTIN requirement; persistent create/read; invalid input does not create a record; client ID stable. If duplicate identification strategy is not yet agreed, do not silently merge records.

**Done when:** all five scenarios pass; form/list can be used on a running local app and previewed in-chat.

---

## Slice 2 — Select, view and explicitly edit a client

**User story:** As a user, I want to select an existing client without accidentally editing it, and explicitly edit its details when needed.

```gherkin
Feature: Client selection and editing
  Scenario: Display existing client read-only
    Given a saved client exists
    When I select that client
    Then its details are displayed as labels
    And no editable text inputs are shown

  Scenario: Edit only after explicit action
    Given I have selected a client
    When I choose "Edit client"
    Then I can change its editable details
    And saving persists the changes

  Scenario: Cancel editing
    Given I am editing a client
    When I cancel editing
    Then previously saved details remain unchanged
```

**Checks:** read-only state in UI; save/cancel behaviour; edits survive restart.

---

## Slice 3 — Fixed teaching and travel rates per client

**User story:** As an issuer, I want to record each client's agreed teaching and travel amounts so that subsequent invoices use those rates.

```gherkin
Feature: Client service prices
  Scenario: Save both agreed amounts
    Given a client exists
    When I save teaching as ₹150000.00 and travel as ₹12000.00
    Then both amounts are stored against that client
    And the same amounts appear after restarting the application

  Scenario: Reject negative agreed rates
    Given a client exists
    When I enter a negative teaching or travel amount
    Then the changes are rejected with a validation message

  Scenario: Update a rate for future use
    Given a client has a saved teaching amount
    When I update the teaching amount
    Then the revised amount is available for future invoices
```

**Checks:** decimal money handling; rates tied to correct client; no change to another client's rates.

---

## Slice 4 — Calculate service totals and 18% GST

**User story:** As an issuer, I want precise invoice calculations so that the total is correct before finalisation.

```gherkin
Feature: Invoice amount calculation
  Scenario: Teaching and travel both attract 18% GST
    Given teaching is ₹10000.00 and travel is ₹2000.00
    When I calculate the invoice
    Then the taxable subtotal is ₹12000.00
    And GST is ₹2160.00
    And the grand total is ₹14160.00

  Scenario: Teaching only
    Given teaching is ₹10000.00 and travel is not selected
    When I calculate the invoice
    Then GST is ₹1800.00
    And the grand total is ₹11800.00

  Scenario: Reject an empty invoice
    Given neither service is selected
    When I calculate an invoice for finalisation
    Then the invoice is rejected as having no billable service
```

**Checks:** decimal arithmetic; two-decimal rounding edge cases; no binary-float artefacts; one or both items; zero/negative invoice validation. Tax presentation by interstate/intrastate supply is to be agreed before Slice 7.

---

## Slice 5 — Create and preview invoice draft

**User story:** As an issuer, I want to compose an invoice using an existing client and agreed service amounts, and review it before finalising.

```gherkin
Feature: Draft invoice
  Scenario: Use client rates in a draft
    Given a client has fixed teaching and travel amounts
    When I select the client and billing period
    And I select teaching and travel
    Then both saved amounts populate the draft
    And I see subtotal, 18% GST and grand total

  Scenario: Select one service
    Given a client has fixed amounts
    When I select teaching only
    Then only the teaching service contributes to the draft total

  Scenario: Create a new client within invoice workflow
    Given I am creating an invoice draft
    When I choose "Add new client"
    And save a valid new client
    Then the new client is selected for the draft
    And my existing draft context is preserved
```

**Checks:** navigation, selection, required dates/periods, draft re-calculation, no accidental finalisation. Draft local persistence is optional for this slice; finalised persistence comes next.

---

## Slice 6 — Finalise and persist an immutable invoice

**User story:** As an issuer, I want a finalised invoice with a unique identifier and frozen values so that records remain trustworthy.

```gherkin
Feature: Invoice finalisation
  Scenario: Finalise a valid draft
    Given a valid invoice draft exists
    When I finalise it
    Then a unique invoice number is assigned
    And the invoice is saved locally
    And its initial payment status is Unpaid

  Scenario: Finalised values are immutable
    Given an invoice has been finalised
    When I later change the client's address or rates
    Then the finalised invoice still shows its original address and amounts

  Scenario: Reject incomplete finalisation
    Given a draft lacks a required billing period
    When I attempt to finalise it
    Then no finalised invoice is created
    And I see a validation error
```

**Checks:** collision-safe numbering, transaction/atomicity, snapshot correctness, no direct edit endpoint for finalised fields, persistence after restart.

---

## Slice 7 — Preview/download PDF

**User story:** As an issuer, I want a professional PDF of the finalised invoice to email manually.

```gherkin
Feature: Invoice PDF
  Scenario: Generate PDF with correct data
    Given a finalised invoice exists
    When I preview or download the PDF
    Then the PDF contains its number, date, issuer and client details
    And it contains billing period, line items, taxable amounts, GST and total

  Scenario: Re-download historical invoice
    Given a finalised invoice exists
    And the client record has since changed
    When I download that invoice again
    Then the PDF uses the original finalised snapshot
```

**Checks:** PDF content extraction test; display/format smoke test; currency and GST breakdown; correct issuer details. Decide GST presentation (IGST or CGST+SGST) using issuer/client states before implementing.

---

## Slice 8 — Manually record invoice sent

**User story:** As an issuer, I want to record when I have emailed a PDF outside the application, without connecting the application to email.

```gherkin
Feature: Manual delivery tracking
  Scenario: Record sending
    Given a finalised invoice exists
    When I manually mark it Sent and provide a sent date
    Then its delivery status is Sent
    And its sent date is persisted

  Scenario: No automatic sending
    Given a finalised invoice exists
    When I download its PDF
    Then the application does not attempt to send an email
    And the delivery status does not automatically become Sent
```

**Checks:** sent status distinct from payment status; no email dependencies.

---

## Slice 9 — Manually record full payment

**User story:** As an issuer, I want to mark an invoice as fully paid when I have verified receipt outside the application.

```gherkin
Feature: Payment tracking
  Scenario: Record full payment
    Given a finalised Unpaid invoice exists
    When I mark it Paid and provide the payment date
    Then its payment status becomes Paid
    And its payment date persists across restarts

  Scenario: Reject duplicate confirmation
    Given an invoice is already Paid
    When I attempt to mark it Paid again
    Then no duplicate payment event is recorded

  Scenario: No bank automation
    Given an invoice is Unpaid
    When I open the application
    Then its status remains Unpaid until I explicitly confirm payment
```

**Checks:** explicit user action; transaction safety; date validation; no partial payments.

---

## Slice 10 — Invoice history and dashboard

**User story:** As an issuer, I want to find historical invoices and see my invoiced, received and unpaid totals.

```gherkin
Feature: Invoice history
  Scenario: Filter unpaid invoices
    Given I have one Paid and one Unpaid invoice
    When I filter by Unpaid
    Then only the Unpaid invoice appears

  Scenario: View outstanding total
    Given active invoices of ₹11800.00 Paid and ₹14160.00 Unpaid
    When I open the dashboard
    Then total payments recorded is ₹11800.00
    And outstanding balance is ₹14160.00

  Scenario: Retrieve an old invoice
    Given a finalised invoice exists
    When I open its history entry
    Then I can view its details and download its PDF
```

**Checks:** client/date/payment filters; sums use decimal; history survives restart; compact aligned layout.

---

## Slice 11 — Correct by issuing a linked revision

**User story:** As an issuer, I want to correct a finalised invoice without destroying its original record.

```gherkin
Feature: Invoice revisions
  Scenario: Create a linked revision
    Given an original finalised invoice exists
    When I issue a revised invoice based on it
    Then a new invoice with a distinct number is saved
    And the revised invoice references the original
    And the original remains readable and unchanged

  Scenario: Avoid double-counting outstanding balance
    Given an Unpaid original invoice has been superseded by a revised invoice
    When I view current outstanding amounts
    Then the superseded original is not counted as currently outstanding
    And the active revised invoice is counted

  Scenario: Trace invoice history
    Given an original and revised invoice exist
    When I open either invoice
    Then I can identify their revision relationship
```

**Checks:** immutable provenance; numbering policy; paid/sent originals and statutory treatment reviewed before implementation; dashboard accounting excludes superseded invoices appropriately.

---

## Cross-slice testing policy

- **Unit:** validation, state transitions, decimal arithmetic, immutable snapshots and revision logic.
- **Integration:** SQLite round-trips, transaction atomicity, service layer to repository, PDF content.
- **Acceptance:** Gherkin scenarios and real user workflow UI tests as relevant.
- **Regression:** all earlier tests run after each slice.
- **Evidence:** record failing test before implementation, passing test after implementation, and preview/UI verification.
- **No premature implementation:** starting with Slice 1, do not claim later slices are implemented until tested.

## Traceability

| Slice | Requirements |
| --- | --- |
| 1 | FR-01, NFR-03, NFR-04 |
| 2 | FR-01, NFR-04 |
| 3 | FR-02, NFR-05 |
| 4 | FR-03, NFR-05 |
| 5 | FR-01, FR-02, FR-04, NFR-04 |
| 6 | FR-04, FR-06, NFR-07 |
| 7 | FR-05, NFR-09 |
| 8 | FR-05 |
| 9 | FR-06 |
| 10 | FR-07 |
| 11 | FR-08, NFR-07 |

**Next action:** Slice 1 test-first implementation in its own change/commit.
