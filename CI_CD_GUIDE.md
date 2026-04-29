# CI/CD Pipeline Documentation

## Overview
This project now includes a comprehensive CI/CD pipeline built with GitHub Actions, Docker, and automated testing. The pipeline ensures code quality, security, and reliable deployments.

## Pipeline Stages

### 1. **Continuous Integration (CI)**
Triggered on every push and pull request to `main` and `develop` branches.

**File**: `.github/workflows/ci.yml`

**Steps**:
- ✅ **Setup**: Python environment (3.9, 3.10, 3.11)
- ✅ **Dependency Caching**: Speeds up builds
- ✅ **Format Check**: Black code formatter
- ✅ **Linting**: Flake8 for code quality
- ✅ **Type Checking**: MyPy for type safety
- ✅ **Security Scan**: Bandit for vulnerabilities
- ✅ **Unit Tests**: Pytest with coverage reporting
- ✅ **Coverage Upload**: To Codecov
- ✅ **Artifact Upload**: Test reports and coverage

### 2. **Security Scanning**
Runs on push, PR, and weekly schedule for proactive vulnerability detection.

**File**: `.github/workflows/security.yml`

**Scans**:
- 🔒 Bandit - Python security issues
- 🔒 Safety - Known dependency vulnerabilities
- 🔒 pip-audit - Additional vulnerability checks

### 3. **Continuous Deployment (CD)**
Automatically builds and pushes Docker images on main branch updates.

**File**: `.github/workflows/cd.yml`

**Steps**:
- 🐳 Build Docker image
- 🐳 Push to Docker Hub (optional)
- 🐳 Cache optimization with BuildX
- 📦 Generate deployment report
- 🚀 Ready for staging/production deployment

## Local Development

### Prerequisites
- Python 3.9+
- Docker & Docker Compose
- Make (optional, for convenience)

### Setup Development Environment

```bash
# Install development dependencies
make dev

# Or manually:
pip install -r requirements.txt
pip install pytest pytest-cov black flake8 mypy bandit
```

### Running CI Checks Locally

```bash
# Run all checks (recommended before pushing)
make ci-local

# Or run individual checks:
make lint          # Flake8 linting
make format        # Black formatting
make type-check    # MyPy type checking
make test          # Pytest with coverage
make security      # Security scans
```

### Running Tests

```bash
# Run all tests
make test

# Run specific test file
pytest tests/test_ai_developer.py -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# View coverage report
open htmlcov/index.html
```

## Docker Support

### Build Docker Images

```bash
# Build using Makefile
make docker

# Or manually:
docker build -t sdlc-multi-agent:latest .
docker build -t sdlc-frontend:latest -f Dockerfile.streamlit .
```

### Run with Docker Compose

```bash
# Start all services
make docker-up

# View logs
make docker-logs

# Stop services
make docker-down
```

**Services**:
- **Backend**: `http://localhost:8001` (FastAPI)
- **Gemini Wrapper**: `http://localhost:8000` (API wrapper)
- **Frontend**: `http://localhost:8501` (Streamlit UI)

### Environment Variables for Docker

Create `.env` file:
```
GEMINI_API_KEY=your_api_key_here
DEBUG=False
GEMINI_MODEL=gemini-2.5-flash
```

## GitHub Actions Setup

### 1. Enable GitHub Actions
- Go to your GitHub repository
- Navigate to **Settings** → **Actions**
- Enable GitHub Actions

### 2. Set Secrets (Optional for Docker Hub)
For automatic Docker Hub pushes:

```
Settings → Secrets and variables → Actions
```

Add secrets:
- `DOCKER_USERNAME`: Your Docker Hub username
- `DOCKER_PASSWORD`: Your Docker Hub access token

### 3. Branch Protection Rules (Recommended)

```
Settings → Branches → Branch protection rules
```

Configure:
- ✅ Require status checks to pass before merging
- ✅ Require PR reviews before merging
- ✅ Dismiss stale PR approvals
- ✅ Require branches to be up to date

## Workflow Execution

### On Push to Main
1. CI pipeline runs (tests, lint, format)
2. Security scan runs
3. If all pass → CD pipeline builds Docker image
4. Docker image available for deployment

### On Pull Request
1. CI pipeline runs
2. Security scan runs
3. Results displayed on PR

### Manual Workflow Dispatch (Optional)
Can be enabled for manual CI/CD triggering:

```yaml
on:
  workflow_dispatch:
    inputs:
      environment:
        description: 'Environment to deploy'
        required: true
        default: 'staging'
```

## Testing

### Test Coverage

Currently includes tests for:
- Requirement analysis
- Utility functions
- Capability extraction

Add more tests in `tests/` directory:

```bash
pytest tests/ --cov=. --cov-report=html
```

### Test File Structure

```
tests/
├── __init__.py
├── conftest.py                  # Pytest fixtures
├── test_ai_developer.py         # Core logic tests
├── test_api_endpoints.py        # API endpoint tests (to add)
├── test_code_generation.py      # Code generation tests (to add)
└── test_integration.py          # Integration tests (to add)
```

## Monitoring & Reporting

### GitHub Actions UI
- Go to **Actions** tab in repository
- View workflow runs, logs, and artifacts
- Download test reports and coverage

### Codecov Integration
- Coverage reports automatically uploaded
- Accessible at: `codecov.io/gh/your-org/your-repo`

### Artifacts
Downloads available after each run:
- `test-results-*.zip` - Test reports
- `security-reports/` - Security scan reports
- `deployment-report.md` - Deployment metadata

## Cleanup

```bash
# Clean local cache
make clean

# Remove Docker images and containers
make clean-docker

# Full reset
make clean && make clean-docker
```

## Best Practices

1. **Always run `make ci-local` before pushing**
   ```bash
   make ci-local
   ```

2. **Keep tests updated** when adding features
   ```bash
   pytest tests/ -v
   ```

3. **Use meaningful commit messages**
   ```
   feat: Add CI/CD pipeline
   fix: Resolve test failures
   docs: Update README
   ```

4. **Review security reports** before merging
   - Check Bandit output in GitHub Actions
   - Fix vulnerabilities immediately

5. **Monitor coverage metrics**
   - Aim for >80% code coverage
   - Review uncovered lines in CI output

## Troubleshooting

### Docker Build Fails
```bash
# Clear Docker cache and rebuild
docker system prune -a
make docker
```

### Tests Fail Locally but Pass on CI
```bash
# Rebuild dependency cache
pip install --upgrade pip
pip install -r requirements.txt
make test
```

### GitHub Actions Not Running
1. Check that Actions is enabled in Settings
2. Verify workflow file syntax (`.github/workflows/*.yml`)
3. Check branch protection rules aren't blocking

### Docker Compose Port Conflicts
```bash
# Check which processes use ports
lsof -i :8001  # Check port 8001
lsof -i :8000  # Check port 8000
lsof -i :8501  # Check port 8501

# Kill process if needed
kill -9 <PID>
```

## Next Steps

1. ✅ Push code to GitHub with workflows
2. ✅ Add more comprehensive tests
3. ✅ Set up Codecov integration
4. ✅ Configure branch protection rules
5. ✅ Add deployment webhooks for production
6. ✅ Monitor metrics and optimize pipeline

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Documentation](https://docs.docker.com/)
- [Pytest Documentation](https://pytest.org/)
- [GitHub Actions Best Practices](https://docs.github.com/en/actions/guides)
