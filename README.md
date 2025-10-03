# Commercial-View
Principal KPI

## Usage (no demo data)

Use your live DataFrames with the exact column names described in the "Data contracts" section below.

## Data contracts (required columns)

### Payments & DPD

**Schedule DF:**
- Required columns: `loan_id|id_loan|...`, `due_date|fecha_vencimiento|scheduled_date`, `due_amount|amount_due|...`

**Payments DF:**
- Required columns: `loan_id|id_loan|...`, `payment_date|fecha_pago|...`, `payment_amount|amount|monto_pago`

### Feature engineering

**Master DF:**
- Required columns: `loan_id`, `customer_id`, `outstanding_balance`
- Optional columns: `days_past_due`, `apr`, `eir`, `term`, `line_amount`

### Pricing enrichment

**Pricing grid CSV:**
- Columns to match on any of: `[segment, risk_score|risk_rating, term, amount]`

**Recommended pricing CSV:**
- Columns to match on any of: `[segment, risk_score|risk_rating, term, amount]`
- Optional interval keys in grid: e.g. `tenor_min`, `tenor_max`, `amount_min`, `amount_max`

### KPIs

**Revenue DF:**
- Required columns: `date`, `recurring_revenue`
- Optional columns: `start_revenue`, `end_revenue`, `revenue`, `customer_count`

**Customer DF:**
- Required columns: `churn_count`, `start_count`
- Optional columns: `new_customers`, `is_churned`

**Expense DF:**
- Required columns: `date`, `total_expense`, `cash_balance`
- Optional columns: `marketing_expense`

**Loan DF:**
- Required columns: one of `loan_amount|amount|monto_prestamo`
- Optional columns: `days_past_due|dpd|dias_atraso`, `revenue`, `apr`, `eir`

**Financial DF:**
- Required columns: `pre_money_valuation`
- Optional columns: `investment_amount`, `enterprise_value`, `ebitda`, `shares_before`, `shares_after`

## Interval pricing example (configure keys in code where you call enrich_loan_data)

Provide mapping like:

```python
# Example configuration for interval pricing
interval_keys = {
    'term': ('tenor_min', 'tenor_max'),
    'amount': ('amount_min', 'amount_max')
}

# When calling enrich_loan_data, pass the interval configuration
enriched_data = enrich_loan_data(
    loan_df=your_loan_dataframe,
    pricing_grid=pricing_grid_csv,
    interval_keys=interval_keys
)
```
