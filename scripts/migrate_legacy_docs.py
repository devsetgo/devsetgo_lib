#!/usr/bin/env python3
"""
Migration script to preserve existing documentation as a versioned release
and set up Mike versioning structure for DevSetGo Library.

This script will:
1. Backup existing documentation from gh-pages
2. Create a versioned structure using Mike
3. Preserve your current docs as version 2025.5.4.1 (or detected version)
4. Set up the new versioning system
"""

import os
import sys
import subprocess
import shutil
import json
from pathlib import Path


def run_command(cmd, description, check=True):
    """Run a shell command with error handling."""
    print(f"\n🔧 {description}")
    print(f"   Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, check=check, capture_output=True, text=True, shell=isinstance(cmd, str))
        if result.stdout:
            print(f"   Output: {result.stdout.strip()}")
        return result
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Error: {e}")
        if e.stderr:
            print(f"   Stderr: {e.stderr}")
        if not check:
            return None
        raise


def get_legacy_version():
    """Determine what version to assign to the legacy documentation."""
    # Based on user input, the current published docs are 2025.5.4.1
    return "2025.5.4.1"


def backup_current_branch():
    """Create a backup of the current branch state."""
    print("\n💾 Creating backup of current branch...")
    current_branch = subprocess.run(["git", "branch", "--show-current"], 
                                   capture_output=True, text=True).stdout.strip()
    print(f"   Current branch: {current_branch}")
    return current_branch


def switch_to_gh_pages():
    """Switch to gh-pages branch and examine current state."""
    print("\n🔄 Switching to gh-pages branch...")
    
    # First try to switch to existing branch
    result = run_command(["git", "checkout", "gh-pages"], "Switching to existing gh-pages branch", check=False)
    
    if result and result.returncode == 0:
        print("   ✅ Switched to existing gh-pages branch")
        # Fetch and reset to latest remote state
        run_command(["git", "fetch", "origin", "gh-pages"], "Fetching latest from remote", check=False)
        run_command(["git", "reset", "--hard", "origin/gh-pages"], "Resetting to remote state", check=False)
        return
    
    # If that failed, try to fetch and then switch
    print("   📥 Fetching gh-pages from remote...")
    fetch_result = run_command(["git", "fetch", "origin", "gh-pages:gh-pages"], "Fetching gh-pages branch", check=False)
    
    if fetch_result and fetch_result.returncode == 0:
        run_command(["git", "checkout", "gh-pages"], "Switching to fetched branch")
    else:
        print("   ⚠️  No remote gh-pages branch found. The versioning might not be set up yet.")
        print("   This is normal for new repositories. You can proceed with regular deployment.")
        raise Exception("No gh-pages branch available")


def identify_legacy_content():
    """Identify content that's not part of mike's version directories."""
    print("\n🔍 Identifying current Mike structure...")

    # Check if versions.json exists (indicates Mike is already set up)
    if os.path.exists("versions.json"):
        print("   📋 Found existing Mike structure!")
        with open("versions.json", "r") as f:
            versions = json.load(f)
        
        print(f"   Current versions: {[v['version'] for v in versions]}")
        
        # Check if we have the correct version (2025.5.4.1)
        target_version = "2025.5.4.1"
        current_versions = [v['version'] for v in versions]
        
        if target_version in current_versions:
            print(f"   ✅ Version {target_version} already exists!")
            return set(), True  # No migration needed, Mike already set up correctly
        else:
            print(f"   ⚠️  Expected version {target_version} not found.")
            print(f"   Current structure needs to be corrected.")
            return set(), False  # Need to fix the Mike structure
    
    # If no versions.json, we have traditional MkDocs structure
    print("   📋 Found traditional MkDocs structure")
    
    # Mike-managed directories and files
    mike_items = {
        "versions.json", "index.html", ".nojekyll",  # Mike management files
    }

    # Get all items in gh-pages root
    if not os.path.exists("."):
        print("   No gh-pages content found")
        return set(), False
        
    all_items = set(os.listdir("."))

    # Remove git and development artifacts that shouldn't be migrated  
    ignore_items = {
        ".git", ".gitignore", "README.md", ".coverage", "__pycache__", 
        ".pytest_cache", ".ruff_cache", ".vscode"
    }

    # Version directories (these would be YYYY.M.D.N format)
    version_dirs = {item for item in all_items 
                   if os.path.isdir(item) and 
                   len(item.split('.')) >= 3 and 
                   item.replace('.', '').replace('-', '').isdigit()}

    # Legacy content = all items - mike items - ignore items - version dirs
    legacy_items = all_items - mike_items - ignore_items - version_dirs

    print(f"   All items found: {sorted(all_items)}")
    print(f"   Version directories: {sorted(version_dirs)}")
    print(f"   Legacy content to migrate: {sorted(legacy_items)}")
    
    return legacy_items, False


def create_legacy_version(legacy_items, target_version="2025.5.4.1"):
    """Create a version directory for legacy documentation."""
    print(f"\n📦 Creating legacy version: {target_version}")
    
    if not legacy_items:
        print("   No legacy content to migrate")
        return False
    
    version_dir = Path(target_version)
    if version_dir.exists():
        print(f"   Removing existing {target_version} directory...")
        shutil.rmtree(version_dir)
    
    version_dir.mkdir()
    
    # Copy legacy content to version directory
    for item in legacy_items:
        item_path = Path(item)
        target_path = version_dir / item
        
        if item_path.is_file():
            print(f"   Copying file: {item} -> {target_path}")
            shutil.copy2(item_path, target_path)
        elif item_path.is_dir():
            print(f"   Copying directory: {item} -> {target_path}")
            shutil.copytree(item_path, target_path)
    
    print(f"   ✅ Legacy content migrated to {target_version}/")
    return True


def initialize_mike_structure(target_version="2025.5.4.1"):
    """Initialize mike's versioning structure."""
    print(f"\n🚀 Initializing Mike structure with {target_version}...")
    
    # Create versions.json
    versions_data = [
        {
            "version": target_version,
            "title": f"{target_version}",
            "aliases": ["latest", "stable"]
        }
    ]
    
    with open("versions.json", "w") as f:
        json.dump(versions_data, f, indent=2)
    print("   ✅ Created versions.json")
    
    # Create index.html that redirects to the default version
    index_html = f'''<!DOCTYPE html>
<html>
<head>
    <meta http-equiv="refresh" content="0; url=./{target_version}/">
    <meta charset="utf-8">
    <title>Redirecting...</title>
</head>
<body>
    <p>Redirecting to <a href="./{target_version}/">latest documentation</a>...</p>
</body>
</html>'''
    
    with open("index.html", "w") as f:
        f.write(index_html)
    print("   ✅ Created index.html redirect")
    
    # Create .nojekyll file
    Path(".nojekyll").touch()
    print("   ✅ Created .nojekyll")
    
    # Create symlinks for aliases
    if os.name != 'nt':  # Unix-like systems
        try:
            if os.path.exists("latest"):
                os.unlink("latest")
            os.symlink(target_version, "latest")
            print("   ✅ Created 'latest' symlink")
            
            if os.path.exists("stable"):
                os.unlink("stable")
            os.symlink(target_version, "stable")
            print("   ✅ Created 'stable' symlink")
        except Exception as e:
            print(f"   ⚠️  Could not create symlinks: {e}")


def correct_mike_structure(target_version="2025.5.4.1"):
    """Correct existing Mike structure to use the right version."""
    print(f"\n🔧 Correcting Mike structure to use version {target_version}...")
    
    # Read current versions.json
    with open("versions.json", "r") as f:
        versions = json.load(f)
    
    current_versions = [v['version'] for v in versions]
    print(f"   Current versions: {current_versions}")
    
    # Find the version directory that contains the actual documentation
    doc_version = None
    for version in current_versions:
        version_dir = Path(version)
        if version_dir.exists() and version_dir.is_dir():
            doc_version = version
            break
    
    if doc_version and doc_version != target_version:
        print(f"   📦 Renaming version directory: {doc_version} -> {target_version}")
        
        # Rename the version directory
        if Path(target_version).exists():
            shutil.rmtree(Path(target_version))
        
        Path(doc_version).rename(Path(target_version))
        
        # Update symlinks
        for link_name in ["latest", "stable"]:
            if os.path.exists(link_name):
                if os.path.islink(link_name):
                    os.unlink(link_name)
                else:
                    shutil.rmtree(link_name)
            os.symlink(target_version, link_name)
            print(f"   🔗 Updated {link_name} symlink -> {target_version}")
        
        # Update versions.json
        updated_versions = [
            {
                "version": target_version,
                "title": f"{target_version}",
                "aliases": ["latest", "stable"]
            }
        ]
        
        with open("versions.json", "w") as f:
            json.dump(updated_versions, f, indent=2)
        
        print(f"   ✅ Updated versions.json to use {target_version}")
        
        return True
    
    return False


def clean_legacy_content(legacy_items):
    """Remove legacy content from gh-pages root."""
    print(f"\n🧹 Cleaning up legacy content...")
    
    for item in legacy_items:
        item_path = Path(item)
        if item_path.exists():
            if item_path.is_file():
                print(f"   Removing file: {item}")
                item_path.unlink()
            elif item_path.is_dir():
                print(f"   Removing directory: {item}")
                shutil.rmtree(item_path)
    
    print("   ✅ Legacy content cleanup complete")


def commit_changes(target_version="2025.5.4.1"):
    """Commit the migration changes."""
    print(f"\n💾 Committing migration to git...")
    
    run_command(["git", "add", "."], "Adding all changes")
    
    commit_message = f"Migrate to Mike versioning structure\n\n- Preserve existing docs as version {target_version}\n- Initialize Mike versioning system\n- Set up version aliases (latest, stable)"
    
    run_command(["git", "commit", "-m", commit_message], "Committing changes")
    print("   ✅ Changes committed")


def return_to_original_branch(original_branch):
    """Return to the original working branch."""
    print(f"\n🔄 Returning to original branch: {original_branch}")
    run_command(["git", "checkout", original_branch], f"Switching back to {original_branch}")


def main():
    """Main migration function."""
    print("🚀 DevSetGo Library Documentation Migration to Mike Versioning")
    print("=" * 60)
    
    # Determine target version for legacy docs
    target_version = get_legacy_version()
    print(f"\n📋 Migration Plan:")
    print(f"   • Legacy docs will be preserved as version: {target_version}")
    print(f"   • Mike versioning structure will be initialized")
    print(f"   • Aliases 'latest' and 'stable' will point to {target_version}")
    
    # Confirm before proceeding
    response = input(f"\n❓ Proceed with migration? (y/N): ").strip().lower()
    if response != 'y':
        print("Migration cancelled.")
        return
    
    try:
        # Step 1: Backup current state
        original_branch = backup_current_branch()
        
        # Step 2: Switch to gh-pages
        switch_to_gh_pages()
        
        # Step 3: Identify what needs to be migrated or corrected
        legacy_items, mike_setup_correctly = identify_legacy_content()
        
        if mike_setup_correctly:
            print(f"\n✅ Mike versioning is already set up correctly!")
            print(f"   Version {target_version} is properly configured.")
            print("   No migration needed.")
            return_to_original_branch(original_branch)
            return
        
        # Check if we have a Mike structure that needs correction
        if os.path.exists("versions.json"):
            print(f"\n🔧 Mike structure exists but needs correction...")
            correction_made = correct_mike_structure(target_version)
            if correction_made:
                commit_changes(target_version)
                return_to_original_branch(original_branch)
                print(f"\n🎉 Mike structure corrected successfully!")
                print(f"   • Documentation now uses version {target_version}")
                print(f"   • Aliases 'latest' and 'stable' point to {target_version}")
                return
        
        if not legacy_items:
            print("\n⚠️  No legacy content found to migrate!")
            print("   The gh-pages branch might be empty or already set up.")
            print("   You can proceed with regular documentation deployment.")
            return_to_original_branch(original_branch)
            return
        
        # Step 4: Create version directory with legacy content
        migration_successful = create_legacy_version(legacy_items, target_version)
        
        if not migration_successful:
            print("   Migration failed - no content to migrate")
            return_to_original_branch(original_branch)
            return
        
        # Step 5: Initialize Mike structure
        initialize_mike_structure(target_version)
        
        # Step 6: Clean up legacy content from root
        clean_legacy_content(legacy_items)
        
        # Step 7: Commit changes
        commit_changes(target_version)
        
        # Step 8: Return to original branch
        return_to_original_branch(original_branch)
        
        print("\n🎉 Migration completed successfully!")
        print(f"   • Legacy documentation preserved as version {target_version}")
        print(f"   • Mike versioning structure initialized")
        print(f"   • Ready for new versioned deployments")
        print("\n📋 Next steps:")
        print("   1. Run 'make create-docs' to deploy current version")
        print("   2. Visit your GitHub Pages site to see the version selector")
        print("   3. Use version management commands as needed")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        print("   Attempting to return to original branch...")
        try:
            return_to_original_branch(original_branch)
        except:
            pass
        raise


if __name__ == "__main__":
    main()
