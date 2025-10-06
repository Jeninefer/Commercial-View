# Versioning Strategy

## Overview

This document defines the versioning strategy, release workflow, and tagging conventions for the Commercial-View project.

## Version Numbering

### Semantic Versioning (SemVer)

We follow [Semantic Versioning 2.0.0](https://semver.org/) with the format:

```
MAJOR.MINOR.PATCH[-PRERELEASE][+BUILD-METADATA]
```

### Version Components

#### MAJOR (X.0.0)
Increment when making incompatible API changes or major breaking changes:
- Changes to configuration file structure that require migration
- Breaking changes to export formats
- Changes to DPD calculation methodology
- Major architectural changes
- **Commercial lending specific**: Changes to pricing models, risk calculation algorithms, regulatory compliance frameworks

#### MINOR (0.X.0)
Increment when adding functionality in a backwards-compatible manner:
- New KPI metrics
- New export formats
- New configuration options (with defaults)
- Enhanced masking strategies
- Performance improvements
- **Commercial lending specific**: New pricing tiers, additional risk factors, enhanced collateral types, expanded geographic coverage

#### PATCH (0.0.X)
Increment when making backwards-compatible bug fixes:
- Bug fixes
- Security patches
- Documentation updates
- Minor performance optimizations
- **Commercial lending specific**: Rate calculation fixes, DPD bucket corrections, regulatory compliance updates

#### Pre-release Identifiers
- `alpha`: Early development, unstable
- `beta`: Feature complete, testing phase
- `rc` (Release Candidate): Production-ready, final testing
- **Commercial lending specific**: `regulatory` (awaiting compliance approval), `audit` (under regulatory review)

**Examples:**
- `2.0.0-alpha.1`
- `2.0.0-beta.2`
- `2.0.0-rc.1`
- `2.1.0-regulatory.1` (pending regulatory approval)

## Tagging Convention

### Git Tag Format
```
v{MAJOR}.{MINOR}.{PATCH}[-{PRERELEASE}]
```

### Tag Examples
- `v1.0.0` - Production release
- `v1.2.3` - Regular update
- `v2.0.0-beta.1` - Pre-release
- `v1.5.4-hotfix` - Hotfix tag
- `v2.3.0-regulatory.1` - Regulatory compliance release

### Tag Naming Rules
1. Always prefix with lowercase `v`
2. Use semantic version numbers
3. No spaces in tag names
4. Use hyphens for pre-release identifiers
5. Include descriptive suffix for special releases (e.g., `-hotfix`, `-lts`, `-regulatory`)

### Creating Tags
```bash
# Create annotated tag for releases
git tag -a v1.2.3 -m "Release version 1.2.3 - Enhanced commercial lending risk models"

# Create lightweight tag for internal milestones
git tag v1.2.3-dev

# Push tags to remote
git push origin v1.2.3
# Or push all tags
git push origin --tags
```

## Branch Strategy

### Main Branches

#### `main`
- Always production-ready
- Protected branch (requires PR and reviews)
- Tagged with release versions
- Only accepts merges from `release/*` or `hotfix/*` branches
- **Commercial lending specific**: Must pass regulatory compliance checks

#### `develop`
- Integration branch for features
- Contains latest delivered development changes
- Source for next release
- **Commercial lending specific**: Includes staging environment deployment

### Supporting Branches

#### Feature Branches
- **Format**: `feature/{issue-number}-{short-description}`
- **Example**: `feature/123-add-commercial-re-pricing`
- Branch from: `develop`
- Merge to: `develop`
- Naming: lowercase with hyphens

#### Release Branches
- **Format**: `release/{version}`
- **Example**: `release/1.2.0`
- Branch from: `develop`
- Merge to: `main` and `develop`
- Purpose: Prepare new production release
- **Commercial lending specific**: Includes regulatory compliance validation

#### Hotfix Branches
- **Format**: `hotfix/{version}`
- **Example**: `hotfix/1.2.1`
- Branch from: `main`
- Merge to: `main` and `develop`
- Purpose: Quick production fixes
- **Commercial lending specific**: Emergency regulatory or calculation fixes

#### Regulatory Branches
- **Format**: `regulatory/{version}-{compliance-type}`
- **Example**: `regulatory/2.1.0-basel-iii`
- Branch from: `develop`
- Merge to: `develop` after approval
- Purpose: Regulatory compliance implementations

## Release Workflow

### Regular Release Process

#### 1. Prepare Release Branch
```bash
# Create release branch from develop
git checkout develop  
git pull origin develop
git checkout -b release/1.2.0
```

#### 2. Update Version Numbers
Update version in:
- `VERSION` file
- `setup.py` or `pyproject.toml`
- Configuration files (`configs/pricing_config.yml`)
- API documentation
- **Commercial lending specific**: Pricing model versions, risk calculation versions

#### 3. Update Changelog
Update `CHANGELOG.md` with:
- Release version and date
- New features (pricing models, KPIs, risk factors)
- Bug fixes (calculation corrections, data fixes)
- Breaking changes (API changes, configuration changes)
- Deprecations (old pricing models, legacy endpoints)
- **Commercial lending specific**: Regulatory compliance updates, model changes, rate adjustments

#### 4. Commercial Lending Validation
- **Risk Model Testing**: Validate all pricing and risk calculations
- **Regulatory Compliance**: Ensure CECL, Basel III, and local regulations
- **Data Integrity**: Verify DPD calculations, NPL classifications
- **Performance Testing**: Test with large commercial portfolios
- **Integration Testing**: Validate Google Drive, export systems
- **Security Scan**: PII masking, data protection compliance

#### 5. Test Release Candidate
- Run full test suite
- Perform integration testing
- Conduct security scan
- Review documentation
- **Commercial lending specific**: Validate against regulatory test cases

#### 6. Finalize Release
```bash
# Merge to main
git checkout main
git merge --no-ff release/1.2.0
git tag -a v1.2.0 -m "Release version 1.2.0 - Enhanced commercial lending platform"

# Merge back to develop
git checkout develop
git merge --no-ff release/1.2.0

# Push changes and tags
git push origin main develop --tags

# Delete release branch
git branch -d release/1.2.0
git push origin --delete release/1.2.0
```

#### 7. Publish Release
- Create GitHub release from tag
- Attach release artifacts (pricing matrices, documentation)
- Publish release notes
- Update documentation
- **Commercial lending specific**: Notify stakeholders of pricing/model changes

### Commercial Lending Specific Workflows

#### Regulatory Release Process
```bash
# Create regulatory compliance branch
git checkout develop
git checkout -b regulatory/2.1.0-dodd-frank

# Implement compliance changes
# Run regulatory test suite
# Submit for compliance review

# After approval, merge to develop
git checkout develop
git merge --no-ff regulatory/2.1.0-dodd-frank
```

#### Emergency Rate Adjustment
```bash
# Create emergency hotfix for rate changes
git checkout main
git checkout -b hotfix/1.2.1-emergency-rate-fix

# Apply rate adjustments
# Test calculations
# Fast-track review process

# Deploy immediately after approval
```

## CI/CD Integration

### Automated Version Management

#### On Feature Branch
- Run tests (unit, integration, calculation validation)
- Check code quality
- Build preview artifacts
- **Commercial lending specific**: Validate pricing calculations, risk model accuracy

#### On Develop Branch
- Run full test suite
- Generate development builds
- Tag with pre-release version: `v{next-version}-dev.{build-number}`
- **Commercial lending specific**: Deploy to staging with test portfolios

#### On Release Branch
- Run full test suite
- Generate release candidate: `v{version}-rc.{number}`
- Deploy to staging environment
- Run integration tests
- **Commercial lending specific**: Regulatory compliance validation, stress testing

#### On Main Branch (Tag Push)
- Validate tag format
- Run production tests
- Build release artifacts
- Deploy to production
- Create GitHub release
- Publish documentation
- **Commercial lending specific**: Update pricing sheets, notify rate changes

### Commercial Lending CI Checks
```yaml
# Example CI validation for commercial lending
- name: Validate Commercial Lending Models
  run: |
    python -m pytest tests/test_pricing_models.py
    python -m pytest tests/test_risk_calculations.py
    python -m pytest tests/test_dpd_analysis.py
    python scripts/validate_regulatory_compliance.py

- name: Performance Test Large Portfolios
  run: |
    python scripts/performance_test.py --portfolio-size 100000
    
- name: Validate Export Formats  
  run: |
    python scripts/validate_exports.py --all-formats
```

## Changelog Management

### Commercial Lending Changelog Format
```markdown
# Changelog

## [Unreleased]
### Added
- New commercial real estate pricing tiers
- Enhanced DSCR calculations

## [1.2.0] - 2024-01-15
### Added
- Multi-tier commercial lending pricing matrix
- Industry-specific risk adjustments
- Geographic risk premium calculations
- Enhanced collateral valuation models

### Changed
- Improved DPD calculation performance for large portfolios
- Updated export file naming with regulatory timestamps
- Enhanced risk-based pricing granularity

### Deprecated
- Legacy pricing configuration format (removal in 2.0.0)
- Single-tier risk model (replaced by multi-factor model)

### Removed
- Deprecated consumer lending endpoints
- Legacy DPD bucket definitions

### Fixed
- Commercial loan tenor calculation edge cases
- Memory optimization for portfolios >500K loans
- Risk weight calculation for secured loans

### Security
- Enhanced PII masking for commercial customer data
- Updated encryption for sensitive financial data

### Regulatory
- CECL compliance implementation
- Basel III capital adequacy calculations
- Enhanced stress testing capabilities
```

## Version Support Policy

### Commercial Lending Release Types

#### Standard Releases
- Full feature releases with new functionality
- Support timeline: 18 months

#### Regulatory Releases  
- Compliance-focused releases
- Extended support: 36 months
- Tagged with `-regulatory` suffix

#### Long-Term Support (LTS)
- Major versions receive security updates for 3 years
- Regulatory compliance updates for 5 years
- LTS versions tagged with `-lts` suffix
- Example: `v2.0.0-lts`

### Support Timeline
- **Current Release**: Full support (features + bugfixes + security + regulatory)
- **Previous Major**: Security and regulatory updates only  
- **LTS Releases**: Security and regulatory updates for extended period
- **Older Releases**: No longer supported

## Commercial Lending Documentation

### Release Documentation Requirements
- **Pricing Model Changes**: Detailed impact analysis
- **Risk Calculation Updates**: Mathematical formulations
- **Regulatory Compliance**: Compliance mapping documents
- **Performance Benchmarks**: Before/after performance metrics
- **Migration Guides**: Step-by-step upgrade instructions

### Version-Specific Artifacts
- Pricing matrices (CSV files)
- Risk model documentation
- Regulatory compliance reports
- Performance benchmarks
- API documentation with examples

## Deployment Considerations

### Production Deployment Checklist
- [ ] Backup current configuration files
- [ ] Validate pricing model calculations
- [ ] Test export generation with production data sample
- [ ] Verify regulatory compliance
- [ ] Performance test with expected load
- [ ] Rollback plan prepared
- [ ] Stakeholder notification sent
- [ ] Documentation updated

### Emergency Procedures
- **Rate Changes**: Can be deployed via hotfix with expedited approval
- **Regulatory Changes**: May require immediate deployment
- **Security Issues**: Emergency deployment process available
- **Data Issues**: Rollback procedures documented

This comprehensive versioning strategy ensures reliable, compliant, and auditable releases for the Commercial-View commercial lending platform.
