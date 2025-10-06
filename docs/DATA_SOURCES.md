# Commercial View data sources

This guide documents the canonical input datasets required by the Commercial
View ETL pipeline. Each section describes the expected schema, data quality
rules, and refresh guidance for operational teams.

## Shared conventions

- **File format:** UTF-8 CSV with headers on the first row.
- **Date fields:** ISO-8601 (`YYYY-MM-DD`).
- **Currency fields:** Store as numeric values without thousands separators.
- **Identifiers:** `Loan ID` and `Customer ID` are case-sensitive strings.
- **Storage location:** By default the repository reads from `data/`. Override
  by setting `COMMERCIAL_VIEW_DATA_PATH` to a directory (or direct CSV path for
  ad-hoc loads).

Validation is enforced by `src/data_loader.py`. Tests in
`tests/test_data_loader.py` exercise the same rules to guard against schema
regressions.

## `loan_data.csv`

Primary loan tape used for portfolio analytics.

| Column | Type | Description |
|--------|------|-------------|
| Loan ID | string | Unique identifier for the loan account. |
| Customer ID | string | Master identifier for the borrowing entity. |
| Disbursement Date | date | Date the facility was funded. |
| Disbursement Amount | number | Gross funded amount in local currency. |
| Outstanding Loan Value | number | Current principal balance outstanding. |
| Days in Default | integer | Calendar days past contractual due date (0 if current). |
| Interest Rate APR | number | Annualised interest rate expressed as percentage. |
| Product | string | (Optional) Product family label used for segmentation. |
| Loan Status | string | (Optional) Operational status (e.g. Current, Past Due). |

### Refresh notes

- Ensure `Days in Default` stays in sync with the reporting date of the tape.
- Any additional columns may be included; the loader only enforces the required
  set above.
- Sensitive borrower information (names, tax IDs) must be removed or anonymised
  before committing sample data.

## `payment_schedule.csv`

Contractual schedule used for forecasting and cohort analytics.

| Column | Type | Description |
|--------|------|-------------|
| Loan ID | string | Identifier linking to the loan tape. |
| Due Date | date | Scheduled due date for the instalment. |
| Scheduled Principal | number | Principal amount contractually due. |
| Scheduled Interest | number | Interest amount contractually due. |
| Total Payment | number | Sum of scheduled principal and interest. |
| Installment Number | integer | Sequential number of the instalment starting at 1. |

### Refresh notes

- Include only active or outstanding instalments to keep schedules lean.
- Keep instalment numbering contiguous per loan to support cohort analytics.

## `historic_real_payment.csv`

Recorded payments used for recovery and collections performance tracking.

| Column | Type | Description |
|--------|------|-------------|
| Loan ID | string | Identifier linking to the loan tape. |
| True Payment Date | date | Actual settlement date. |
| True Principal Payment | number | Principal amount applied. |
| True Interest Payment | number | Interest amount applied. |
| Payment Channel | string | (Optional) Channel or instrument used for the payment. |

### Refresh notes

- Payments beyond the reporting window may be truncated to align with BI
  dashboards.
- If a payment contains zero principal, keep the row to preserve auditability.

## `Q4_Targets.csv`

Executive targets used for operational scorecards.

| Column | Type | Description |
|--------|------|-------------|
| Metric | string | Name of the KPI or initiative. |
| Target Value | number | Numeric target expressed in the KPI's unit. |
| Owner | string | Accountable business owner. |
| Due Date | date | Target completion date. |
| Notes | string | (Optional) Additional context or assumptions. |

### Refresh notes

- Update quarterly; retain prior files in version control for audit trail.
- When adding new KPIs, document the definition within this file before
  shipping changes.

## Operational checklist

1. Pull the latest exports from the core banking system.
2. Remove or anonymise direct identifiers before staging in the repository.
3. Drop the CSVs into a working directory and set `COMMERCIAL_VIEW_DATA_PATH`
   accordingly (or copy into `data/`).
4. Run `pytest tests/test_data_loader.py -v` to confirm schema compatibility.
5. Proceed with downstream analytics or commit the refreshed data.
