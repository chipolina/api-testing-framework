import psycopg
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

from config import DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USER

app = FastAPI(
    title="Local Employee API",
    description="A small API used to practise API-to-PostgreSQL integration tests.",
    version="0.1.0",
)


class EmployeeCreate(BaseModel):
    full_name: str = Field(min_length=1, max_length=200)
    email: str = Field(
        min_length=3,
        max_length=254,
        pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
    )
    department_id: int = Field(gt=0)
    salary: float = Field(gt=0)


class EmployeeUpdate(BaseModel):
    full_name: str = Field(min_length=1, max_length=200)
    salary: float = Field(gt=0)


def get_connection():
    return psycopg.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )


@app.get("/health")
def health_check():
    with get_connection() as connection:
        connection.execute("SELECT 1")
    return {"status": "ok"}


@app.post("/employees", status_code=status.HTTP_201_CREATED)
def create_employee(employee: EmployeeCreate):
    try:
        with get_connection() as connection:
            row = connection.execute(
                """
                INSERT INTO employees (full_name, email, department_id, salary)
                VALUES (%s, %s, %s, %s)
                RETURNING id, full_name, email, department_id, salary
                """,
                (
                    employee.full_name,
                    employee.email,
                    employee.department_id,
                    employee.salary,
                ),
            ).fetchone()
            return dict(row)
    except psycopg.errors.UniqueViolation as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An employee with this email already exists.",
        ) from exc
    except psycopg.errors.ForeignKeyViolation as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="The department does not exist.",
        ) from exc


@app.get("/employees/{employee_id}")
def get_employee(employee_id: int):
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT id, full_name, email, department_id, salary
            FROM employees
            WHERE id = %s
            """,
            (employee_id,),
        ).fetchone()

    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found.",
        )
    return dict(row)


@app.patch("/employees/{employee_id}")
def update_employee(employee_id: int, employee: EmployeeUpdate):
    with get_connection() as connection:
        row = connection.execute(
            """
            UPDATE employees
            SET full_name = %s, salary = %s
            WHERE id = %s
            RETURNING id, full_name, email, department_id, salary
            """,
            (employee.full_name, employee.salary, employee_id),
        ).fetchone()

    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found.",
        )
    return dict(row)
