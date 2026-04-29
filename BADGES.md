# Status Badges for README

Add these badges to your README.md to show CI/CD status:

```markdown
# SDLC Multi-Agent Backend Builder

[![CI - Test & Code Quality](https://github.com/YOUR_ORG/YOUR_REPO/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/YOUR_ORG/YOUR_REPO/actions/workflows/ci.yml)
[![CD - Build & Deploy Docker Image](https://github.com/YOUR_ORG/YOUR_REPO/actions/workflows/cd.yml/badge.svg?branch=main)](https://github.com/YOUR_ORG/YOUR_REPO/actions/workflows/cd.yml)
[![Security - Vulnerability Scanning](https://github.com/YOUR_ORG/YOUR_REPO/actions/workflows/security.yml/badge.svg?branch=main)](https://github.com/YOUR_ORG/YOUR_REPO/actions/workflows/security.yml)
[![Code Coverage](https://codecov.io/gh/YOUR_ORG/YOUR_REPO/branch/main/graph/badge.svg)](https://codecov.io/gh/YOUR_ORG/YOUR_REPO)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-%E2%9C%93-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## Quick Links

- 📖 [CI/CD Guide](CI_CD_GUIDE.md)
- 🚀 [Implementation Summary](CI_CD_IMPLEMENTATION.md)
- ⚡ [Quick Reference](CI_CD_QUICK_REFERENCE.md)
- 🔧 [Workflows](.github/workflows/)
```

## Instructions

1. Replace `YOUR_ORG` and `YOUR_REPO` with your actual GitHub organization and repository names
2. Add the badges to your `README.md` near the top
3. Commit and push to activate the badges

## What These Badges Show

| Badge | Shows |
|-------|-------|
| CI - Test & Code Quality | Latest CI workflow status |
| CD - Build & Deploy | Latest deployment workflow status |
| Security - Vulnerability Scanning | Latest security scan status |
| Code Coverage | Coverage percentage on Codecov |
| Python 3.9+ | Minimum supported Python version |
| Docker | Project supports Docker |
| License | Project license |

## Alternative Badge Styles

For shields.io badges with different styles:

```markdown
[![CI](https://img.shields.io/github/actions/workflow/status/YOUR_ORG/YOUR_REPO/ci.yml?branch=main&label=CI&style=flat-square)](https://github.com/YOUR_ORG/YOUR_REPO/actions)
```

Styles available: `flat`, `flat-square`, `plastic`, `for-the-badge`
