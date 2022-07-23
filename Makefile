ifneq ($(wildcard .env.example),)
    include .env.example
endif
ifneq ($(wildcard .env),)
    include .env
endif

export


.SILENT:
.PHONY: help
help: ## Display this help screen
	awk 'BEGIN {FS = ":.*##"; printf "Usage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) }' $(MAKEFILE_LIST)

.PHONY: install
install: ## Installations
	poetry env use python
	poetry install
	poetry run pre-commit install

.PHONY: lint
lint: ## Run linters
	poetry run isort .
	poetry run flake8
	poetry run mypy .

.PHONY: run
run: ## Run applications
	make -j 2 run-admin run-backend

.PHONY: run-admin
run-admin: ## Run admin
	poetry run gunicorn --reload --bind $(HOST):$(ADMIN_PORT) \
	--workers $(WORKERS) --log-level $(LEVEL) --chdir cmd/admin main:app

.PHONY: run-backend
run-backend: ## Run backend
	poetry run gunicorn --reload --bind $(HOST):$(BACKEND_PORT) \
	--worker-class uvicorn.workers.UvicornWorker \
	--workers $(WORKERS) --log-level $(LEVEL) --chdir cmd/app main:app

.PHONY: migrate-create
migrate-create: ## Create new migration
	poetry run alembic revision --autogenerate -m $(name)

.PHONY: migrate-up
migrate-up: ## Migration up
	poetry run alembic upgrade head
