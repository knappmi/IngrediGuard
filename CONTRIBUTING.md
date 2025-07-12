# Contributing to IngrediGuard

Thank you for your interest in contributing to IngrediGuard! This document provides guidelines for contributing to the project, with a special focus on versioning.

## Table of Contents

1. [Development Setup](#development-setup)
2. [Versioning Guidelines](#versioning-guidelines)
3. [Creating Releases](#creating-releases)
4. [Pull Request Process](#pull-request-process)
5. [Coding Standards](#coding-standards)

## Development Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/knappmi/IngrediGuard.git
   cd IngrediGuard
   ```

2. Set up a virtual environment:

   ```bash
   python -m venv venv
   # On Windows
   .\venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Versioning Guidelines

IngrediGuard follows [Semantic Versioning](https://semver.org/) (SemVer) principles.

### Version Format

Versions follow the format `vX.Y.Z[-release][+build]` where:

- **X** is the Major version (breaking changes)
- **Y** is the Minor version (new features, backwards compatible)
- **Z** is the Patch version (bug fixes, backwards compatible)
- **release** (optional) is a pre-release designation like `alpha`, `beta`, or `rc.1`
- **build** (optional) is build metadata

### When to Increment Version Numbers

- **Major (X)**: Incompatible API changes, major UI overhauls, or significant functionality changes that might break existing user workflows
- **Minor (Y)**: New features or significant enhancements that maintain backward compatibility
- **Patch (Z)**: Bug fixes and minor improvements that don't add new features

### Pre-release Designations

- **alpha**: Early development versions, expect significant bugs and incomplete features
- **beta**: Feature complete but still testing for bugs
- **rc** (release candidate): Potential final version unless serious bugs are found

## Creating Releases

IngrediGuard includes a versioning utility script that helps manage version changes and Git tags.

### Using the Version Bump Script

The `version_bump.py` script handles versioning tasks automatically:

```bash
# For a patch update (v0.1.0 → v0.1.1)
python version_bump.py patch

# For a minor update (v0.1.0 → v0.2.0)
python version_bump.py minor

# For a major update (v0.1.0 → v1.0.0)
python version_bump.py major

# To set a pre-release designation
python version_bump.py minor beta  # Creates v0.2.0-beta
```

### Release Process

1. **Ensure all changes are committed** to your branch
2. **Run the version bump script** appropriate for your change type
3. When prompted, choose `y` to create the Git tag
4. **Push the changes and tag**:

   ```bash
   git push origin symmantic-versioning  # Or your current branch
   git push origin v1.2.3                # Push the specific tag
   ```

5. **Create a release on GitHub** by:
   - The CI pipeline will automatically create a GitHub Release when you push a tag
   - The release will include automatically built AAB files for Android

### What Happens When You Push a Tag

1. GitHub Actions workflow is triggered
2. A GitHub Release is created with auto-generated release notes
3. The signed AAB file is built and attached to the release

## Pull Request Process

1. Create a feature branch from `main` or `develop`
2. Make your changes with appropriate tests
3. Update documentation as necessary
4. Submit a pull request to the appropriate branch
5. Await code review and address any feedback

## Coding Standards

1. Follow PEP 8 style guidelines for Python code
2. Write meaningful commit messages
3. Include docstrings for functions and classes
4. Write tests for new features or bug fixes
5. Keep dependencies to a minimum

---

## Release Checklist

Before creating a release, ensure the following:

1. All tests pass
2. Documentation is updated
3. CHANGELOG.md is updated (if applicable)
4. Version in `version.py` reflects the correct version
5. Release notes are prepared

Thank you for contributing to IngrediGuard!
