# Security Constraints and Data Protection

## Overview
This document outlines security constraints, data protection measures, and PII (Personally Identifiable Information) handling requirements for the Commercial-View system.

## PII Identification

### Sensitive Data Fields
The following fields are considered PII and must be handled according to security policies:

1. **Customer Identifiers**
   - Customer ID (when directly mappable to individuals)
   - Customer Name
   - National ID / Tax ID
   - Email Address
   - Phone Number
   - Physical Address

2. **Financial Information**
   - Account Numbers
   - Credit Card Numbers
   - Bank Account Details
   - Credit Scores (individual level)
   - Income Information

3. **Loan Details** (context-dependent)
   - Loan ID (when mappable to individuals)
   - Specific transaction details

## PII Masking Strategies

### Before Export - Data Masking Rules

#### 1. Customer Names
```yaml
masking_strategy: "partial"
method: "first_and_last_initial"
example:
  original: "John Smith"
  masked: "J*** S****"
```

#### 2. Customer IDs
```yaml
masking_strategy: "hash"
method: "sha256_truncated"
salt_required: true
example:
  original: "CUST-12345"
  masked: "HSH-89AB4F2E"
```

#### 3. Email Addresses
```yaml
masking_strategy: "partial"
method: "preserve_domain"
example:
  original: "john.smith@example.com"
  masked: "j***@example.com"
```

#### 4. Phone Numbers
```yaml
masking_strategy: "partial"
method: "mask_middle_digits"
example:
  original: "+1-555-123-4567"
  masked: "+1-555-XXX-XX67"
```

#### 5. Account Numbers
```yaml
masking_strategy: "partial"
method: "last_four_digits"
example:
  original: "1234567890123456"
  masked: "************3456"
```

## Data Classification Levels

### Level 1: Public
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

### Level 4: Highly Confidential
- Complete unmasked data
- Individual customer details
- Sensitive financial information
- Restricted to data stewards and compliance officers

## Export Security Controls

### By Export Type

#### KPI JSON/CSV Exports (Public/Internal)
```yaml
security_level: "internal"
pii_masking_required: true
masking_rules:
  - customer_id: "hash"
  - customer_name: "full_mask"
  - loan_id: "hash"
  - email: "full_mask"
  - phone: "full_mask"
access_control: "role_based"
encryption_at_rest: true
encryption_in_transit: true
```

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
```

#### Buckets Exports (Internal)
```yaml
security_level: "internal"
pii_masking_required: true
masking_rules:
  - customer_id: "hash"
aggregation_required: false
access_control: "role_based"
```

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

### Response Procedures
1. Immediate containment
2. Impact assessment
3. Notification (compliance officer, affected parties)
4. Investigation and remediation
5. Post-incident review and prevention measures

## Security Review and Updates

### Regular Reviews
- Quarterly security audit
- Annual penetration testing
- Bi-annual access control review
- Continuous vulnerability scanning

### Security Training
- Annual security awareness training for all users
- Quarterly data protection training for data handlers
- Specialized training for privileged users
