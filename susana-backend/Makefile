install:
	python3 -m venv .venv
	. .venv/bin/activate && python -m pip install -e ".[dev]"

up:
	docker compose up -d postgres

down:
	docker compose down

migrate:
	alembic upgrade head

seed:
	python -m scripts.seed

ollama-check:
	python -m scripts.check_ollama

dev:
	uvicorn app.main:app --reload

test:
	pytest -q

lint:
	ruff check app tests scripts

check: lint test
