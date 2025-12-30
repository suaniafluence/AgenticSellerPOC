# AgenticSellerPOC

[![CI Pipeline](https://github.com/suaniafluence/AgenticSellerPOC/workflows/CI%20Pipeline/badge.svg)](https://github.com/suaniafluence/AgenticSellerPOC/actions)
[![codecov](https://codecov.io/gh/suaniafluence/AgenticSellerPOC/branch/main/graph/badge.svg)](https://codecov.io/gh/suaniafluence/AgenticSellerPOC)
[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Agentic Seller Proof of Concept

## Features

- 🚀 Modern Python project structure
- 🔄 Complete CI/CD pipeline with GitHub Actions
- 🧪 Automated testing with pytest
- 📦 Docker support
- 🔒 Security scanning with Bandit and CodeQL
- 📊 Code coverage tracking
- 🎨 Code formatting with Black and Ruff

## Installation

### Using pip

```bash
pip install agenticsellerpoc
```

### From source

```bash
git clone https://github.com/suaniafluence/AgenticSellerPOC.git
cd AgenticSellerPOC
pip install -r requirements.txt
pip install -e .
```

### Using Docker

```bash
docker build -t agenticsellerpoc .
docker run agenticsellerpoc
```

## Development

### Setup Development Environment

1. Clone the repository:
```bash
git clone https://github.com/suaniafluence/AgenticSellerPOC.git
cd AgenticSellerPOC
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=agenticseller --cov-report=html

# Run specific test file
pytest tests/test_example.py
```

### Code Quality

```bash
# Format code
black .
isort .

# Lint code
ruff check .

# Type checking
mypy .

# Security scan
bandit -r agenticseller/
```

## CI/CD Pipeline

This project uses GitHub Actions for continuous integration and deployment:

### Continuous Integration (CI)

The CI pipeline runs on every push and pull request:

- **Linting & Formatting**: Checks code style with Ruff, Black, and isort
- **Type Checking**: Static type analysis with mypy
- **Testing**: Runs test suite across Python 3.9, 3.10, 3.11, and 3.12
- **Code Coverage**: Generates coverage reports and uploads to Codecov
- **Security Scanning**:
  - Bandit for Python security issues
  - Safety for dependency vulnerabilities
  - CodeQL for advanced security analysis
- **Build**: Validates package building

### Continuous Deployment (CD)

Automated deployment workflows:

- **PyPI Deployment**: Publishes to PyPI on release
- **Docker Images**: Builds and pushes to GitHub Container Registry
- **Environment Deployments**:
  - Staging: Auto-deploy from `develop` branch
  - Production: Deploy from releases or manually trigger

### Additional Automations

- **Dependency Updates**: Dependabot automatically creates PRs for dependency updates
- **PR Labeling**: Automatic labeling based on file changes and PR size
- **Dependency Review**: Security checks for new dependencies in PRs

## Project Structure

```
AgenticSellerPOC/
├── .github/
│   ├── workflows/          # GitHub Actions workflows
│   │   ├── ci.yml         # Main CI pipeline
│   │   ├── cd.yml         # Deployment workflows
│   │   ├── codeql.yml     # Security scanning
│   │   ├── dependency-review.yml
│   │   └── pr-labeler.yml
│   ├── ISSUE_TEMPLATE/    # Issue templates
│   ├── PULL_REQUEST_TEMPLATE/
│   ├── dependabot.yml     # Dependabot configuration
│   └── labeler.yml        # PR labeling rules
├── agenticseller/         # Main package
│   └── __init__.py
├── tests/                 # Test suite
│   ├── __init__.py
│   └── test_example.py
├── .dockerignore
├── .gitignore
├── Dockerfile
├── pyproject.toml         # Project configuration
├── requirements.txt       # Production dependencies
├── requirements-dev.txt   # Development dependencies
└── README.md
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linting (`pytest && ruff check .`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions, please use the [GitHub Issues](https://github.com/suaniafluence/AgenticSellerPOC/issues) page.
