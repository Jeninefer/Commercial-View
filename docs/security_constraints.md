# Security Constraints and Data Protection

## Overview

This document outlines security constraints, data protection measures, and PII (Personally Identifiable Information) handling requirements for the Commercial-View commercial lending system.

## Commercial Lending PII Identification

### Sensitive Data Fields

The following fields are considered PII and must be handled according to security policies:

1. **Customer Identifiers**

   - Customer ID (when directly mappable to individuals)

   - Customer Name / Business Name

   - National ID / Tax ID / EIN (Employer Identification Number)

   - DUNS Number

   - Email Address

   - Phone Number

   - Physical Address / Business Address

   - Beneficial ownership information

2. **Financial Information**

   - Account Numbers

   - Credit Card Numbers

   - Bank Account Details / Routing Numbers

   - Credit Scores (individual and business level)

   - Income Information / Revenue Data

   - **Commercial lending specific**: Cash flow statements, financial ratios, collateral valuations

   - **Commercial lending specific**: Debt service coverage ratios, working capital amounts

3. **Loan Details** (context-dependent)

   - Loan ID (when mappable to individuals/businesses)

   - Specific transaction details

   - **Commercial lending specific**: Collateral descriptions and locations

   - **Commercial lending specific**: Personal guarantees and guarantor information

   - **Commercial lending specific**: UCC filing details

4. **Commercial Lending Specific PII**

   - **Business Financial Data**: Detailed financial statements, tax returns

   - **Collateral Information**: Property addresses, equipment serial numbers, inventory details

   - **Personal Guarantors**: Individual guarantor PII for commercial loans

   - **Relationship Data**: Corporate structure, beneficial ownership chains

   - **Regulatory Data**: CRA (Community Reinvestment Act) classification data

## PII Masking Strategies

### Before Export - Data Masking Rules

#### 1. Customer Names

```yaml
masking_strategy: "partial"
method: "first_and_last_initial"
example:
  original: "John Smith"
  masked: "J*** S****"

```bash

#### 2. Customer IDs

```yaml
masking_strategy: "hash"
method: "sha256_truncated"
salt_required: true
example:
  original: "CUST-12345"
  masked: "HSH-89AB4F2E"

```bash

#### 3. Email Addresses

```yaml
masking_strategy: "partial"
method: "preserve_domain"
example:
  original: "john.smith@example.com"
  masked: "j***@example.com"

```bash

#### 4. Phone Numbers

```yaml
masking_strategy: "partial"
method: "mask_middle_digits"
example:
  original: "+1-555-123-4567"
  masked: "+1-555-XXX-XX67"

```bash

#### 5. Account Numbers

```yaml
masking_strategy: "partial"
method: "last_four_digits"
example:
  original: "1234567890123456"
  masked: "************3456"

```bash

#### 6. Business Tax ID / EIN

```yaml
masking_strategy: "partial"
method: "mask_middle_digits"
example:
  original: "12-3456789"
  masked: "12-****789"

```bash

#### 7. DUNS Numbers

```yaml
masking_strategy: "hash"
method: "sha256_truncated"
salt_required: true
example:
  original: "123456789"
  masked: "HSH-45A7B9C2"

```bash

#### 8. Collateral Addresses

```yaml
masking_strategy: "geographical_generalization"
method: "zip_code_only"
example:
  original: "123 Main Street, Anytown, CA 90210"
  masked: "*** *** ******, *******, CA 90210"

```bash

#### 9. Financial Ratios (Sensitive Business Data)

```yaml
masking_strategy: "range_bucketing"
method: "categorical_ranges"
example:
  original: "DSCR: 1.47"
  masked: "DSCR: 1.25-1.50"

```bash

#### 10. Loan Amounts (Large Commercial Loans)

```yaml
masking_strategy: "amount_bucketing"
method: "logarithmic_ranges"
example:
  original: "$2,450,000"
  masked: "$2M-$5M"

```bash

## Enhanced Data Classification Levels

### Level 0: Public (Regulatory Reporting)

- Aggregated CRA statistics

- Published regulatory ratios

- Market-level lending data

- No individual institution identification

### Level 1: Public (Internal Reporting)

- Aggregated statistics

- Portfolio-level KPIs

- Bucket summaries

- No individual loan details

### Level 2: Internal

- Anonymized loan-level data

- Masked customer identifiers

- Aggregated risk metrics

- Department-level reports

### Level 3: Confidential

- Full loan details with PII masking

