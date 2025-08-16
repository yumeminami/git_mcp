---
description: Release automation with versioning and changelog updates
argument-hint: [version] [optional: --dry-run]
allowed-tools: Bash(git *), Edit, MultiEdit, Read, Grep
---

# 🚀 Release Automation

Automate the complete release process including version updates, changelog generation, and Git operations.

**Version:** $ARGUMENTS

## Pre-flight Validation

**First, perform comprehensive pre-flight checks:**

1. **Environment Validation**
   ```bash
   # Check git repository status
   git status --porcelain

   # Verify we're on correct branch (should be main or release branch)
   git branch --show-current

   # Check remote connectivity
   git remote -v
   git ls-remote origin HEAD
   ```

2. **Version Validation**
   - Validate semantic versioning format (e.g., `1.2.3`, `0.1.10`)
   - Check if version already exists as Git tag
   - Ensure version is higher than current version
   - Parse version arguments and dry-run flag

3. **Repository State Check**
   - Ensure working directory is clean (no uncommitted changes)
   - Verify current branch is appropriate for releases
   - Check if remote origin is accessible
   - Validate Git user configuration for tagging

## Version Processing

**Extract and validate version information:**

```bash
# Extract version argument
VERSION=$ARGUMENTS
DRY_RUN=""

# Check for dry-run flag
if [[ "$ARGUMENTS" == *"--dry-run"* ]]; then
    DRY_RUN="--dry-run"
    VERSION=$(echo "$ARGUMENTS" | sed 's/--dry-run//g' | xargs)
fi

# Validate semantic version format
if [[ ! "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "❌ Error: Version must be in semantic format (e.g., 1.2.3)"
    echo "Provided: $VERSION"
    exit 1
fi

# Check if tag already exists
if git tag -l | grep -q "^v$VERSION$"; then
    echo "❌ Error: Version v$VERSION already exists as Git tag"
    echo "Existing tags:"
    git tag -l | grep -E "^v[0-9]+\.[0-9]+\.[0-9]+$" | sort -V | tail -5
    exit 1
fi

# Get current version from pyproject.toml
CURRENT_VERSION=$(grep '^version = ' pyproject.toml | cut -d'"' -f2)
echo "📋 Current version: $CURRENT_VERSION"
echo "🎯 Target version: $VERSION"

# Version comparison (ensure new version is higher)
if [[ "$(printf '%s\n' "$CURRENT_VERSION" "$VERSION" | sort -V | head -n1)" != "$CURRENT_VERSION" ]]; then
    echo "❌ Error: New version $VERSION must be higher than current version $CURRENT_VERSION"
    exit 1
fi
```

## File Updates

**Update version across all project files:**

1. **Update pyproject.toml**
   ```bash
   # Backup current version
   cp pyproject.toml pyproject.toml.backup

   # Update version in pyproject.toml
   sed -i '' "s/^version = \"$CURRENT_VERSION\"/version = \"$VERSION\"/" pyproject.toml

   # Verify update
   NEW_PROJECT_VERSION=$(grep '^version = ' pyproject.toml | cut -d'"' -f2)
   if [[ "$NEW_PROJECT_VERSION" != "$VERSION" ]]; then
       echo "❌ Error: Failed to update pyproject.toml version"
       cp pyproject.toml.backup pyproject.toml
       exit 1
   fi
   ```

2. **Update git_mcp/__init__.py fallback version**
   ```bash
   # Backup current file
   cp git_mcp/__init__.py git_mcp/__init__.py.backup

   # Update fallback version
   sed -i '' "s/__version__ = \"$CURRENT_VERSION\"/__version__ = \"$VERSION\"/" git_mcp/__init__.py

   # Verify update
   if ! grep -q "__version__ = \"$VERSION\"" git_mcp/__init__.py; then
       echo "❌ Error: Failed to update __init__.py version"
       cp git_mcp/__init__.py.backup git_mcp/__init__.py
       cp pyproject.toml.backup pyproject.toml
       exit 1
   fi
   ```

3. **Verify version consistency**
   ```bash
   echo "✅ Version updates completed:"
   echo "   pyproject.toml: $(grep '^version = ' pyproject.toml | cut -d'"' -f2)"
   echo "   __init__.py: $(grep '__version__ = ' git_mcp/__init__.py | cut -d'"' -f2)"
   ```

## Changelog Updates

**Generate new changelog section:**

1. **Parse Current Changelog**
   - Read existing CHANGELOG.md structure
   - Identify unreleased section content
   - Prepare new version section with current date

2. **Generate Release Section**
   ```bash
   # Get current date in YYYY-MM-DD format
   RELEASE_DATE=$(date +%Y-%m-%d)

   # Create new changelog entry
   NEW_SECTION="## [$VERSION] - $RELEASE_DATE"

   # Read current unreleased content
   UNRELEASED_CONTENT=$(sed -n '/## \[Unreleased\]/,/## \[/p' CHANGELOG.md | head -n -1 | tail -n +2)

   # If unreleased section is empty, prompt for release notes
   if [[ -z "$(echo "$UNRELEASED_CONTENT" | xargs)" ]]; then
       echo "⚠️  Warning: No unreleased changes found in CHANGELOG.md"
       echo "Please add release notes manually or update the unreleased section before releasing"
       read -p "Continue with empty release notes? (y/N): " -n 1 -r
       echo
       if [[ ! $REPLY =~ ^[Yy]$ ]]; then
           echo "❌ Release cancelled. Please update CHANGELOG.md first."
           # Restore backups
           cp pyproject.toml.backup pyproject.toml
           cp git_mcp/__init__.py.backup git_mcp/__init__.py
           exit 1
       fi
   fi
   ```

