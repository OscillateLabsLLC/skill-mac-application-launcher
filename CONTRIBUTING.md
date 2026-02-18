# Contributing to Mac Application Launcher

Thanks for your interest in contributing!

**Note:** This project is in **Security Fixes Only** status. We accept:

- Security vulnerability fixes
- Critical bug fixes
- Dependency updates for security

We are **not** accepting new features or enhancements at this time.

## Development Setup

### Prerequisites

- macOS 10.15+ (required for AppleScript functionality)
- Python 3.9+
- [uv](https://github.com/astral-sh/uv) package manager
- [just](https://github.com/casey/just) task runner (optional but recommended)

### Getting Started

```bash
git clone https://github.com/OscillateLabsLLC/skill-mac-application-launcher
cd skill-mac-application-launcher

# Install development dependencies
uv sync --group dev
# or using just
just install
```

### Running Locally

This skill requires a running OVOS or Neon instance to test properly. For unit tests:

```bash
just test
# or
uv run pytest
```

## Common Commands

```bash
# Install dependencies
just install

# Run tests
just test

# Run tests with coverage
just test-cov

# Run all quality checks (format, lint, test)
just check

# Format code
just format

# Lint code
just lint

# Build package
just build

# Clean build artifacts
just clean

# Show all available commands
just --list
```

Or run commands directly with uv:

```bash
# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=skill_mac_application_launcher --cov-report=term-missing

# Run linter
uv run ruff check .

# Format code
uv run ruff format .
```

## Code Style

This project uses:

- **Formatting**: `ruff format` (line length: 119)
- **Linting**: `ruff` with pycodestyle, pyflakes, and isort rules
- **Type Checking**: `mypy` with strict type checking enabled

All code must pass linting and type checking before merging.

## Testing

We use pytest with coverage reporting:

```bash
# Run all tests with coverage
pytest --cov=skill_mac_application_launcher --cov-report=term-missing

# Run specific test
pytest tests/test_specific.py::test_name
```

## Security Vulnerabilities

If you discover a security vulnerability, please:

1. **Do not** open a public issue
2. Email mike@oscillatelabs.net with details
3. Include steps to reproduce if possible
4. Allow time for a patch before public disclosure

## Pull Requests

For security fixes and critical bugs:

1. Create a feature branch: `git checkout -b fix/security-issue`
2. Make your changes and add tests
3. Run `just check` (or `just format && just lint && just test`)
4. Ensure all tests pass
5. Commit using [Conventional Commits](https://www.conventionalcommits.org/) (e.g., `fix:`, `chore:`)
6. Push to your fork
7. Open a pull request with clear description of the security issue or bug

**PR Guidelines:**

- Include detailed description of the vulnerability or bug
- Add tests demonstrating the fix
- Update documentation if needed
- Ensure all CI checks pass

## Commit Messages

Use [Conventional Commits](https://www.conventionalcommits.org/) format:

```
fix: resolve command injection vulnerability in app launcher
fix: prevent race condition in process termination
chore: update dependencies to address CVE-XXXX-XXXXX
```

**Accepted prefixes for this project:**

- `fix:` - Bug fixes and security patches
- `chore:` - Dependency updates and maintenance
- `docs:` - Documentation updates
- `test:` - Test additions or modifications

## Release Process

This project uses [release-please](https://github.com/googleapis/release-please) for automated versioning:

1. Create commits using conventional commit messages
2. Release-please creates a PR with version bump and changelog
3. When the PR is merged, a release is created automatically
4. Package is published to PyPI

## Platform Requirements

This skill is macOS-specific and requires:

- macOS APIs for application management
- AppleScript for window management
- System directories for application discovery

Changes must maintain compatibility with macOS 10.15+.

## Questions?

- Open an issue for security vulnerabilities (privately via email)
- Join the [OpenVoiceOS Matrix chat](https://matrix.to/#/!XFpdtmgyCoPDxOMPpH:matrix.org?via=matrix.org) for questions
- Check existing issues before creating new ones

## Code of Conduct

Be respectful and constructive. We're building tools for the OpenVoiceOS community - professionalism and clear communication are essential.

## License

By contributing, you agree that your contributions will be licensed under the Apache 2.0 License.
