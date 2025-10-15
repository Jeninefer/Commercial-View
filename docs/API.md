# API Documentation

## Commercial-View Abaco Integration API

### Core Components

#### DataLoader Class

Handles loading and validation of Abaco loan tape data.

**Features:**

- Validates against exact 48,853 record schema

- Spanish client name support

- USD factoring product processing

- Risk scoring and analytics

#### Portfolio Processing

Main processing pipeline for Abaco data.

**Capabilities:**

- Delinquency bucketing (7 tiers)

- Risk scoring (0.0-1.0 scale)

- Export to CSV and JSON formats

- Spanish business name handling

### Usage Examples

```python
from src.data_loader import DataLoader

# Initialize with Abaco support

loader = DataLoader(data_dir="data")

# Load complete dataset

abaco_data = loader.load_abaco_data()

# Process with portfolio script

python portfolio.py --config config --abaco-only

<<<<<<< Updated upstream
```bash
=======
```text
>>>>>>> Stashed changes

### Validation Status

- Schema: 48,853 records (16,205 + 16,443 + 16,205)

- Spanish Names: "SERVICIOS TECNICOS MEDICOS, S.A. DE C.V."

- Currency: USD exclusively

- Products: Factoring exclusively

- Interest Rates: 29.47% - 36.99% APR
