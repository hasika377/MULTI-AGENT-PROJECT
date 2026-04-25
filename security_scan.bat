@echo off
REM Security scan helper for Windows

echo.
echo ========================================
echo Running security scans
echo ========================================
echo.

echo [1/2] Running Bandit source code scan...
bandit -r . -x ./venv,./__pycache__
echo.

echo [2/2] Running pip-audit dependency scan...
pip-audit
echo.

echo ========================================
echo Security scan complete
echo ========================================
echo.
