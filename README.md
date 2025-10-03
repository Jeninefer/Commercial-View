# Commercial-View
Principal KPI

## Installation

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

The `Calculator` class provides safe mathematical operations for KPI calculations:

```python
from commercial_view import Calculator
import pandas as pd
import numpy as np

calc = Calculator()

# Scalar division
result = calc.safe_division(10, 2)  # Returns 5.0
result = calc.safe_division(10, 0)  # Returns nan (default)
result = calc.safe_division(10, 0, default=0)  # Returns 0

# Series division
num = pd.Series([10, 20, 30])
den = pd.Series([2, 0, 5])
result = calc.safe_division(num, den)  # Returns Series([5.0, nan, 6.0])

# Array division
num = np.array([10, 20, 30])
den = np.array([2, 0, 5])
result = calc.safe_division(num, den)  # Returns array([5.0, nan, 6.0])
```

## Testing

Run the tests:

```bash
python -m unittest discover tests
```
