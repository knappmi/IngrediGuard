"""
IngrediGuard versioning information.

This file contains the current version of IngrediGuard.
Version follows semantic versioning (https://semver.org/):
  - MAJOR version for incompatible API changes
  - MINOR version for new functionality in a backwards compatible manner
  - PATCH version for backwards compatible bug fixes
"""

__version__ = '1.1.1'  # Initial personal project version
VERSION_INFO = {
    'major': 1,
    'minor': 1,
    'patch': 1,
    'release': 'beta',
    'build': '',
}

def get_version():
    """Return the version string in format vX.Y.Z[-release][+build]."""
    version = f"v{VERSION_INFO['major']}.{VERSION_INFO['minor']}.{VERSION_INFO['patch']}"
    if VERSION_INFO['release']:
        version += f"-{VERSION_INFO['release']}"
    if VERSION_INFO['build']:
        version += f"+{VERSION_INFO['build']}"
    return version

def get_short_version():
    """Return just the numeric version string X.Y.Z."""
    return f"{VERSION_INFO['major']}.{VERSION_INFO['minor']}.{VERSION_INFO['patch']}"
