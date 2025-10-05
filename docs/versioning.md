# Versioning Strategy

## Overview

This document defines the versioning strategy, release workflow, and tagging conventions for the Commercial-View project.

## Version Numbering

### Semantic Versioning (SemVer)

We follow [Semantic Versioning 2.0.0](https://semver.org/) with the format:

```
MAJOR.MINOR.PATCH[-PRERELEASE][+BUILD-METADATA]
### Version Components

#### MAJOR (X.0.0)
Increment when making incompatible API changes or major breaking changes:
- Changes to configuration file structure that require migration
- Breaking changes to export formats
- Changes to DPD calculation methodology
- Major architectural changes

#### MINOR (0.X.0)
Increment when adding functionality in a backwards-compatible manner:
- New KPI metrics
- New export formats
- New configuration options (with defaults)
- Enhanced masking strategies
- Performance improvements

#### PATCH (0.0.X)
Increment when making backwards-compatible bug fixes:
- Bug fixes
- Security patches
- Documentation updates
- Minor performance optimizations

#### Pre-release Identifiers
- `alpha`: Early development, unstable
- `beta`: Feature complete, testing phase
- `rc` (Release Candidate): Production-ready, final testing

**Examples:**
- `2.0.0-alpha.1`
- `2.0.0-beta.2`
- `2.0.0-rc.1`

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

### Tag Naming Rules
1. Always prefix with lowercase `v`
2. Use semantic version numbers
3. No spaces in tag names
4. Use hyphens for pre-release identifiers
5. Include descriptive suffix for special releases (e.g., `-hotfix`, `-lts`)

### Creating Tags
```bash
# Create annotated tag for releases
git tag -a v1.2.3 -m "Release version 1.2.3 - Description of changes"

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

#### `develop`

- Integration branch for features
- Contains latest delivered development changes
- Source for next release

### Supporting Branches

#### Feature Branches

- **Format**: `feature/{issue-number}-{short-description}`
- **Example**: `feature/123-add-new-kpi-metrics`
- Branch from: `develop`
- Merge to: `develop`
- Naming: lowercase with hyphens

#### Release Branches

- **Format**: `release/{version}`
- **Example**: `release/1.2.0`
- Branch from: `develop`
- Merge to: `main` and `develop`
- Purpose: Prepare new production release

#### Hotfix Branches

- **Format**: `hotfix/{version}`
- **Example**: `hotfix/1.2.1`
- Branch from: `main`
- Merge to: `main` and `develop`
- Purpose: Quick production fixes

#### Bugfix Branches

- **Format**: `bugfix/{issue-number}-{short-description}`
- **Example**: `bugfix/456-fix-dpd-calculation`
- Branch from: `develop`
- Merge to: `develop`

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
- `package.json` (if applicable)
- Documentation

#### 3. Update Changelog

Update `CHANGELOG.md` with:

- Release version and date
- New features
- Bug fixes
- Breaking changes
- Deprecations

#### 4. Test Release Candidate

- Run full test suite
- Perform integration testing
- Conduct security scan
- Review documentation

#### 5. Finalize Release

```bash
# Merge to main
git checkout main
git merge --no-ff release/1.2.0
git tag -a v1.2.0 -m "Release version 1.2.0"

# Merge back to develop
git checkout develop
git merge --no-ff release/1.2.0

# Push changes and tags
git push origin main develop --tags

# Delete release branch
git branch -d release/1.2.0
git push origin --delete release/1.2.0
```

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
```

## CI/CD Integration

### Automated Version Management

#### On Feature Branch

- Run tests
- Check code quality
- Build preview artifacts

#### On Develop Branch

- Run full test suite
- Generate development builds
- Tag with pre-release version: `v{next-version}-dev.{build-number}`

#### On Release Branch

- Run full test suite
- Generate release candidate: `v{version}-rc.{number}`
- Deploy to staging environment
- Run integration tests

#### On Main Branch (Tag Push)

- Validate tag format
- Run production tests
- Build release artifacts
- Deploy to production
- Create GitHub release
- Publish documentation

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
```

## Changelog Management

### Changelog Format

Follow [Keep a Changelog](https://keepachangelog.com/) format:

```markdown
# Changelog

## [Unreleased]
### Added
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
```

## Version Support Policy

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