- Customer segments with anonymization

- Detailed risk assessments

- Restricted to authorized personnel

- **Commercial lending**: Industry-level risk metrics

- **Commercial lending**: Collateral details with location masking

### Level 4: Highly Confidential

- Complete unmasked data

- Individual customer details

- Sensitive financial information

- Restricted to data stewards and compliance officers

- **Commercial lending**: Full collateral details, personal guarantor information

### Level 5: Restricted (New Level for Commercial Lending)

- Regulatory examination data

- Board-level confidential information

- Merger & acquisition sensitive data

- Legal proceeding documentation

- Access limited to C-level executives and legal counsel

## Commercial Lending Export Security Controls

### By Export Type

#### Commercial Pricing Matrices (Confidential)

```yaml
security_level: "confidential"
pii_masking_required: true
masking_rules:
  customer_segment: "generalize"
  geographic_region: "state_level_only"
  specific_rates: "range_bucketing"
access_control: "pricing_committee_only"
encryption_at_rest: true
encryption_in_transit: true
watermarking: true

```bash

#### Risk Assessment Reports (Highly Confidential)

```yaml
security_level: "highly_confidential"
pii_masking_required: true
masking_rules:
  borrower_name: "hash"
  financial_statements: "ratio_bucketing"
  collateral_details: "generalized_descriptions"
access_control: "credit_committee_only"
audit_logging: true
retention_period_days: 2555 # 7 years for regulatory compliance
digital_signatures: required

```bash

#### Regulatory Reporting Exports (Restricted)

```yaml
security_level: "restricted"
pii_masking_required: false # Regulatory requirement for full data
masking_rules: null
access_control: "compliance_officer_cro_only"
audit_logging: true
encryption_at_rest: true
encryption_in_transit: true
regulatory_approval_required: true
transmission_controls: "secure_regulatory_portal_only"

```bash

#### KPI JSON/CSV Exports (Public/Internal)

```yaml
security_level: "internal"
pii_masking_required: true
masking_rules:
  customer_id: "hash"
  customer_name: "full_mask"
  loan_id: "hash"
  email: "full_mask"
  phone: "full_mask"
access_control: "role_based"
encryption_at_rest: true
encryption_in_transit: true

```bash

#### DPD Frame Exports (Internal/Confidential)

```yaml
security_level: "confidential"
pii_masking_required: true
masking_rules:

  - customer_id: "hash"

  - customer_name: "partial"

access_control: "role_based"
audit_logging: true
retention_period_days: 90

```bash

#### Buckets Exports (Internal)

```yaml
security_level: "internal"
pii_masking_required: true
masking_rules:

  - customer_id: "hash"

aggregation_required: false
access_control: "role_based"

```bash

## Access Control

### Role-Based Access Control (RBAC)

#### Roles and Permissions

1. **Data Analyst**

   - Read access to masked exports

   - Generate KPI reports

   - View aggregated data

2. **Risk Manager**

   - Read access to confidential exports

   - View loan-level details (masked PII)

   - Generate risk reports

3. **Data Steward**

   - Read/Write access to all data

   - Configure masking rules

   - Manage data quality

4. **Compliance Officer**

   - Full access to unmasked data (with audit trail)

   - Review security controls

   - Access audit logs

5. **Credit Analyst**

   - Read access to borrower financial data (masked PII)

   - Generate credit memos and risk assessments

   - Access to industry benchmarking data

   - Cannot access personal guarantor PII

6. **Loan Officer**

   - Read access to customer relationship data

   - Generate loan proposals and pricing sheets

   - Limited access to financial performance data

   - Cannot access underwriting models

7. **Portfolio Manager**

   - Read access to portfolio performance analytics

   - Generate management reports

   - Access to concentration and diversification metrics

   - Cannot access individual borrower details

8. **Credit Committee Member**

   - Full access to credit analysis (with masked PII for non-guarantors)

   - Access to credit decisions and voting records

   - View collateral appraisals and valuations

   - Access to comparative risk analytics

9. **Chief Risk Officer (CRO)**

   - Full access to all risk-related data

   - Access to stress testing and scenario analysis

   - View regulatory examination findings

   - Access to board-level risk reports

10. **Regulatory Affairs Officer**

    - Full access to regulatory reporting data

    - Access to examination preparation materials

    - View fair lending analysis and testing

    - Access to CRA performance data

### Authentication Requirements

- Multi-factor authentication (MFA) for production access

- API key rotation every 90 days

