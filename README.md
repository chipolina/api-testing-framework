# API Testing Framework

A small learning project for API testing and database integration. It includes an external demo API and a minimal local API connected to PostgreSQL. The project can later be extended with MCP integrations such as Playwright, Jira, or Confluence.

## Stack

- Python and pytest
- Requests for API calls
- FastAPI for the local demo API
- PostgreSQL in Docker Compose
- psycopg for database access
- Allure and pytest-cov for reporting and coverage

## Requirements

- Python 3.14
- Docker Desktop with Docker Compose
- Git

## 1. Set up the Python environment

```bash
python3.14 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 2. Configure the database

Create a local `.env` file in the repository root. Do not commit it.

```dotenv
DB_HOST=localhost
DB_PORT=5432
DB_NAME=api_testing
DB_USER=test_user
DB_PASSWORD=test_password
LOCAL_API_BASE_URL=http://localhost:8000
```

These credentials are for the local learning environment only.

## 3. Start the local stack

Build and start PostgreSQL and the local API:

```bash
docker compose up --build -d
docker compose ps
```

- PostgreSQL is available at `localhost:5432`.
- The local API is available at `http://localhost:8000`.
- Interactive API documentation is available at `http://localhost:8000/docs`.

The Compose service initializes the schema and sample data from `db/init/01_schema.sql` when the database volume is created for the first time.

Check the database connection:

```bash
python -m scripts.check_db_connection
```

Check the API:

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{"status":"ok"}
```

To reset the database and re-run initialization:

```bash
docker compose down -v
docker compose up --build -d
```

**Warning:** `docker compose down -v` deletes the Compose database volume and all data stored in it.

## 4. Run tests

With the stack running:

```bash
python -m pytest
```

The suite retains the existing tests against the external Restful Booker API and PostgreSQL. Local API integration tests cover health, create/read/update, missing employees, invalid salary, duplicate email, and unknown departments. The create and update checks verify the actual database state.

Pytest writes Allure results to `allure-results/` and enforces the coverage threshold configured in `pytest.ini`.

## 5. Allure report

If the Allure CLI is installed:

```bash
allure serve allure-results
```

GitHub Actions starts PostgreSQL, initializes the schema and sample data, starts the local API, and runs the tests. The generated HTML report is uploaded as a workflow artifact.

## Project structure

```text
app/                      Local FastAPI application
clients/                  External API client
config.py                 Environment and database settings
db/init/01_schema.sql     Demo schema and seed data
scripts/                  Utility scripts
tests/                    External API, local API, and database tests
Dockerfile                Local API image
compose.yaml              PostgreSQL and local API services
.github/workflows/         CI workflow
```

## Scope

This repository demonstrates the foundations only. It is not a production-ready service. The local API intentionally exposes only a small employee CRUD subset for integration-testing practice.
