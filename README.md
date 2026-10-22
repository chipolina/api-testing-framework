# API Testing Framework

A small learning project for API testing and database integration. It is intentionally limited in scope and can later be extended with MCP integrations such as Playwright, Jira, or Confluence.

## Stack

- Python and pytest
- Requests for API calls
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
```

These credentials are for the local learning environment only.

## 3. Start PostgreSQL

```bash
docker compose up -d postgres
docker compose ps
```

The Compose service initializes the schema and sample data from `db/init/01_schema.sql` when the database volume is created for the first time.

To reset the database and re-run initialization:

```bash
docker compose down -v
docker compose up -d postgres
```

**Warning:** `docker compose down -v` deletes the Compose database volume and all data stored in it.

Check the connection:

```bash
python -m scripts.check_db_connection
```

## 4. Run tests

```bash
python -m pytest
```

The database tests cover connection settings, department/employee queries, joins, task filtering, transactional inserts, and database constraints. Tests that write data use a transaction and roll it back to avoid polluting the sample dataset.

Pytest writes Allure results to `allure-results/` and enforces the coverage threshold configured in `pytest.ini`.

## 5. Allure report

If the Allure CLI is installed:

```bash
allure serve allure-results
```

GitHub Actions runs the tests with a PostgreSQL service and uploads the generated HTML report as a workflow artifact. The report can be downloaded from the completed workflow run.

## Project structure

```text
clients/                  API client
config.py                 Environment and database settings
db/init/01_schema.sql     Demo schema and seed data
scripts/                  Utility scripts
tests/                    API and database tests
compose.yaml              Local PostgreSQL service
.github/workflows/         CI workflow
```

## Scope

This repository demonstrates the foundations only. It does not aim to be a production-ready framework. Future iterations can add API-to-database consistency checks and MCP-backed tools for browser, issue-tracker, and documentation workflows.
