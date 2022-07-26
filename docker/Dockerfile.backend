FROM python:3.10-slim

# Step 1: Setup Environment Variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_HOME='/usr/local' \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR='/var/cache/pypoetry'

# Step 2: Install Utilites
RUN apt-get update; \
    apt-get install -y curl make build-essential; \
    curl -sSL https://install.python-poetry.org | python -

WORKDIR /code

# Step 3: Install Python Modules
COPY poetry.lock pyproject.toml /code/
RUN poetry install --no-root --no-dev

# Step 4: Copy Application
COPY . .

# Step 5: Run Application
CMD ["make", "run"]
