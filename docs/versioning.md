# Versioning Strategy

<<<<<<< HEAD
## Overview
=======
[⬅ Documentation Hub](index.md)

## Overview

>>>>>>> fa393d2be80b675bbc0b12c922c156c6c1d27af7
This document defines the versioning strategy, release workflow, and tagging conventions for the Commercial-View project.

## Version Numbering

### Semantic Versioning (SemVer)
<<<<<<< HEAD
=======

>>>>>>> fa393d2be80b675bbc0b12c922c156c6c1d27af7
We follow [Semantic Versioning 2.0.0](https://semver.org/) with the format:

```
MAJOR.MINOR.PATCH[-PRERELEASE][+BUILD-METADATA]
<<<<<<< HEAD
=======
```

>>>>>>> fa393d2be80b675bbc0b12c922c156c6c1d27af7
### Version Components

#### MAJOR (X.0.0)
Increment when making incompatible API changes or major breaking changes:
- Changes to configuration file structure that require migration
- Breaking changes to export formats
- Changes to DPD calculation methodology
- Major architectural changes
<<<<<<< HEAD
=======
- **Commercial lending specific**: Changes to pricing models, risk calculation algorithms, regulatory compliance frameworks
>>>>>>> fa393d2be80b675bbc0b12c922c156c6c1d27af7

#### MINOR (0.X.0)
Increment when adding functionality in a backwards-compatible manner:
- New KPI metrics
- New export formats
- New configuration options (with defaults)
- Enhanced masking strategies
- Performance improvements
<<<<<<< HEAD
=======
- **Commercial lending specific**: New pricing tiers, additional risk factors, enhanced collateral types, expanded geographic coverage
>>>>>>> fa393d2be80b675bbc0b12c922c156c6c1d27af7

#### PATCH (0.0.X)
Increment when making backwards-compatible bug fixes:
- Bug fixes
- Security patches
- Documentation updates
- Minor performance optimizations
<<<<<<< HEAD
=======
- **Commercial lending specific**: Rate calculation fixes, DPD bucket corrections, regulatory compliance updates
>>>>>>> fa393d2be80b675bbc0b12c922c156c6c1d27af7

#### Pre-release Identifiers
- `alpha`: Early development, unstable
- `beta`: Feature complete, testing phase
- `rc` (Release Candidate): Production-ready, final testing
<<<<<<< HEAD
=======
- **Commercial lending specific**: `regulatory` (awaiting compliance approval), `audit` (under regulatory review)
>>>>>>> fa393d2be80b675bbc0b12c922c156c6c1d27af7

**Examples:**
- `2.0.0-alpha.1`
- `2.0.0-beta.2`
- `2.0.0-rc.1`
<<<<<<< HEAD
=======
- `2.1.0-regulatory.1` (pending regulatory approval)
>>>>>>> fa393d2be80b675bbc0b12c922c156c6c1d27af7

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
<<<<<<< HEAD
=======
- `v2.3.0-regulatory.1` - Regulatory compliance release
>>>>>>> fa393d2be80b675bbc0b12c922c156c6c1d27af7

### Tag Naming Rules
1. Always prefix with lowercase `v`
2. Use semantic version numbers
3. No spaces in tag names
4. Use hyphens for pre-release identifiers
<<<<<<< HEAD
5. Include descriptive suffix for special releases (e.g., `-hotfix`, `-lts`)
=======
5. Include descriptive suffix for special releases (e.g., `-hotfix`, `-lts`, `-regulatory`)
>>>>>>> fa393d2be80b675bbc0b12c922c156c6c1d27af7

### Creating Tags
```bash
# Create annotated tag for releases
<<<<<<< HEAD
git tag -a v1.2.3 -m "Release version 1.2.3 - Description of changes"
=======
git tag -a v1.2.3 -m "Release version 1.2.3 - Enhanced commercial lending risk models"
>>>>>>> fa393d2be80b675bbc0b12c922c156c6c1d27af7

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
<<<<<<< HEAD
=======
- **Commercial lending specific**: Must pass regulatory compliance checks
>>>>>>> fa393d2be80b675bbc0b12c922c156c6c1d27af7

#### `develop`
- Integration branch for features
- Contains latest delivered development changes
- Source for next release
<<<<<<< HEAD
=======
- **Commercial lending specific**: Includes staging environment deployment
>>>>>>> fa393d2be80b675bbc0b12c922c156c6c1d27af7

### Supporting Branches

#### Feature Branches
- **Format**: `feature/{issue-number}-{short-description}`
<<<<<<< HEAD
- **Example**: `feature/123-add-new-kpi-metrics`
=======
- **Example**: `feature/123-add-commercial-re-pricing`
>>>>>>> fa393d2be80b675bbc0b12c922c156c6c1d27af7
- Branch from: `develop`
- Merge to: `develop`
- Naming: lowercase with hyphens

#### Release Branches
- **Format**: `release/{version}`
- **Example**: `release/1.2.0`
- Branch from: `develop`
- Merge to: `main` and `develop`
- Purpose: Prepare new production release
<<<<<<< HEAD
=======
- **Commercial lending specific**: Includes regulatory compliance validation
>>>>>>> fa393d2be80b675bbc0b12c922c156c6c1d27af7

#### Hotfix Branches
- **Format**: `hotfix/{version}`
- **Example**: `hotfix/1.2.1`
- Branch from: `main`
- Merge to: `main` and `develop`
- Purpose: Quick production fixes
<<<<<<< HEAD

#### Bugfix Branches
- **Format**: `bugfix/{issue-number}-{short-description}`
- **Example**: `bugfix/456-fix-dpd-calculation`
- Branch from: `develop`
- Merge to: `develop`
=======
- **Commercial lending specific**: Emergency regulatory or calculation fixes

#### Regulatory Branches
- **Format**: `regulatory/{version}-{compliance-type}`
- **Example**: `regulatory/2.1.0-basel-iii`
- Branch from: `develop`
- Merge to: `develop` after approval
- Purpose: Regulatory compliance implementations
>>>>>>> fa393d2be80b675bbc0b12c922c156c6c1d27af7

## Release Workflow

### Regular Release Process

#### 1. Prepare Release Branch
```bash
# Create release branch from develop
<<<<<<< HEAD
git checkout develop
=======
git checkout develop  
>>>>>>> fa393d2be80b675bbc0b12c922c156c6c1d27af7
git pull origin develop
git checkout -b release/1.2.0
```

#### 2. Update Version Numbers
Update version in:
- `VERSION` file
- `setup.py` or `pyproject.toml`
<<<<<<< HEAD
- `package.json` (if applicable)
- Documentation
=======
- Configuration files (`configs/pricing_config.yml`)
- API documentation
- **Commercial lending specific**: Pricing model versions, risk calculation versions
>>>>>>> fa393d2be80b675bbc0b12c922c156c6c1d27af7

#### 3. Update Changelog
Update `CHANGELOG.md` with:
- Release version and date
<<<<<<< HEAD
- New features
- Bug fixes
- Breaking changes
- Deprecations

#### 4. Test Release Candidate
=======
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
>>>>>>> fa393d2be80b675bbc0b12c922c156c6c1d27af7
- Run full test suite
- Perform integration testing
- Conduct security scan
- Review documentation
<<<<<<< HEAD

#### 5. Finalize Release
=======
- **Commercial lending specific**: Validate against regulatory test cases

#### 6. Finalize Release
>>>>>>> fa393d2be80b675bbc0b12c922c156c6c1d27af7
```bash
# Merge to main
git checkout main
git merge --no-ff release/1.2.0
<<<<<<< HEAD
git tag -a v1.2.0 -m "Release version 1.2.0"
=======
git tag -a v1.2.0 -m "Release version 1.2.0 - Enhanced commercial lending platform"
>>>>>>> fa393d2be80b675bbc0b12c922c156c6c1d27af7

# Merge back to develop
git checkout develop
git merge --no-ff release/1.2.0

# Push changes and tags
git push origin main develop --tags

# Delete release branch
git branch -d release/1.2.0
git push origin --delete release/1.2.0
```

<<<<<<< HEAD
#### 6. Publish Release
- Create GitHub release from tag
- Attach release artifacts
- Publish release notes
- Update documentation

### Hotfix Release Process

#### 1. Create Hotfix Branch
```bash
git checkout main
git pull origin main
git checkout -b hotfix/1.2.1
```

#### 2. Apply Fix and Test
```bash
# Make necessary changes
# Run tests
# Update version and changelog
```

#### 3. Finalize Hotfix
```bash
# Merge to main
git checkout main
git merge --no-ff hotfix/1.2.1
git tag -a v1.2.1 -m "Hotfix version 1.2.1"

# Merge to develop
git checkout develop
git merge --no-ff hotfix/1.2.1

# Push and cleanup
git push origin main develop --tags
git branch -d hotfix/1.2.1
git push origin --delete hotfix/1.2.1
=======
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
>>>>>>> fa393d2be80b675bbc0b12c922c156c6c1d27af7
```

## CI/CD Integration

### Automated Version Management

#### On Feature Branch
<<<<<<< HEAD
- Run tests
- Check code quality
- Build preview artifacts
=======
- Run tests (unit, integration, calculation validation)
- Check code quality
- Build preview artifacts
- **Commercial lending specific**: Validate pricing calculations, risk model accuracy
>>>>>>> fa393d2be80b675bbc0b12c922c156c6c1d27af7

#### On Develop Branch
- Run full test suite
- Generate development builds
- Tag with pre-release version: `v{next-version}-dev.{build-number}`
<<<<<<< HEAD
=======
- **Commercial lending specific**: Deploy to staging with test portfolios
>>>>>>> fa393d2be80b675bbc0b12c922c156c6c1d27af7

#### On Release Branch
- Run full test suite
- Generate release candidate: `v{version}-rc.{number}`
- Deploy to staging environment
- Run integration tests
<<<<<<< HEAD
=======
- **Commercial lending specific**: Regulatory compliance validation, stress testing
>>>>>>> fa393d2be80b675bbc0b12c922c156c6c1d27af7

#### On Main Branch (Tag Push)
- Validate tag format
- Run production tests
- Build release artifacts
- Deploy to production
- Create GitHub release
- Publish documentation
<<<<<<< HEAD

### Version Validation in CI
```yaml
# Example CI check for version consistency
- name: Validate Version
  run: |
    VERSION_FILE=$(cat VERSION)
    VERSION_TAG=${GITHUB_REF#refs/tags/v}
    if [ "$VERSION_FILE" != "$VERSION_TAG" ]; then
      echo "Version mismatch: $VERSION_FILE != $VERSION_TAG"
      exit 1
    fi
=======
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
>>>>>>> fa393d2be80b675bbc0b12c922c156c6c1d27af7
```

## Changelog Management

<<<<<<< HEAD
### Changelog Format
Follow [Keep a Changelog](https://keepachangelog.com/) format:

=======
### Commercial Lending Changelog Format
>>>>>>> fa393d2be80b675bbc0b12c922c156c6c1d27af7
```markdown
# Changelog

## [Unreleased]
### Added
<<<<<<< HEAD
- New features in development

## [1.2.0] - 2023-12-01
### Added
- New KPI metric for portfolio health
- Support for additional pricing bands

### Changed
- Improved DPD calculation performance
- Updated export file naming convention

### Deprecated
- Old pricing configuration format (will be removed in 2.0.0)

### Removed
- Deprecated API endpoints

### Fixed
- Bug in bucket classification for edge cases
- Memory leak in large portfolio processing

### Security
- Updated dependencies with security vulnerabilities
=======
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
>>>>>>> fa393d2be80b675bbc0b12c922c156c6c1d27af7
```

## Version Support Policy

<<<<<<< HEAD
### Long-Term Support (LTS)
- Major versions receive security updates for 2 years
- LTS versions tagged with `-lts` suffix
- Example: `v1.0.0-lts`

### Support Timeline
- **Current Release**: Full support (features + bugfixes + security)
- **Previous Major**: Security updates only
- **Older Releases**: No longer supported

### End of Life (EOL)
- Announced 6 months in advance
- Security updates only during notice period
- No updates after EOL date

## Version Documentation

### Documentation Versioning
- Maintain docs for current and previous major versions
- Use version switcher in documentation site
- Archive old version docs

### Release Notes
Include in each release:
- Version number and date
- Summary of changes
- Upgrade instructions
- Breaking changes
- Known issues
- Deprecation notices

## Tools and Automation

### Recommended Tools
- **bump2version**: Automate version bumping
- **semantic-release**: Automated version management and changelog generation
- **git-flow**: Git workflow automation
- **GitHub Actions**: CI/CD automation

### Version File
Maintain a `VERSION` file at repository root:
```
1.2.3
```

This file is the single source of truth for the current version.
=======
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
>>>>>>> fa393d2be80b675bbc0b12c922c156c6c1d27af7
