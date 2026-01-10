# Makefile

dev-venv:
	python3 -m venv venv

dev-install: venv
	source venv/bin/activate && pip install -r requirements.txt

dev-run: install
	source venv/bin/activate && uvicorn main:app --reload
dev-clean:
	rm -rf venv __pycache__
	
docker-up:
	docker compose up -d
docker-down:
	docker compose down
docker-rebuild:
	docker compose down -v && docker compose up --build -d

db-migrate:
	docker compose exec web alembic upgrade head
db-revision:
	docker compose exec web alembic revision --autogenerate -m "$(m)"
db-status:
	docker compose exec web alembic current
db-downgrade:
	docker compose exec web alembic downgrade -1
db-history:
	docker compose exec web alembic history

create-provider:
	docker compose exec web python3 ./scripts/generate_provider.py