import os

from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv(
    "BASE_URL",
    "https://restful-booker.herokuapp.com",
)
LOCAL_API_BASE_URL = os.getenv(
    "LOCAL_API_BASE_URL",
    "http://localhost:8000",
)

DB_HOST = os.environ["DB_HOST"]
DB_PORT = int(os.environ["DB_PORT"])
DB_NAME = os.environ["DB_NAME"]
DB_USER = os.environ["DB_USER"]
DB_PASSWORD = os.environ["DB_PASSWORD"]