- Session timeout: 30 minutes of inactivity

- Password complexity requirements enforced

## Encryption Standards

### Data at Rest

- **Algorithm**: AES-256

- **Key management**: External key management service (KMS)

- **Scope**: All exports, databases, and file storage

### Data in Transit

- **Protocol**: TLS 1.3 minimum

- **Certificate validation**: Required

- **Scope**: All API calls, data transfers, and exports

## Audit and Compliance

### Audit Logging Requirements

Log the following for all data access and export operations:

- Timestamp

- User identity

- Action performed

- Data accessed (tables/files)

- IP address

- Result (success/failure)

- Amount of data accessed

### Retention Policies

- Audit logs: 7 years

- Export files: 90 days (configurable)

- Archived exports: 1 year

- Security logs: 3 years

### Compliance Frameworks

The system should comply with:

- **GDPR**: Right to erasure, data portability, consent management

- **SOX**: Financial data integrity and access controls

- **PCI DSS**: If handling payment card data

- **Local data protection regulations**: Country-specific requirements

## Data Anonymization for Non-Production

### Development and Testing Environments

- Use synthetic data generation

- Never use production data in development

- If production data is required, apply full anonymization:

  - Remove all direct identifiers

  - Generalize quasi-identifiers

  - Add noise to numeric values

  - Shuffle linkable attributes

### Data Sharing with Third Parties

- Sign Data Processing Agreement (DPA)

- Apply maximum masking level

- Limit data to minimum required

- Audit third-party security controls

- Establish data retention and deletion terms

## Incident Response

### Security Incident Categories

1. **Data Breach**: Unauthorized access to PII

2. **Data Loss**: Accidental deletion or corruption

3. **Unauthorized Export**: Data exported by unauthorized user

4. **Masking Failure**: PII exposed due to masking error

5. **Regulatory Data Breach**: Unauthorized access to regulatory reporting data

6. **Credit Decision Compromise**: Tampering with credit decisions or models

7. **Fair Lending Violation**: Discriminatory data access or analysis

8. **Collateral Data Exposure**: Unauthorized access to collateral information

9. **Model Manipulation**: Unauthorized changes to risk or pricing models

### Response Procedures

1. Immediate containment (within 15 minutes)

2. Regulatory notification (within 24 hours for material incidents)

3. Impact assessment (within 4 hours)

4. Customer notification (as required by banking regulations)

5. Investigation and forensics (within 72 hours)

6. Remediation and controls enhancement (within 30 days)

7. Regulatory examination preparation (ongoing)

8. Board and management reporting (within 48 hours)

## Business Continuity and Disaster Recovery

```yaml
bcdr_requirements:
  recovery_time_objective: 4_hours # Maximum tolerable downtime
  recovery_point_objective: 15_minutes # Maximum data loss acceptable

  backup_strategy:

    - real_time_replication_to_secondary_site

    - daily_encrypted_backups_to_cloud

    - weekly_full_system_snapshots

    - monthly_disaster_recovery_testing

  incident_communication:

    - automated_stakeholder_notification

    - regulatory_authority_alert_system

    - customer_communication_templates

    - media_relations_protocol

```bash

## Enhanced Security Training and Awareness

### Role-Specific Training Programs

```yaml
training_matrix:
  all_users:

    - annual_security_awareness

    - phishing_simulation_quarterly

    - password_hygiene_training

  privileged_users:

    - advanced_threat_recognition

    - social_engineering_prevention

    - incident_response_procedures

  developers:

    - secure_coding_practices

    - owasp_top_10_training

    - threat_modeling_workshops

  commercial_lending_staff:

    - financial_privacy_regulations

    - fair_lending_compliance

    - customer_data_protection

    - regulatory_examination_preparation

```bash

This comprehensive security framework ensures the Commercial-View platform meets the stringent security requirements of commercial lending operations while maintaining regulatory compliance and protecting sensitive financial data.

# Go to repository root

cd /Users/jenineferderas/Documents/GitHub/Commercial-View

# Remove old venv

rm -rf .venv

# Create new one

python3 -m venv .venv

# Activate for tcsh

source .venv/bin/activate.csh

# Install packages (use full paths to be safe)

.venv/bin/pip install --upgrade pip
.venv/bin/pip install fastapi pandas numpy pydantic
.venv/bin/pip install "uvicorn[standard]"

# Verify

.venv/bin/python -c "import fastapi, pandas, numpy; print('✅ All packages installed')"
