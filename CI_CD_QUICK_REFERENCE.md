# CI/CD Pipeline Quick Reference

## 🚀 Getting Started (5 minutes)

```bash
# 1. Install dev dependencies
make dev

# 2. Run local CI checks (before pushing!)
make ci-local

# 3. Start Docker services
make docker-up

# 4. Access services
# Backend:  http://localhost:8001
# Frontend: http://localhost:8501
```

---

## 📋 Common Commands

### Testing
```bash
make test              # Run tests with coverage
make test-verbose      # Run tests with verbose output
pytest tests/          # Run specific test directory
pytest tests/test_ai_developer.py::TestRequirementAnalysis  # Specific test class
```

### Code Quality
```bash
make lint              # Check code style
make format            # Auto-format code
make type-check        # Type checking
make security          # Security scan
make ci-local          # Run all checks
```

### Docker
```bash
make docker            # Build images
make docker-up         # Start services
make docker-down       # Stop services
make docker-logs       # View logs
make clean-docker      # Remove images
```

### Cleanup
```bash
make clean             # Remove cache/artifacts
make clean-docker      # Remove Docker files
```

---

## 🔄 Workflow

### Before Pushing Code
```bash
make ci-local          # Run all checks
git add .
git commit -m "feat: Add feature"
git push origin main
```

### GitHub Actions Auto-runs
1. **CI Pipeline** (ci.yml):
   - Tests (3.9, 3.10, 3.11)
   - Lint, Format, Type check
   - Security scan
   - Upload coverage

2. **Security Pipeline** (security.yml):
   - Bandit scan
   - Safety check
   - pip-audit

3. **Code Quality Pipeline** (lint.yml):
   - Black, isort, Flake8, Pylint

4. **If all pass, CD Pipeline** (cd.yml):
   - Build Docker image
   - Optional: Push to Docker Hub

---

## 📊 Files Added

### GitHub Actions Workflows
```
.github/workflows/
├── ci.yml              # Main CI pipeline
├── cd.yml              # Deploy pipeline  
├── security.yml        # Security scanning
└── lint.yml            # Code quality
```

### Docker
```
├── Dockerfile          # Backend container
├── Dockerfile.streamlit # Frontend container
├── docker-compose.yml  # Service orchestration
└── .dockerignore       # Build optimization
```

### Testing
```
tests/
├── __init__.py
├── conftest.py                      # Pytest config
└── test_ai_developer.py            # Tests
```

### Configuration
```
├── Makefile                         # Commands
├── pytest.ini                       # Pytest config
├── .bandit                          # Security config
├── .pre-commit-config.yaml         # Git hooks
└── requirements.txt                # Dependencies
```

### Documentation
```
├── CI_CD_GUIDE.md                   # Detailed guide
├── CI_CD_IMPLEMENTATION.md          # Implementation summary
├── CI_CD_QUICK_REFERENCE.md         # This file
└── deploy.sh                        # Production deploy script
```

---

## 🐛 Troubleshooting

### Tests fail locally but pass on CI
```bash
# Clear cache and reinstall
pip install --upgrade pip
pip install -r requirements.txt
make test
```

### Docker won't start
```bash
# Check port availability
lsof -i :8001
# Kill if needed
kill -9 <PID>
# Retry
make docker-up
```

### Pre-commit hooks not working
```bash
# Reinstall pre-commit
pip install --force-reinstall pre-commit
pre-commit install
```

### Git hook conflicts
```bash
# Temporarily disable
pre-commit uninstall
# Make changes
git commit ...
# Re-enable
pre-commit install
```

---

## 📈 Monitoring

### GitHub Actions UI
1. Go to **Actions** tab
2. Click recent workflow run
3. View logs, download artifacts

### Local Coverage Report
```bash
# After running tests
open htmlcov/index.html  # macOS
# or
xdg-open htmlcov/index.html  # Linux
# or
start htmlcov\index.html  # Windows
```

### Security Reports
```bash
# View Bandit report
cat bandit-report.json
```

---

## ✅ Pre-push Checklist

- [ ] Run `make ci-local` - all checks pass
- [ ] Run tests: `make test` - no failures
- [ ] Code formatted: `make format`
- [ ] No security issues: `make security`
- [ ] Docker builds: `make docker`
- [ ] Commits are atomic and descriptive

---

## 🔐 Best Practices

1. **Always run `make ci-local` before pushing**
2. **Use meaningful commit messages**: `feat:`, `fix:`, `docs:`
3. **Write tests for new features**
4. **Review GitHub Actions logs** for any warnings
5. **Keep dependencies updated**: `pip audit`
6. **Use branches for features**: `feature/my-feature`
7. **Create PRs for code review** before merging to main

---

## 🎯 Next Steps

1. ✅ Run `make dev` - install dev tools
2. ✅ Run `make ci-local` - verify everything works
3. ✅ Push code to GitHub
4. ✅ Monitor GitHub Actions (Actions tab)
5. ✅ Set branch protection rules
6. ✅ Configure Docker Hub (optional)

---

## 📞 Need Help?

- **Detailed Guide**: See `CI_CD_GUIDE.md`
- **Implementation Details**: See `CI_CD_IMPLEMENTATION.md`
- **Workflow Issues**: Check `.github/workflows/*.yml`
- **Local Setup**: Run `bash setup-cicd.sh`

---

## 🎉 You're All Set!

Your project now has enterprise-grade CI/CD. Start with:
```bash
make dev && make ci-local && make docker-up
```
