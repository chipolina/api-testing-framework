import allure
import psycopg
import pytest


@allure.title("Connect to PostgreSQL")
@allure.feature("Database")
@allure.story("Connection")
def test_db_connection(db_connection):
    with db_connection.cursor() as cursor:
        cursor.execute("SELECT current_database(), current_user")
        database, user = cursor.fetchone()

    assert database == "api_testing"
    assert user == "test_user"


@allure.title("Seed data contains the expected departments")
@allure.feature("Database")
@allure.story("Seed data")
def test_departments_seeded(db_connection):
    with db_connection.cursor() as cursor:
        cursor.execute("SELECT name FROM departments ORDER BY id")
        departments = [row[0] for row in cursor.fetchall()]

    assert departments == ["QA", "Engineering", "Product"]


@allure.title("Employees can be filtered by department")
@allure.feature("Database")
@allure.story("Select and join")
def test_employees_by_department(db_connection):
    with db_connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT employees.full_name
            FROM employees
            JOIN departments ON departments.id = employees.department_id
            WHERE departments.name = %s
            ORDER BY employees.id
            """,
            ("QA",),
        )
        employees = [row[0] for row in cursor.fetchall()]

    assert employees == ["Alex Morgan", "Sam Taylor"]


@pytest.mark.parametrize(
    ("status", "expected_count"),
    [("todo", 2), ("in_progress", 2), ("done", 1)],
)
@allure.title("Tasks can be filtered by status")
@allure.feature("Database")
@allure.story("Filtering")
def test_tasks_by_status(db_connection, status, expected_count):
    with db_connection.cursor() as cursor:
        cursor.execute(
            "SELECT COUNT(*) FROM tasks WHERE status = %s",
            (status,),
        )
        count = cursor.fetchone()[0]

    assert count == expected_count


@allure.title("A new employee can be inserted and queried")
@allure.feature("Database")
@allure.story("Insert and transaction rollback")
def test_insert_employee_and_rollback(db_transaction):
    with db_transaction.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO employees (id, full_name, email, department_id, salary)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, full_name, email
            """,
            (999, "Test Employee", "rollback-check@example.test", 1, 50000),
        )
        inserted_employee = cursor.fetchone()

        cursor.execute(
            "SELECT full_name FROM employees WHERE email = %s",
            ("rollback-check@example.test",),
        )
        queried_name = cursor.fetchone()[0]

    assert inserted_employee == (
        999,
        "Test Employee",
        "rollback-check@example.test",
    )
    assert queried_name == "Test Employee"
    # The db_transaction fixture rolls the insert back after this test.


@allure.title("An employee cannot reference a missing department")
@allure.feature("Database")
@allure.story("Foreign key constraint")
def test_employee_with_unknown_department_is_rejected(db_transaction):
    with pytest.raises(psycopg.errors.ForeignKeyViolation):
        with db_transaction.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO employees (id, full_name, email, department_id, salary)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (998, "Invalid Employee", "invalid-dept@example.test", 9999, 50000),
            )


@allure.title("Employee email must be unique")
@allure.feature("Database")
@allure.story("Unique constraint")
def test_duplicate_employee_email_is_rejected(db_transaction):
    with pytest.raises(psycopg.errors.UniqueViolation):
        with db_transaction.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO employees (id, full_name, email, department_id, salary)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (997, "Duplicate Employee", "alex.morgan@example.test", 1, 50000),
            )
