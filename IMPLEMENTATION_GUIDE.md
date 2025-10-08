# Commercial-View Comprehensive Analytics Dashboard

## Implementation Summary

This implementation provides a comprehensive commercial lending analytics dashboard with full-featured data ingestion, financial analysis, risk modeling, and multi-platform integration capabilities.

## Features Implemented

### 1. Data Ingestion
- **CSV Upload API**: POST `/portfolio/ingest` endpoint for uploading portfolio data
- **Automatic File Type Detection**: Identifies loan data, payment schedules, and customer data
- **Data Validation**: Validates CSV structure and content
- **Preview Generation**: Returns sample data and summary statistics
- **Replace/Append Options**: Supports both replacing and appending data

### 2. Financial Analysis
- **Portfolio Analytics**: Real-time portfolio valuation and metrics
- **Weighted APR Calculation**: Portfolio yield optimization
- **Tenor Mix Analysis**: Distribution of loans by term
- **Collection Rate Tracking**: Payment performance monitoring

### 3. Risk Modeling
- **NPL Tracking**: Non-Performing Loan identification (90+ days past due)
- **Days Past Due (DPD) Distribution**: Risk segmentation by delinquency
- **Concentration Risk Analysis**: Top client exposure metrics
- **Risk Distribution**: Portfolio risk grading

### 4. Multi-Platform Integration
- **RESTful API**: FastAPI backend with comprehensive endpoints
- **Frontend Integration**: Compatible with React TypeScript dashboard
- **CSV Data Export**: Support for data downloads
- **Google Drive Integration**: Via existing upload_to_drive.py script

## API Endpoints

### Health Check
```
GET /health
```
Returns system health and data availability status.

### Executive Summary
```
GET /executive-summary
```
Returns comprehensive KPIs including:
- Total portfolio value
- Active loan count
- Weighted average interest rate
- NPL rate and amount
- Tenor distribution
- Performance metrics

### Portfolio Trends
```
GET /portfolio/trends
```
Returns historical trends including:
- Portfolio growth over time
- Disbursement trends
- Collection trends
- Monthly performance metrics

### Risk Exposure
```
GET /portfolio/risk-exposure
```
Returns detailed risk analytics including:
- Total exposure and at-risk amounts
- Risk distribution by grade
- Concentration risk metrics
- DPD distribution

### CSV Ingestion
```
POST /portfolio/ingest
```
Upload CSV files for portfolio analysis. Supports:
- Loan data files
- Payment schedule files
- Customer data files

**Parameters:**
- `file`: CSV file (required)
- `replace`: Boolean to replace existing data (optional)

## Usage

### Starting the Server

```bash
# Simple mode (recommended)
python run_simple.py

# Or with the original server
python run.py
```

The API will be available at `http://localhost:8000`

### API Documentation

Interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Example: CSV Upload

```bash
curl -X POST http://localhost:8000/portfolio/ingest \
  -F "file=@loan_data.csv" \
  -F "replace=false"
```

### Example: Get Executive Summary

```bash
curl http://localhost:8000/executive-summary
```

## Sample Data

Sample data files are included in the `data/` directory:
- `loan_data.csv`: Sample loan portfolio data
- `payment_schedule.csv`: Sample payment history

## Testing

Run the comprehensive test suite:

```bash
pytest tests/test_comprehensive_api.py -v
```

All tests validate:
- API endpoint functionality
- Data processing accuracy
- Risk calculations
- Portfolio metrics

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Client Applications                      │
│  (React Dashboard, Mobile Apps, External Integrations)       │
└──────────────────────┬──────────────────────────────────────┘
                       │ REST API
┌──────────────────────▼──────────────────────────────────────┐
│                    FastAPI Backend                           │
│  - Health Check      - Executive Summary                     │
│  - Portfolio Trends  - Risk Exposure                         │
│  - CSV Ingestion                                             │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                   CSV Processor                              │
│  - File Upload       - Type Detection                        │
│  - Data Validation   - Metrics Calculation                   │
│  - NPL Analysis      - Risk Assessment                       │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                    Data Storage                              │
│  - CSV Files (data/)                                         │
│  - Google Drive Integration (optional)                       │
└─────────────────────────────────────────────────────────────┘
```

## Key Metrics Calculated

### Portfolio Metrics
- **Total Portfolio Value**: Sum of outstanding balances
- **Active Loan Count**: Number of active loans
- **Weighted Average Rate**: Portfolio-weighted interest rate

### Risk Metrics
- **NPL Rate**: Percentage of loans >90 days past due
- **NPL Amount**: Dollar value of non-performing loans
- **Concentration Risk**: Top client exposure percentages
- **DPD Distribution**: Breakdown of delinquency buckets

### Performance Metrics
- **Collection Rate**: Payment collection efficiency
- **Portfolio Yield**: Actual portfolio return
- **Tenor Mix**: Distribution of loan terms

## Data Requirements

### Loan Data CSV
Required columns:
- `loan_id`: Unique loan identifier
- `customer_id`: Customer identifier
- `principal_amount`: Loan amount
- `interest_rate`: Annual interest rate
- `term_months`: Loan term in months
- `loan_status`: Status (active, closed, etc.)

### Payment Schedule CSV
Required columns:
- `loan_id`: Loan identifier
- `payment_date`: Payment due/made date
- `payment_amount`: Payment amount
- `remaining_balance`: Outstanding balance
- `days_past_due`: Days past due (0 if current)

## Security Considerations

- **CORS**: Configurable allowed origins
- **Input Validation**: CSV files validated before processing
- **Error Handling**: Comprehensive error messages
- **File Size Limits**: Managed by FastAPI

## Future Enhancements

Potential areas for expansion:
- Authentication and authorization
- Database integration for persistent storage
- Real-time data streaming
- Advanced ML-based risk scoring
- Automated report generation
- Multi-tenant support

## Support

For issues or questions:
1. Check API documentation at `/docs`
2. Review test files for usage examples
3. Check logs for error details

## License

Proprietary - Commercial-View Platform