3. **Update Changelog Structure**
   ```bash
   # Backup changelog
   cp CHANGELOG.md CHANGELOG.md.backup

   # Create temporary file with new structure
   {
       # Header
       sed -n '1,/## \[Unreleased\]/p' CHANGELOG.md
       echo

       # New version section
       echo "$NEW_SECTION"
       echo
       echo "$UNRELEASED_CONTENT"
       echo

       # Rest of changelog (skip unreleased section)
       sed -n '/## \[Unreleased\]/,$ p' CHANGELOG.md | tail -n +1 | sed '/^## \[Unreleased\]/,/^$/d'
   } > CHANGELOG.md.tmp

   # Replace original with updated version
   mv CHANGELOG.md.tmp CHANGELOG.md

   # Clear unreleased section
   sed -i '' '/## \[Unreleased\]/,/## \[/{
       /## \[Unreleased\]/!{
           /## \[/!d
       }
   }' CHANGELOG.md
   ```

## Git Operations

**Commit changes and create release tag:**

1. **Commit Version Changes**
   ```bash
   # Add updated files
   git add pyproject.toml git_mcp/__init__.py CHANGELOG.md

   # Create commit with descriptive message
   git commit -m "chore: Release version $VERSION

   - Update version in pyproject.toml and __init__.py
   - Add $VERSION section to CHANGELOG.md
   - Move unreleased changes to $VERSION release notes

   🤖 Generated with Claude Code"

   # Verify commit
   if [[ $? -ne 0 ]]; then
       echo "❌ Error: Failed to commit changes"
       # Restore backups
       cp pyproject.toml.backup pyproject.toml
       cp git_mcp/__init__.py.backup git_mcp/__init__.py
       cp CHANGELOG.md.backup CHANGELOG.md
       exit 1
   fi
   ```

2. **Create Annotated Git Tag**
   ```bash
   # Create annotated tag with release notes
   TAG_MESSAGE="Release version $VERSION

   $(echo "$UNRELEASED_CONTENT" | head -10)

   Full changelog: https://github.com/yumeminami/git_mcp/blob/main/CHANGELOG.md#$(echo $VERSION | tr '.' '')"

   git tag -a "v$VERSION" -m "$TAG_MESSAGE"

   if [[ $? -ne 0 ]]; then
       echo "❌ Error: Failed to create Git tag"
       git reset --hard HEAD~1
       exit 1
   fi
   ```

3. **Push Changes and Tags**
   ```bash
   # Push commit and tags to remote
   echo "🚀 Pushing changes to remote..."
   git push origin HEAD
   git push origin "v$VERSION"

   if [[ $? -ne 0 ]]; then
       echo "❌ Error: Failed to push to remote"
       echo "🔄 Rolling back local changes..."
       git tag -d "v$VERSION"
       git reset --hard HEAD~1
       exit 1
   fi
   ```

## Dry Run Mode

**If --dry-run flag is provided:**

```bash
if [[ -n "$DRY_RUN" ]]; then
    echo "🧪 DRY RUN MODE - No changes will be made"
    echo
    echo "📋 Planned Changes:"
    echo "   Current version: $CURRENT_VERSION → $VERSION"
    echo "   Files to update: pyproject.toml, git_mcp/__init__.py, CHANGELOG.md"
    echo "   Git tag to create: v$VERSION"
    echo "   Commit message: chore: Release version $VERSION"
    echo
    echo "✅ All validations passed. Use without --dry-run to execute release."
    exit 0
fi
```

## Cleanup and Summary

**Clean up backup files and provide release summary:**

```bash
# Remove backup files
rm -f pyproject.toml.backup git_mcp/__init__.py.backup CHANGELOG.md.backup

# Display release summary
echo
echo "🎉 Release $VERSION completed successfully!"
echo
echo "📋 Release Summary:"
echo "   ✅ Version updated: $CURRENT_VERSION → $VERSION"
echo "   ✅ Files updated: pyproject.toml, git_mcp/__init__.py, CHANGELOG.md"
echo "   ✅ Git tag created: v$VERSION"
echo "   ✅ Changes pushed to remote"
echo
echo "🔗 Next Steps:"
echo "   • GitHub/GitLab will automatically create a release from the tag"
echo "   • CI/CD pipeline will build and publish to PyPI"
echo "   • Monitor the release deployment process"
echo "   • Update any dependent projects with new version"
echo
echo "📍 Release URL: https://github.com/yumeminami/git_mcp/releases/tag/v$VERSION"
```

## Error Handling

**Comprehensive error recovery:**

- **Validation Failures**: Exit early with clear error messages
- **File Update Failures**: Restore from backups, exit with error
- **Git Operation Failures**: Rollback commits/tags, restore files
- **Network Failures**: Provide manual recovery instructions
- **Partial State**: Always restore to clean state before exit

**Manual Recovery Instructions:**

```bash
# If release fails partway through:
echo "🔧 Manual Recovery Instructions:"
echo "   1. Check git status: git status"
echo "   2. Restore files: git checkout HEAD -- pyproject.toml git_mcp/__init__.py CHANGELOG.md"
echo "   3. Remove tag if created: git tag -d v$VERSION"
echo "   4. Reset commit if made: git reset --hard HEAD~1"
echo "   5. Clean workspace: git clean -fd"
```

## Usage Examples

```bash
# Standard release
/release 1.2.3

# Test release with dry-run
/release 1.2.3 --dry-run

# Major version release
/release 2.0.0

# Patch release
/release 1.2.4
```
