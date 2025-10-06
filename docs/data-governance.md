# Data & Governance Handbook

[⬅ Documentation Hub](index.md) · [Secrets Management](secrets-management.md)

This handbook documents datasets, schema expectations, and governance policies for Commercial View.

## Data Sources

| Dataset | Loader | Location | Notes |
|---------|--------|----------|-------|
| Loan Data | `load_loan_data` | `data/pricing/Abaco - Loan Tape_Loan Data_Table.csv` (example) | Primary source for outstanding balances, APR, DPD. |
| Historic Real Payment | `load_historic_real_payment` | `data/payments/Abaco - Loan Tape_Historic Real Payment.csv` | Captures payment history for recovery metrics. |
| Payment Schedule | `load_payment_schedule` | `data/payments/Abaco - Loan Tape_Payment Schedule_Table.csv` | Planned payments and due dates. |
| Customer Data | `load_customer_data` | `data/customer/...` | Optional dataset; API currently returns placeholder data when missing. |
| Collateral | `load_collateral` | `data/collateral/...` | Future enhancement for collateralization metrics. |

## Schema Standards

- Column names use Title Case with spaces to mirror source exports.
- Dates are stored in ISO 8601 format (`YYYY-MM-DD`). Convert to timezone-aware `datetime` objects as needed.
- Monetary values are numeric (`float64`). Use `Decimal` in client layers if higher precision is required.

## Data Quality Controls

1. **Validation:** Loader functions assert presence of critical columns (e.g., `Customer ID`, `Outstanding Loan Value`).
2. **Type Coercion:** Use pandas converters to normalize numeric and date fields.
3. **Anomaly Detection:** `src/metrics_calculator.py` and `src/dpd_analyzer.py` include heuristics for default classification and outlier detection.
4. **Logging:** Missing datasets trigger warnings but do not crash the pipeline; review logs after each run.

## Access Policies

- Restrict production datasets to privileged service accounts.
- Apply row-level security when exporting aggregates outside the core analytics team.
- Track data exports through `google_drive_exporter.py` or other connectors; log success/failure.

## Data Lifecycle

1. **Ingestion:** CSVs land in mounted directories or object storage synchronized to the application host.
2. **Transformation:** Pipeline modules convert raw data to analytics-ready frames.
3. **Storage:** Intermediate artifacts remain in memory; persistent caches can be introduced via Parquet or database tables when needed.
4. **Archival:** Move obsolete datasets to cold storage with retention policies aligned to compliance requirements.

## Compliance Considerations

- Classify datasets according to sensitivity (public, internal, confidential, restricted).
- Apply masking to personally identifiable information before sharing outside the core team.
- Document data sharing agreements and approvals in the governance tracker.

## Change Management

- When schema changes occur, update loader logic, fixtures, and this handbook.
- Notify downstream consumers and coordinate release timelines.
- Add regression tests covering new columns or semantics.

## Related Documents

- [Implementation Guide](implementation-guide.md)
- [Testing & Quality Strategy](testing-and-quality.md)
- [Security Constraints](security_constraints.md)
