import allure


@allure.title("Connect to PostgreSQL")
@allure.feature("Database")
@allure.story("Connection")
def test_db_connection(db_connection):
    with db_connection.cursor() as cursor:
        cursor.execute(
            "SELECT current_database(), current_user"
        )
        database, user = cursor.fetchone()

    assert database == "api_testing"
    assert user == "test_user"


@allure.title("Insert and retrieve a database record")
@allure.feature("Database")
@allure.story("CRUD operations")
def test_insert_and_retrieve_record(db_connection):
    with db_connection.cursor() as cursor:
        cursor.execute("""
            CREATE TEMPORARY TABLE test_records (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL
            )
        """)

        cursor.execute(
            "INSERT INTO test_records (id, name) VALUES (%s, %s)",
            (1, "Test record"),
        )

        cursor.execute(
            "SELECT id, name FROM test_records WHERE id = %s",
            (1,),
        )

        record = cursor.fetchone()

    assert record == (1, "Test record")



@allure.title("Database transaction is rolled back")
@allure.feature("Database")
@allure.story("Transaction management")
def test_db_transaction_rollback(db_transaction):
    with db_transaction.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transaction_test (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL
            )
        """)
        cursor.execute(
            "INSERT INTO transaction_test (id, name) "
            "VALUES (999999, 'temporary') "
            "ON CONFLICT (id) DO NOTHING"
        )

        cursor.execute(
            "SELECT name FROM transaction_test WHERE id = %s",
            (999999,),
        )
        assert cursor.fetchone() == ("temporary",)
