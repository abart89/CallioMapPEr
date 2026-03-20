# Contributing to Calliope

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/contributing/

## Overview

Calliope welcomes contributions from volunteers across various institutions. The project offers multiple ways to get involved, from reporting issues to submitting code changes.

## Ways to Contribute

**Reporting Issues:**
- Report bugs through the GitHub issue tracker with a bug report template
- Document missing or inconsistent information in the documentation
- Request new features or improvements

**Community Engagement:**
- Ask questions and connect with the community on the discussion board
- Review the "good first issues" list for beginner-friendly tasks
- Check GitHub milestones and projects to understand development direction

## Development Setup

### Environment Installation

Using mamba (recommended):

1. Install Mambaforge for your operating system
2. Clone the repository: `git clone git@github.com:calliope-project/calliope.git`
3. Create the development environment with all dependencies
4. Activate the environment and install Calliope in editable mode
5. Install the IPython kernel for documentation testing

For pip users, install with the `dev` option: `pip install -e '.[dev]'`

### Development Tools

**pre-commit:** Runs automatic checks on each commit:
- Prevents staging large files
- Lints Python files
- Formats code to PEP8 standards

**pytest:** Run unit and integration tests with coverage reporting

## Making Changes

### Workflow

1. Fork the main repository on GitHub
2. Clone your fork locally
3. Create a feature branch to isolate your changes
4. Make edits and add tests covering your contribution
5. Run tests: `pytest -m "not time_intensive" --no-cov` for faster feedback
6. Commit changes with clear messages
7. Push to your fork and open a pull request

### Testing Strategy

- Add tests for all new functionality
- Run `pytest` from the repository root
- Use `-x` flag to stop at first failure
- Use `--pdb` flag for debugging
- Integration tests can be skipped with `-m "not time_intensive"`

## Pull Request Requirements

Before submitting, ensure you have:

1. **Test coverage** – Tests prevent future regressions and validate new functionality
2. **Documentation updates** – Added features should be documented in the docs directory
3. **Changelog entry** – Brief description prepended with `fixed`, `changed`, `added`, or `new`
4. **Code coverage** – Maintained or improved overall test coverage percentage

## Code Standards

**Style Guide:** Follow PEP8 with ruff for formatting and linting

**Docstrings:** Use Google-style docstrings for all modules, classes, and methods

**Line Length:** Maximum 88 characters (configured in `pyproject.toml`)

**Automation:** Run `pre-commit install` to automatically format code on each commit

## Release Process

### Creating a Release

1. Create a release branch
2. Update version in `src/calliope/_version.py`
3. Update `CHANGELOG.md` with final version and date
4. Submit PR titled `Release vX.Y.Z` for testing
5. Merge and tag commit with version
6. Create GitHub release with user-facing changelog items

### Post-Release

1. Add "Unreleased" section to changelog
2. Bump version to next patch with `.dev` suffix
3. Update example model version numbers

## Licensing

Contributors agree that their work is original and licensed under the Apache 2.0 license, consistent with Calliope's licensing terms.
