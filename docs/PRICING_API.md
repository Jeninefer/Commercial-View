# Pricing API Endpoints

This document describes the new pricing-related API endpoints added to the Commercial View API.

## Overview

All pricing endpoints return JSON-safe responses with proper handling of pandas/numpy data types including:
- numpy int64/float64 → Python int/float
- pandas Timestamps → ISO format strings
- NaN/NaT → null (None in Python)

## Endpoints

### GET /pricing-grid

Retrieve pricing grid data.

**Query Parameters:**
- `pricing_type` (optional): Type of pricing grid to return
  - Options: `main`, `commercial`, `retail`, `risk_based`
  - Default: `main`

**Response:**
```json
[
  {
    "tenor_min": 0,
    "tenor_max": 90,
    "amount_min": 0,
    "amount_max": 50000,
    "base_rate": 0.05,
    "margin": 0.02,
    "total_rate": 0.07,
    "product_type": "Commercial",
    "customer_segment": "Standard"
  },
  ...
]
```

**Example:**
```bash
curl http://localhost:8000/pricing-grid?pricing_type=main
```

### GET /pricing-config

Retrieve pricing configuration information.

**Response:**
```json
{
  "pricing_files": {
    "main_pricing_csv": "./data/pricing/main_pricing.csv",
    "commercial_loans": "./data/pricing/commercial_loans_pricing.csv",
    "retail_loans": "./data/pricing/retail_loans_pricing.csv",
    "risk_based_pricing": "./data/pricing/risk_based_pricing.csv"
  },
  "band_keys": {
    "tenor_days": {
      "lower_bound": "tenor_min",
      "upper_bound": "tenor_max",
      "description": "Tenor range in days"
    },
    ...
  },
  "pricing_rules": {
    "default_base_rate": 0.05,
    "default_margin": 0.02,
    "rate_decimal_places": 4,
    "amount_decimal_places": 2,
    "matching_strategy": "best_fit"
  },
  "available_types": ["main", "commercial", "retail", "risk_based"]
}
```

**Example:**
```bash
curl http://localhost:8000/pricing-config
```

### POST /enrich-pricing

Enrich loan data with pricing information.

**Request Body:**
```json
{
  "loan_data": [
    {
      "loan_id": "L001",
      "product_type": "Commercial",
      "customer_segment": "Standard",
      "amount": 10000,
      "tenor_days": 100
    }
  ],
  "pricing_type": "main",
  "join_keys": ["product_type", "customer_segment"]
}
```

**Response:**
```json
[
  {
    "loan_id": "L001",
    "product_type": "Commercial",
    "customer_segment": "Standard",
    "amount": 10000,
    "tenor_days": 100,
    "tenor_min": 91,
    "tenor_max": 180,
    "amount_min": 0,
    "amount_max": 50000,
    "base_rate": 0.055,
    "margin": 0.02,
    "total_rate": 0.075
  }
]
```

**Example:**
```bash
curl -X POST http://localhost:8000/enrich-pricing \
  -H "Content-Type: application/json" \
  -d '{
    "loan_data": [
      {
        "loan_id": "L001",
        "product_type": "Commercial",
        "customer_segment": "Standard",
        "amount": 10000,
        "tenor_days": 100
      }
    ],
    "pricing_type": "main",
    "join_keys": ["product_type", "customer_segment"]
  }'
```

## JSON-Safe Conversion

All endpoints use the `_to_json_safe()` helper function to ensure proper JSON serialization:

1. **Numeric Types**: numpy int64/float64 are converted to native Python int/float
2. **Datetime Types**: pandas Timestamps are converted to ISO format strings
3. **Missing Values**: NaN and NaT are converted to null (None in Python)

This ensures that all responses can be serialized to JSON without errors.

## Error Handling

All endpoints include proper error handling and return appropriate HTTP status codes:

- `200 OK`: Successful request
- `404 Not Found`: Resource not found (e.g., invalid schema name)
- `500 Internal Server Error`: Server error with error details

## Testing

Comprehensive test coverage includes:
- API endpoint tests (test_api.py)
- JSON-safe conversion tests (test_json_safe.py)
- PricingEnricher JSON-safe tests (test_pricing_enricher_json.py)

Run tests with:
```bash
pytest tests/test_api.py tests/test_json_safe.py tests/test_pricing_enricher_json.py -v
```
