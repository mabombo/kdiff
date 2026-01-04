<div align="center">
  <img src="loghi/kdiff_logo_3.png" alt="kdiff logo" width="300"/>
</div>

# Contributing to kdiff

Thank you for considering contributing to kdiff! This document outlines our development workflow and guidelines.

## 🔄 Development Workflow

### Branch Strategy

We use a simple but effective branching model:

- **`main`** - Production-ready code, always stable
- **`feature/xxx`** - New features
- **`fix/xxx`** - Bug fixes
- **`docs/xxx`** - Documentation updates

### Getting Started

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/mabombo/kdiff.git
   cd kdiff
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/bug-description
   ```

3. **Make your changes**
   - Write clean, documented code
   - Follow existing code style
   - Add tests if applicable

4. **Commit your changes** (see commit conventions below)
   ```bash
   git add .
   git commit -m "feat: Add your feature description"
   ```

5. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request**
   - Provide clear description of changes
   - Reference any related issues
   - Wait for review

## 📝 Commit Message Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/) for clear and structured commit history.

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation only changes
- **style**: Code style changes (formatting, semicolons, etc.)
- **refactor**: Code change that neither fixes a bug nor adds a feature
- **perf**: Performance improvement
- **test**: Adding or updating tests
- **chore**: Changes to build process, dependencies, etc.

### Examples

```bash
feat: Add multi-namespace comparison support

Allows comparing multiple namespaces in a single run by accepting
comma-separated namespace list in -n option.

Closes #42
```

```bash
fix: Correct Docker library path resolution

Libraries were not found in container due to incorrect path.
Changed copy destination from /app/lib to /usr/local/lib.
```

```bash
docs: Update installation instructions for Docker
```

## 🔖 Versioning

We use [Semantic Versioning](https://semver.org/):

- **MAJOR** (x.0.0) - Breaking changes
- **MINOR** (0.x.0) - New features, backward compatible
- **PATCH** (0.0.x) - Bug fixes, backward compatible

## 🚀 Creating a Release

### Method 1: Automated (Recommended)

Use the release script:

```bash
# Interactive mode - will prompt for version type
./release.sh

# Or specify version directly
./release.sh 1.2.0

# Or specify type
./release.sh 1.2.0 minor
```

The script will:
1. Run pre-flight checks
2. Update CHANGELOG.md
3. Update version in all files
4. Create git tag
5. Push to remote
6. Build and publish Docker image

### Method 2: Manual

```bash
# 1. Update version in files
./version-bump.sh minor  # or patch/major

# 2. Update CHANGELOG.md manually
# Add your changes under [Unreleased] section

# 3. Commit changes
git add -A
git commit -m "chore: Bump version to 1.1.0"

# 4. Create and push tag
git tag -a v1.1.0 -m "Release v1.1.0"
git push origin main
git push origin v1.1.0

# 5. Build and publish Docker
./publish-docker.sh 1.1.0 mabombo
```

## 📋 Pull Request Guidelines

### Before Submitting

- [ ] Code follows existing style
- [ ] All tests pass (run `bash tests/run_tests.sh`)
- [ ] Documentation updated if needed
- [ ] CHANGELOG.md updated under `[Unreleased]`
- [ ] Commit messages follow convention
- [ ] Branch is up to date with main

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix (non-breaking change)
- [ ] New feature (non-breaking change)
- [ ] Breaking change (fix or feature that would cause existing functionality to change)
- [ ] Documentation update

## Testing
How has this been tested?

## Checklist
- [ ] Code follows project style
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Tests added/updated
- [ ] CHANGELOG.md updated
```

## 🧪 Testing

Run tests before submitting:

```bash
# Run all tests
bash tests/run_tests.sh

# Test Docker build
docker build -t kdiff:test .
docker run --rm kdiff:test --help
```

## 🔧 Development Tools

### Available Scripts

- **`release.sh`** - Automated release process
- **`version-bump.sh`** - Update version in files
- **`publish-docker.sh`** - Build and publish Docker image
- **`install.sh`** - Install kdiff locally
- **`tests/run_tests.sh`** - Run test suite

### Code Style

- Use descriptive variable names
- Add comments for complex logic
- Keep functions focused and small
- Follow existing patterns in codebase

## 🐛 Reporting Bugs

Create an issue with:
- Clear title and description
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, kubectl version)
- Relevant logs or screenshots

## 💡 Suggesting Features

Create an issue with:
- Clear use case description
- Why this feature would be useful
- Proposed implementation (if you have ideas)
- Examples of similar features in other tools

## 📞 Questions?

- Open an issue with the `question` label
- Check existing documentation
- Review closed issues for similar questions

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing! 🎉
