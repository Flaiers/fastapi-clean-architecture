include env/example.env
include env/.env
export

VENV=. .venv/bin/activate

.SILENT:
.PHONY: help
help: ## Display this help screen
	awk 'BEGIN {FS = ":.*##"; printf "Usage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) }' $(MAKEFILE_LIST)

.PHONY: init
init: ## Init project
	python -m venv .venv && $(VENV) && \
	pip install -r requirements.txt && pip install -U pip

.PHONY: lint
lint: ## Run linter
	$(VENV) && flake8 .

.PHONY: lint-imports
lint-imports: ## Run imports linter
	$(VENV) && isort .

.PHONY: run
run: ## Run applications
	make -j 2 run-admin run-backend

.PHONY: run-admin
run-admin: ## Run admin
	$(VENV) && gunicorn --reload --bind $(HOST):$(ADMIN_PORT) \
	--workers $(WORKERS) --log-level $(LEVEL) --chdir cmd/admin main:app

.PHONY: run-backend
run-backend: ## Run backend
	$(VENV) && uvicorn --reload --host $(HOST) --port $(BACKEND_PORT) \
	--workers $(WORKERS) --log-level $(LEVEL) --app-dir cmd/app main:app

.PHONY: migrate-create
migrate-create: ## Create new migration
	$(VENV) && alembic revision --autogenerate -m $(name)

.PHONY: migrate-up
migrate-up: ## Migration up
	$(VENV) && alembic upgrade head
