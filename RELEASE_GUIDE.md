<div align="center">
  <img src="loghi/kdiff_logo_3.png" alt="kdiff logo" width="300"/>
</div>

# 🚀 Quick Release Guide

## Daily Workflow

### Working on a Feature

```bash
# 1. Create feature branch
git checkout -b feature/add-filtering

# 2. Make changes and commit
git add .
git commit -m "feat: Add resource type filtering"

# 3. Push and create PR
git push origin feature/add-filtering
# Then create PR on GitHub

# 4. After merge, delete branch
git checkout main
git pull
git branch -d feature/add-filtering
```

### Working on a Bug Fix

```bash
git checkout -b fix/docker-path
# ... make changes ...
git commit -m "fix: Correct Docker library path"
git push origin fix/docker-path
# Create PR
```

## Creating a Release

### Option 1: Fully Automated (Recommended)

```bash
./release.sh
```

The script will:
- ✅ Ask you for version type (major/minor/patch)
- ✅ Check git status
- ✅ Update CHANGELOG.md
- ✅ Update version in files (pyproject.toml, setup.py, Dockerfile)
- ✅ Commit changes
- ✅ Create git tag
- ✅ Push to GitHub
- ✅ Build and publish Docker image

### Option 2: Specify Version

```bash
./release.sh 1.2.0
```

### Option 3: Manual Control

```bash
# 1. Bump version
./version-bump.sh minor  # 1.0.0 -> 1.1.0

# 2. Update CHANGELOG.md
# Edit manually: move items from [Unreleased] to new version section

# 3. Commit
git add -A
git commit -m "chore: Bump version to 1.1.0"

# 4. Create tag
git tag -a v1.1.0 -m "Release v1.1.0: Add filtering support"

# 5. Push
git push origin main
git push origin v1.1.0

# 6. Publish Docker
./publish-docker.sh 1.1.0 mabombo
```

## Commit Message Types

```bash
feat: Add new feature
fix: Fix a bug
docs: Documentation only
style: Formatting changes
refactor: Code restructuring
perf: Performance improvement
test: Add/update tests
chore: Build process, dependencies
```

## Version Numbering

- **1.0.0 → 1.0.1** (patch) - Bug fixes
- **1.0.0 → 1.1.0** (minor) - New features
- **1.0.0 → 2.0.0** (major) - Breaking changes

## Quick Commands

```bash
# Check current version
git describe --tags --abbrev=0

# View commits since last tag
git log $(git describe --tags --abbrev=0)..HEAD --oneline

# View all tags
git tag -l

# Delete local tag
git tag -d v1.0.0

# Delete remote tag
git push origin :refs/tags/v1.0.0

# View release script help
./release.sh --help
```

## CHANGELOG Format

```markdown
## [Unreleased]

### Added
- New feature X

### Changed
- Modified behavior Y

### Fixed
- Bug fix Z

## [1.1.0] - 2026-01-15

### Added
- Feature A
- Feature B
```

## Before Each Release

- [ ] All features tested
- [ ] CHANGELOG.md updated
- [ ] No uncommitted changes
- [ ] All commits pushed
- [ ] Tests passing
- [ ] Documentation updated

## After Release

1. Check Docker Hub: https://hub.docker.com/r/mabombo/kdiff
2. Create GitHub Release with notes
3. Announce release (if applicable)

## Troubleshooting

### "Uncommitted changes detected"
```bash
git status
git add -A
git commit -m "your message"
```

### "Not on main branch"
```bash
git checkout main
git pull
```

### Docker push fails
```bash
docker login
./publish-docker.sh 1.1.0 mabombo
```

### Tag already exists
```bash
# Delete local and remote tag
git tag -d v1.1.0
git push origin :refs/tags/v1.1.0
# Then create release again
```
