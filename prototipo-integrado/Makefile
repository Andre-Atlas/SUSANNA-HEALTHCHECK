install:
	python3 -m venv .venv
	.venv/bin/python -m pip install -e ".[dev]"

up:
	docker compose up -d postgres

down:
	docker compose down

migrate:
	.venv/bin/python -m alembic upgrade head

seed:
	.venv/bin/python -m scripts.seed

ollama-check:
	.venv/bin/python -m scripts.check_ollama

dev:
	.venv/bin/python -m uvicorn app.main:app --reload

test:
	.venv/bin/python -m pytest -q

lint:
	.venv/bin/ruff check app tests scripts

check: lint test
