
install:
	python3 -m venv .venv
	. .venv/bin/activate && pip install -e ".[dev]"

up:
	docker compose up -d postgres

down:
	docker compose down

migrate:
	alembic upgrade head

seed:
	python -m scripts.seed

dev:
	uvicorn app.main:app --reload

test:
	pytest -q

lint:
	ruff check app tests scripts
