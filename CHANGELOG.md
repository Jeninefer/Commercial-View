# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Future features will be listed here

## [1.0.0] - 2024-12-03

### Added
- Initial release of Commercial-View analytics system
- Configuration system with YAML-based config files
  - Column mapping configuration (`column_maps.yml`)
  - Pricing configuration with band keys (`pricing_config.yml`)
  - DPD policy configuration (`dpd_policy.yml`)
  - Export configuration (`export_config.yml`)
- Comprehensive documentation
  - Performance SLOs documentation
  - Security constraints and PII masking guidelines
  - Versioning strategy and release workflow
- CI/CD pipeline with GitHub Actions
  - Automated testing across Python 3.8, 3.9, and 3.10
  - Code quality checks (Black, isort, Flake8, Pylint)
  - Security scanning (Safety, Bandit)
  - Automated deployments to staging and production
- Pre-commit hooks for code quality
  - Python formatting and linting
  - YAML and Markdown validation
  - Security checks
  - Type checking with mypy
- Schema validator for configuration files
  - Validates column mappings
  - Validates pricing configuration
  - Validates DPD policy
  - Validates export configuration
- Example pricing files
  - Main pricing grid
  - Commercial loans pricing
  - Retail loans pricing
  - Risk-based pricing
- DPD analysis specifications
  - Days Past Due calculation framework
  - Risk bucketing system (Current, 1-30, 31-60, 61-90, 91-120, 121-180, 180+ days)
  - Default threshold configuration (90/120/180 days)
- Export specifications
  - DPD frame output format
  - Buckets output format
  - KPI JSON/CSV exports
- Project scaffolding
  - Directory structure
  - .gitignore for build artifacts and runtime exports
  - VERSION file
  - Comprehensive README

### Technical Details
- Python 3.8+ support
- YAML-based configuration system
- Modular schema validation
- Comprehensive CI/CD pipeline
- Pre-commit hook integration
- Security-first design with PII masking

### Documentation
- README with quick start guide
- Performance SLOs with scalability guidelines
- Security constraints with compliance framework
- Versioning strategy with Git workflow
- Example configurations and pricing files

[Unreleased]: https://github.com/Jeninefer/Commercial-View/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/Jeninefer/Commercial-View/releases/tag/v1.0.0
