# Contributing to AidMind

Thank you for your interest in contributing to AidMind! This document provides guidelines for contributing to the project.

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [GitHub Issues](https://github.com/yourorg/aidmind/issues)
2. If not, create a new issue with:
   - Clear, descriptive title
   - Steps to reproduce the bug
   - Expected vs actual behavior
   - Your environment (OS, Python version, AidMind version)
   - Sample data or code (if possible)

### Suggesting Features

1. Check if the feature has been requested in [GitHub Discussions](https://github.com/yourorg/aidmind/discussions)
2. Create a new discussion with:
   - Clear description of the feature
   - Use cases and benefits
   - Potential implementation approach (optional)

### Code Contributions

#### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/yourorg/aidmind.git
cd aidmind

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt
pip install -e ".[dev]"
```

#### Development Workflow

1. **Fork** the repository
2. **Create a branch** for your feature/fix:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make changes** following our coding standards
4. **Add tests** for new functionality
5. **Run tests** to ensure nothing breaks:
   ```bash
   pytest
   ```
6. **Commit** with clear, descriptive messages:
   ```bash
   git commit -m "Add feature: description"
   ```
7. **Push** to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
8. **Create a Pull Request** with:
   - Description of changes
   - Link to related issues
   - Screenshots (if UI changes)

#### Coding Standards

- **Style**: Follow PEP 8
  - Use `black` for formatting: `black aidmind.py`
  - Use `flake8` for linting: `flake8 aidmind.py`
- **Type hints**: Add type annotations for all functions
- **Docstrings**: Use NumPy-style docstrings
- **Testing**: Aim for >80% code coverage
- **Logging**: Use structured logging (INFO level for user-facing, DEBUG for internal)

#### Code Review Process

1. Maintainers will review your PR within 1-2 weeks
2. Address feedback and update your PR
3. Once approved, a maintainer will merge your PR

### Documentation Contributions

Improvements to documentation are highly valued:
- Fix typos or unclear instructions
- Add examples or use cases
- Improve API documentation
- Translate documentation (future)

### Testing

Run the test suite:
```bash
# All tests
pytest

# With coverage
pytest --cov=aidmind --cov-report=html

# Specific test file
pytest test_aidmind.py -v
```

### Questions?

- Open a [GitHub Discussion](https://github.com/yourorg/aidmind/discussions)
- Email: support@aidmind.org

## Code of Conduct

Be respectful and inclusive. We follow the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/).

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
