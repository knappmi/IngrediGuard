#!/usr/bin/env python
"""
Version Management Script for IngrediGuard.

This script helps with updating the version number in version.py
and creating the corresponding Git tag.

Usage:
    python version_bump.py [major|minor|patch] [release]
    
Examples:
    python version_bump.py patch          # Bump patch version
    python version_bump.py minor beta     # Bump minor version, set release to beta
    python version_bump.py major          # Bump major version
"""

import sys
import re
import os
import subprocess
from version import VERSION_INFO, get_version

def get_current_branch():
    """Return the current git branch name."""
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None

def update_version_file(version_type, release=None):
    """Update the version.py file with new version numbers."""
    with open('version.py', 'r') as f:
        content = f.read()
    
    # Update version components
    if version_type == 'major':
        VERSION_INFO['major'] += 1
        VERSION_INFO['minor'] = 0
        VERSION_INFO['patch'] = 0
    elif version_type == 'minor':
        VERSION_INFO['minor'] += 1
        VERSION_INFO['patch'] = 0
    elif version_type == 'patch':
        VERSION_INFO['patch'] += 1
    
    # Update release type if specified
    if release is not None:
        VERSION_INFO['release'] = release
    
    # Create new version string
    version_str = f"{VERSION_INFO['major']}.{VERSION_INFO['minor']}.{VERSION_INFO['patch']}"
    
    # Update the version in the file
    content = re.sub(
        r"__version__ = ['\"].*?['\"]",
        f"__version__ = '{version_str}'",
        content
    )
    
    # Update the version info dictionary
    for key, value in VERSION_INFO.items():
        if isinstance(value, str):
            content = re.sub(
                rf"'{key}': ['\"].*?['\"]",
                f"'{key}': '{value}'",
                content
            )
        else:
            content = re.sub(
                rf"'{key}': \d+",
                f"'{key}': {value}",
                content
            )
    
    with open('version.py', 'w') as f:
        f.write(content)
    
    return get_version()

def create_git_tag(version):
    """Create a Git tag for the new version."""
    try:
        current_branch = get_current_branch()
        
        # Add the version file
        subprocess.run(['git', 'add', 'version.py'], check=True)
        
        # Commit the change
        subprocess.run(['git', 'commit', '-m', f'Bump version to {version}'], check=True)
        
        # Create the tag
        subprocess.run(['git', 'tag', version], check=True)
        
        print(f"\nGit tag '{version}' created successfully!")
        print("\nTo push the new version to the repository, run:")
        print(f"  git push origin {current_branch} {version}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error creating git tag: {e}")
        return False

def main():
    """Process command line arguments and update version."""
    if len(sys.argv) < 2 or sys.argv[1] not in ['major', 'minor', 'patch']:
        print(__doc__)
        return 1
    
    # Check if we're on the main branch
    current_branch = get_current_branch()
    if current_branch != "main":
        print(f"Error: You are currently on branch '{current_branch}'")
        print("Version bumping should only be performed on the main branch.")
        
        # Allow override with force flag
        if len(sys.argv) > 2 and sys.argv[-1] == "--force":
            print("\nForce flag detected. Proceeding anyway...\n")
        else:
            print("\nIf you're absolutely sure you want to proceed anyway, run with --force")
            print("Example: python version_bump.py patch --force")
            return 1
    
    version_type = sys.argv[1]
    
    # Check if release is specified (but not a --force flag)
    release = None
    if len(sys.argv) > 2 and sys.argv[2] != "--force":
        release = sys.argv[2]
    
    print(f"Current version: {get_version()}")
    
    # Update version
    new_version = update_version_file(version_type, release)
    print(f"New version: {new_version}")
    
    # Ask for confirmation
    confirm = input("\nCreate git tag for this version? [y/N]: ")
    if confirm.lower() == 'y':
        create_git_tag(new_version)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
