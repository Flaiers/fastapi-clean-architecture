include env/example.env
include env/.env
export

VENV=. .venv/bin/activate

.PHONY: help

help: ## Display this help screen
	@awk 'BEGIN {FS = ":.*##"; printf "Usage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) }' $(MAKEFILE_LIST)

run: ## Run applications
	@make -j 2 run-admin run-backend
.PHONY: run

run-admin: ## Run admin
	@$(VENV) && uvicorn --reload --host $(HOST) --port $(ADMIN_PORT) \
	--workers $(WORKERS) --log-level $(LEVEL) --app-dir cmd/admin main:app
.PHONY: run-admin

run-backend: ## Run backend
	@$(VENV) && uvicorn --reload --host $(HOST) --port $(BACKEND_PORT) \
	--workers $(WORKERS) --log-level $(LEVEL) --app-dir cmd/app main:app
.PHONY: run-backend

migrate-create: ## Create new migration
	@alembic revision --autogenerate -m $(name)
.PHONY: migrate-create

migrate-up: ## Migration up
	@alembic upgrade head
.PHONY: migrate-up
