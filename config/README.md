# Configuration Directory

This directory contains all configuration files for the Commercial-View Abaco integration system.

## Configuration Files

### Core Configuration

- **abaco_schema_autodetected.json**: Auto-detected schema from 48,853 Abaco records

- **abaco_schema_config.yml**: Abaco-specific schema configuration

- **abaco_column_maps.yml**: Column mapping for Abaco datasets

### Business Logic Configuration

- **pricing_config.yml**: Pricing rules and interest rate configurations

- **dpd_policy.yml**: Days Past Due (DPD) policies and thresholds

- **export_config.yml**: Export format and destination configurations

### Integration Configuration

- **figma_config.json**: Figma API integration settings

- **google_sheets.yml**: Google Sheets API configuration

- **column_maps.yml**: Generic column mapping rules

### Production Configuration

- **production_config.py**: Production environment settings

## Abaco Data Summary

- **Total Records**: 48,853

- **Portfolio Value**: $208,192,588.65 USD

- **Companies**: Abaco Technologies, Abaco Financial

- **Product Type**: Factoring only

- **Currency**: USD only

- **Payment Frequency**: Bullet payments

## Usage

```python
from config.production_config import ABACO_CONFIG

## Access configuration

total_records = ABACO_CONFIG['total_records']
portfolio_value = ABACO_CONFIG['financial_summary']['total_loan_exposure_usd']

```bash

## Directory Structure
