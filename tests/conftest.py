import platform
import sys
from pathlib import Path

import psycopg
import pytest
import requests

from clients.api_client import ApiClient
from config import (
    BASE_URL,
    DB_HOST,
    DB_NAME,
    DB_PASSWORD,
    DB_PORT,
    DB_USER,
    LOCAL_API_BASE_URL,
)


@pytest.fixture
def http_session():
    with requests.Session() as session:
        session.headers.update({"Accept": "application/json"})
        yield session


@pytest.fixture
def api_client():
    client = ApiClient(BASE_URL)
    try:
        yield client
    finally:
        client.close()


@pytest.fixture
def local_api_base_url():
    return LOCAL_API_BASE_URL.rstrip("/")


@pytest.fixture
def booking_id(api_client):
    response = api_client.get("/booking")
    assert response.status_code == 200

    bookings = response.json()
    assert bookings, "Booking list is empty"

    return bookings[0]["bookingid"]


@pytest.fixture(scope="session", autouse=True)
def write_allure_environment():
    results_dir = Path("allure-results")
    results_dir.mkdir(exist_ok=True)

    environment = (
        f"Python={sys.version.split()[0]}\n"
        f"OS={platform.platform()}\n"
        f"Architecture={platform.machine()}\n"
        f"Pytest={pytest.__version__}\n"
    )

    (results_dir / "environment.properties").write_text(
        environment,
        encoding="utf-8",
    )


@pytest.fixture
def db_connection():
    with psycopg.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    ) as connection:
        yield connection


@pytest.fixture
def db_transaction(db_connection):
    try:
        yield db_connection
    finally:
        db_connection.rollback()
