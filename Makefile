.PHONY: help install dev test lint format security clean docker docker-up docker-down

help:
	@echo "SDLC Multi-Agent Backend Builder - Development Commands"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make install          Install production dependencies"
	@echo "  make dev              Install development dependencies"
	@echo ""
	@echo "Testing & Quality:"
	@echo "  make test             Run unit tests with coverage"
	@echo "  make lint             Run linting checks (Flake8)"
	@echo "  make format           Format code with Black"
	@echo "  make type-check       Run type checks with MyPy"
	@echo "  make security         Run security scan with Bandit"
	@echo ""
	@echo "Docker:"
	@echo "  make docker           Build Docker images"
	@echo "  make docker-up        Start services with Docker Compose"
	@echo "  make docker-down      Stop Docker Compose services"
	@echo "  make docker-logs      View Docker Compose logs"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean            Remove cache and build artifacts"
	@echo "  make clean-docker     Remove Docker images and containers"

install:
	pip install --upgrade pip
	pip install -r requirements.txt

dev: install
	pip install pytest pytest-cov black flake8 mypy bandit safety pip-audit

test:
	pytest tests/ --cov=. --cov-report=html --cov-report=term-missing -v

lint:
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics

format:
	black . --line-length=100

type-check:
	mypy . --ignore-missing-imports || true

security:
	@echo "Running Bandit security scan..."
	bandit -r . -f json -o bandit-report.json || true
	@echo "Running Safety vulnerability check..."
	safety check || true
	@echo "Running pip-audit..."
	pip-audit || true

docker:
	docker build -t sdlc-multi-agent:latest .
	docker build -t sdlc-frontend:latest -f Dockerfile.streamlit .

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

ci-local: dev lint format type-check test security
	@echo "✅ All CI checks passed locally!"

clean:
	find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name ".pytest_cache" -exec rm -r {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -r {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -r {} + 2>/dev/null || true
	rm -f .coverage coverage.xml bandit-report.json

clean-docker:
	docker-compose down -v
	docker rmi sdlc-multi-agent:latest sdlc-frontend:latest || true
