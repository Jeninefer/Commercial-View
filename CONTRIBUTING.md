# Contributing to Commercial View Platform

Thank you for your interest in contributing to the Commercial View Platform! This document provides guidelines and instructions for contributing to this project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)

## Code of Conduct

### Our Standards

- Be respectful and inclusive
- Accept constructive criticism gracefully
- Focus on what is best for the project and team
- Show empathy towards other team members

### The Prime Directive

**"Standard is Excellence"** - All code and communication must adhere to the highest standards of quality, clarity, and professionalism. We don't just aim for correct - we aim for superior, robust, and market-leading solutions.

## Getting Started

### 1. Set Up Development Environment

```bash
# Clone the repository
git clone https://github.com/Jeninefer/Commercial-View.git
cd Commercial-View

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest black flake8 mypy pre-commit
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your local settings
# For development, you can use mock data without API keys
```

### 3. Verify Setup

```bash
# Run tests
pytest tests/ -v

# Check code style
black --check .
flake8 .

# Run main script
python main.py --mode analysis
```

## Development Workflow

### 1. Create Feature Branch

```bash
# Update main branch
git checkout main
git pull origin main

# Create feature branch
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

### Branch Naming Conventions

- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Test additions/updates
- `chore/` - Maintenance tasks

### 2. Make Changes

- Write clean, readable code
- Follow existing code style
- Add comments for complex logic
- Update documentation as needed
- Write tests for new features

### 3. Test Your Changes

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_optimization.py -v

# Check coverage
pytest tests/ --cov=. --cov-report=html

# Lint your code
black .
flake8 .
```

### 4. Commit Changes

```bash
# Stage changes
git add .

# Commit with meaningful message
git commit -m "feat: add portfolio concentration alerts"
```

### 5. Push and Create PR

```bash
# Push to remote
git push origin feature/your-feature-name

# Create Pull Request on GitHub
# Request review from team members
```

## Coding Standards

### Python Style Guide

We follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) with some modifications:

**Line Length:**
- Maximum 100 characters (not 79)
- Break long lines logically

**Imports:**
```python
# Standard library
import os
from pathlib import Path

# Third-party
import pandas as pd
import numpy as np

# Local
from config import settings
from analysis import KPICalculator
```

**Docstrings:**
```python
def optimize_disbursements(requests, portfolio, available_cash):
    """
    Optimize loan disbursement decisions.
    
    Args:
        requests (pd.DataFrame): Pending disbursement requests
        portfolio (pd.DataFrame): Current loan portfolio
        available_cash (float): Available cash for disbursement
        
    Returns:
        dict: Optimization results with recommended loans
        
    Example:
        >>> result = optimize_disbursements(requests_df, portfolio_df, 1000000)
        >>> print(result['num_loans'])
        15
    """
    # Implementation
```

**Type Hints:**
```python
from typing import Dict, List, Optional

def calculate_kpis(
    loan_tape: pd.DataFrame,
    historical_data: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, float]:
    """Calculate portfolio KPIs."""
    pass
```

### Code Formatting

We use **Black** for code formatting:

```bash
# Format all files
black .

# Format specific file
black path/to/file.py

# Check without modifying
black --check .
```

### Linting

We use **Flake8** for linting:

```bash
# Run linter
flake8 .

# Configuration in setup.cfg or .flake8
```

## Testing Guidelines

### Writing Tests

**Test Structure:**
```python
import pytest
import pandas as pd
from module import function_to_test

@pytest.fixture
def sample_data():
    """Fixture for test data."""
    return pd.DataFrame({
        'column1': [1, 2, 3],
        'column2': ['a', 'b', 'c']
    })

def test_function_basic(sample_data):
    """Test basic functionality."""
    result = function_to_test(sample_data)
    assert result is not None
    assert len(result) > 0

def test_function_edge_cases():
    """Test edge cases."""
    # Empty data
    result = function_to_test(pd.DataFrame())
    assert result == expected_default
    
    # Invalid input
    with pytest.raises(ValueError):
        function_to_test(None)
```

**Test Coverage:**
- Aim for >80% code coverage
- Test happy paths and edge cases
- Test error handling
- Use fixtures for reusable test data

**Running Tests:**
```bash
# All tests
pytest tests/ -v

# Specific test
pytest tests/test_optimization.py::test_greedy_optimization -v

# With coverage
pytest tests/ --cov=. --cov-report=term-missing

# Generate HTML coverage report
pytest tests/ --cov=. --cov-report=html
open htmlcov/index.html
```

## Commit Guidelines

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```bash
feat(optimization): add sector-based filtering

Add ability to filter disbursement requests by sector before optimization.
This allows KAMs to focus on specific industry segments.

Closes #123

---

fix(dashboard): correct KPI calculation for overdue loans

Previous calculation included paid loans in overdue ratio.
Now correctly filters for active and overdue loans only.

---

docs(readme): update installation instructions

Add Docker installation steps and troubleshooting section.
```

### Atomic Commits

- One logical change per commit
- Commit working code only
- Write clear, descriptive messages
- Reference issue numbers when applicable

## Pull Request Process

### Before Submitting PR

**Checklist:**
- [ ] Code follows style guidelines
- [ ] Tests pass locally
- [ ] New code has tests
- [ ] Documentation updated
- [ ] No merge conflicts
- [ ] Commit messages are clear
- [ ] Branch is up to date with main

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
How was this tested?
- [ ] Unit tests
- [ ] Integration tests
- [ ] Manual testing

## Screenshots (if applicable)
Add screenshots for UI changes

## Checklist
- [ ] My code follows the style guidelines
- [ ] I have performed a self-review
- [ ] I have commented complex code
- [ ] I have updated documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests
- [ ] All tests pass
```

### Review Process

1. **Submit PR** with clear description
2. **Request review** from team members
3. **Address feedback** promptly
4. **Update PR** based on reviews
5. **Merge** when approved

### Merging

- Squash commits if appropriate
- Delete branch after merge
- Update local main branch

```bash
git checkout main
git pull origin main
git branch -d feature/your-feature-name
```

## Development Tips

### Using Sample Data

```python
# For testing without API keys
from ingestion import load_sample_data

data = load_sample_data()
# Use data['loan_tape'], data['disbursement_requests'], etc.
```

### Debugging

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Use pdb for debugging
import pdb; pdb.set_trace()

# Or use breakpoint (Python 3.7+)
breakpoint()
```

### Environment-Specific Config

```bash
# Development
export ENV=development
export DEBUG=true

# Testing
export ENV=testing
export ENABLE_MOCK_DATA=true

# Production
export ENV=production
export DEBUG=false
```

## Questions or Issues?

- **Technical Questions**: Open a discussion on GitHub
- **Bug Reports**: Create an issue with detailed description
- **Feature Requests**: Open an issue with use case
- **Security Issues**: Email security@abaco.com

## Recognition

Contributors will be acknowledged in:
- CHANGELOG.md
- Project README
- Release notes

Thank you for contributing to Commercial View Platform! 🚀

---

**Remember: Standard is Excellence**
