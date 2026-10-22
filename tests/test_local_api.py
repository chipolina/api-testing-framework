from uuid import uuid4

import allure
import pytest

from config import LOCAL_API_BASE_URL


@pytest.fixture
def employee_payload():
    return {
        "full_name": "API Test Employee",
        "email": f"api-test-{uuid4().hex}@example.test",
        "department_id": 1,
        "salary": 52000,
    }


@pytest.fixture
def created_employee(http_session, local_api_base_url, employee_payload, db_connection):
    response = http_session.post(
        f"{local_api_base_url}/employees",
        json=employee_payload,
        timeout=10,
    )
    assert response.status_code == 201
    employee = response.json()

    yield employee

    with db_connection.cursor() as cursor:
        cursor.execute("DELETE FROM employees WHERE id = %s", (employee["id"],))


@allure.title("Local API health endpoint is available")
@allure.feature("Local API")
def test_local_api_health(http_session, local_api_base_url):
    response = http_session.get(f"{local_api_base_url}/health", timeout=10)

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@allure.title("Creating an employee through the API persists it in PostgreSQL")
@allure.feature("Local API")
@allure.story("Create")
def test_create_employee_persists_to_postgres(
    http_session, local_api_base_url, employee_payload, db_connection
):
    response = http_session.post(
        f"{local_api_base_url}/employees",
        json=employee_payload,
        timeout=10,
    )
    assert response.status_code == 201
    created = response.json()

    try:
        assert created["id"] > 0
        assert created["full_name"] == employee_payload["full_name"]
        assert created["email"] == employee_payload["email"]
        assert created["department_id"] == employee_payload["department_id"]
        assert float(created["salary"]) == employee_payload["salary"]

        with db_connection.cursor() as cursor:
            cursor.execute(
                "SELECT full_name, email, department_id, salary FROM employees WHERE id = %s",
                (created["id"],),
            )
            row = cursor.fetchone()

        assert row is not None
        assert row[0] == employee_payload["full_name"]
        assert row[1] == employee_payload["email"]
        assert row[2] == employee_payload["department_id"]
        assert float(row[3]) == employee_payload["salary"]
    finally:
        with db_connection.cursor() as cursor:
            cursor.execute("DELETE FROM employees WHERE id = %s", (created["id"],))


@allure.title("Getting an employee returns the stored database record")
@allure.feature("Local API")
@allure.story("Read")
def test_get_employee_returns_database_record(
    http_session, local_api_base_url, created_employee
):
    response = http_session.get(
        f"{local_api_base_url}/employees/{created_employee['id']}",
        timeout=10,
    )

    assert response.status_code == 200
    assert response.json()["id"] == created_employee["id"]
    assert response.json()["email"] == created_employee["email"]


@allure.title("Updating an employee changes the database record")
@allure.feature("Local API")
@allure.story("Update")
def test_update_employee_updates_postgres(
    http_session, local_api_base_url, created_employee, db_connection
):
    payload = {"full_name": "Updated API Employee", "salary": 61000}
    response = http_session.patch(
        f"{local_api_base_url}/employees/{created_employee['id']}",
        json=payload,
        timeout=10,
    )

    assert response.status_code == 200
    assert response.json()["full_name"] == payload["full_name"]
    assert float(response.json()["salary"]) == payload["salary"]

    with db_connection.cursor() as cursor:
        cursor.execute(
            "SELECT full_name, salary FROM employees WHERE id = %s",
            (created_employee["id"],),
        )
        row = cursor.fetchone()

    assert row[0] == payload["full_name"]
    assert float(row[1]) == payload["salary"]


@pytest.mark.parametrize("method", ["get", "patch"])
@allure.title("Requests for a missing employee return 404")
@allure.feature("Local API")
@allure.story("Not found")
def test_missing_employee_returns_404(http_session, local_api_base_url, method):
    url = f"{local_api_base_url}/employees/2147483000"
    if method == "get":
        response = http_session.get(url, timeout=10)
    else:
        response = http_session.patch(
            url,
            json={"full_name": "Missing Employee", "salary": 40000},
            timeout=10,
        )

    assert response.status_code == 404
    assert response.json()["detail"] == "Employee not found."


@allure.title("The API rejects a non-positive employee salary")
@allure.feature("Local API")
@allure.story("Validation")
def test_create_employee_rejects_invalid_salary(
    http_session, local_api_base_url, employee_payload
):
    employee_payload["salary"] = 0
    response = http_session.post(
        f"{local_api_base_url}/employees",
        json=employee_payload,
        timeout=10,
    )

    assert response.status_code == 422


@allure.title("The API rejects a duplicate employee email")
@allure.feature("Local API")
@allure.story("Database constraint")
def test_create_employee_rejects_duplicate_email(http_session, local_api_base_url):
    payload = {
        "full_name": "Duplicate Email Employee",
        "email": "alex.morgan@example.test",
        "department_id": 1,
        "salary": 50000,
    }
    response = http_session.post(
        f"{local_api_base_url}/employees",
        json=payload,
        timeout=10,
    )

    assert response.status_code == 409


@allure.title("The API rejects an employee with an unknown department")
@allure.feature("Local API")
@allure.story("Foreign key constraint")
def test_create_employee_rejects_unknown_department(
    http_session, local_api_base_url, employee_payload
):
    employee_payload["department_id"] = 9999
    response = http_session.post(
        f"{local_api_base_url}/employees",
        json=employee_payload,
        timeout=10,
    )

    assert response.status_code == 422
