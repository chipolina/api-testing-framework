import psycopg

from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD


def main():
    with psycopg.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT current_database(), current_user")
            print(cursor.fetchone())


if __name__ == "__main__":
    main()
