ifneq ($(wildcard docker/.env.example),)
	ENV_FILE = .env.example
endif
ifneq ($(wildcard .env.example),)
	ifeq ($(COMPOSE_PROJECT_NAME),)
		include .env.example
	endif
endif
ifneq ($(wildcard docker/.env),)
	ENV_FILE = .env
endif
ifneq ($(wildcard .env),)
	ifeq ($(COMPOSE_PROJECT_NAME),)
		include .env
	endif
endif

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
migrate-create: ## Create a new revision file
	poetry run alembic revision --autogenerate -m $(name)

.PHONY: migrate-up
migrate-up: ## Upgrade to a later version
	poetry run alembic upgrade head

.PHONY: migrate-down
migrate-down: ## Revert to a previous version
	poetry run alembic downgrade $(revision)

.PHONY: rabbitmq-compose-up
rabbitmq-compose-up: ## Create and start rabbitmq container
	docker-compose -f docker/rabbitmq-docker-compose.yml -p rabbitmq --env-file docker/$(ENV_FILE) up -d

.PHONY: compose-build
compose-build: ## Build or rebuild services
	docker-compose -f docker/docker-compose.yml --env-file docker/$(ENV_FILE) build

.PHONY: compose-convert
compose-convert: ## Converts the compose file to platform's canonical format
	docker-compose -f docker/docker-compose.yml --env-file docker/$(ENV_FILE) convert

.PHONY: compose-up
compose-up: rabbitmq-compose-up ## Create and start containers
	docker-compose -f docker/docker-compose.yml --env-file docker/$(ENV_FILE) up -d

.PHONY: compose-logs
compose-logs: ## View output from containers
	docker-compose -f docker/docker-compose.yml --env-file docker/$(ENV_FILE) logs -f

.PHONY: compose-ps
compose-ps: ## List containers
	docker-compose -f docker/docker-compose.yml --env-file docker/$(ENV_FILE) ps

.PHONY: compose-ls
compose-ls: ## List running compose projects
	docker-compose -f docker/docker-compose.yml --env-file docker/$(ENV_FILE) ls

.PHONY: compose-exec
compose-exec: ## Execute a command in a running container
	docker-compose -f docker/docker-compose.yml --env-file docker/$(ENV_FILE) exec backend bash

.PHONY: compose-start
compose-start: ## Start services
	docker-compose -f docker/docker-compose.yml --env-file docker/$(ENV_FILE) start

.PHONY: compose-restart
compose-restart: ## Restart services
	docker-compose -f docker/docker-compose.yml --env-file docker/$(ENV_FILE) restart

.PHONY: compose-stop
compose-stop: ## Stop services
	docker-compose -f docker/docker-compose.yml --env-file docker/$(ENV_FILE) stop

.PHONY: compose-down
compose-down: ## Stop and remove containers, networks
	docker-compose -f docker/docker-compose.yml --env-file docker/$(ENV_FILE) down --remove-orphans

.PHONY: docker-rm-volume
docker-rm-volume: ## Remove db volume
	docker volume rm -f fastapi_clean_db_data

.PHONY: docker-clean
docker-clean: ## Remove unused data
	docker system prune
