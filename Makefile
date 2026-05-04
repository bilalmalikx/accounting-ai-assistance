.PHONY: help install run dev test clean backup health init-db setup-ollama

help:
	@echo "📦 Accounting AI Assistant - Makefile Commands"
	@echo "=============================================="
	@echo "make install      - Install all dependencies"
	@echo "make setup        - Complete setup (install + models + DB)"
	@echo "make run          - Run production server"
	@echo "make dev          - Run development server with auto-reload"
	@echo "make test         - Run all tests"
	@echo "make test-cov     - Run tests with coverage"
	@echo "make init-db      - Initialize database"
	@echo "make setup-ollama - Pull Ollama models"
	@echo "make clean        - Clean temporary files"
	@echo "make backup       - Backup data"
	@echo "make health       - Check service health"
	@echo "make lint         - Run code linter"

install:
	pip install --upgrade pip
	pip install -r requirements.txt

setup-ollama:
	@echo "📥 Pulling Ollama models..."
	ollama pull llama3.2:3b
	ollama pull nomic-embed-text
	@echo "✅ Models pulled successfully"

init-db:
	python scripts/init_db.py

setup: install setup-ollama init-db
	@echo "✅ Complete setup finished!"

run:
	uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 2

dev:
	uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

test:
	pytest tests/ -v

test-cov:
	pytest tests/ --cov=backend --cov-report=html --cov-report=term

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.so" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -delete
	rm -rf build/ dist/ htmlcov/

backup:
	./scripts/backup.sh

health:
	./scripts/healthcheck.sh

lint:
	ruff check backend/
	mypy backend/

docker-build:
	docker build -t accounting-ai:latest .

docker-run:
	docker-compose up -d

docker-stop:
	docker-compose down