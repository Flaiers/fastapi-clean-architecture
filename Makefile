ifneq ($(wildcard docker/.env.example),)
    ENV_FILE = .env.example
endif
ifneq ($(wildcard .env.example),)
    include .env.example
endif
ifneq ($(wildcard docker/.env),)
    ENV_FILE = .env
endif
ifneq ($(wildcard .env),)
	ifeq ($(COMPOSE_PROJECT_NAME),)
		include .env
	endif
endif

docker_compose = docker-compose -f docker/docker-compose.yml --env-file docker/$(ENV_FILE)

export


.SILENT:
.PHONY: help
help: ## Display this help screen
	awk 'BEGIN {FS = ":.*##"; printf "Usage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) }' $(MAKEFILE_LIST)

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

.PHONY: compose-build
compose-build: ## Build or rebuild services
	$(docker_compose) build

.PHONY: compose-up
compose-up: ## Create and start containers
	$(docker_compose) up -d && $(docker_compose) logs -f

.PHONY: compose-ps
compose-ps: ## List containers
	$(docker_compose) ps

.PHONY: compose-ls
compose-ls: ## List running compose projects
	$(docker_compose) ls

.PHONY: compose-exec
compose-exec: ## Execute a command in a running container
	$(docker_compose) exec backend bash

.PHONY: compose-start
compose-start: ## Start services
	$(docker_compose) start

.PHONY: compose-restart
compose-restart: ## Restart services
	$(docker_compose) restart

.PHONY: compose-stop
compose-stop: ## Stop services
	$(docker_compose) stop

.PHONY: compose-down
compose-down: ## Stop and remove containers, networks
	$(docker_compose) down --remove-orphans

.PHONY: docker-rm-volume
docker-rm-volume: ## Remove db volume
	docker volume rm -f fastapi_clean_db_data fastapi_clean_rabbitmq_data

.PHONY: docker-clean
docker-clean: ## Remove unused data
	docker system prune
