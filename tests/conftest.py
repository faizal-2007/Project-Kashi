import os
import sys
from pathlib import Path

import mysql.connector
import pytest
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
load_dotenv(PROJECT_ROOT / ".env")

from app import app as flask_app  # noqa: E402


TEST_DB_NAME = os.getenv("TEST_DB_NAME", "project_kashi_test")

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "charset": "utf8mb4",
    "use_unicode": True,
    "autocommit": True,
}

SCRIPTS = [
    "schema.sql",
    "views.sql",
    "functions.sql",
    "procedures.sql",
    "triggers.sql",
]

TABLES = [
    "LOAN_PAYMENT",
    "LOAN",
    "BANK_TRANSACTION",
    "ACCOUNT_HOLDER",
    "ACCOUNT",
    "EMPLOYEE",
    "CUSTOMER",
    "BRANCH",
]


def server_connection(include_database=True):
    config = dict(DB_CONFIG)
    if include_database:
        config["database"] = TEST_DB_NAME
    return mysql.connector.connect(**config)


def split_sql_script(path, database_name):
    text = path.read_text(encoding="utf-8").replace("project_kashi", database_name)
    delimiter = ";"
    statements = []
    buffer = []

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.upper().startswith("DELIMITER "):
            delimiter = line.split(None, 1)[1]
            continue
        if not buffer and (not line or line.startswith("--")):
            continue
        buffer.append(raw_line)
        if line.endswith(delimiter):
            statement = "\n".join(buffer)
            statement = statement[: -len(delimiter)].strip()
            if statement:
                statements.append(statement)
            buffer = []

    if buffer and "\n".join(buffer).strip():
        statements.append("\n".join(buffer).strip())
    return statements


def run_script(connection, filename):
    cursor = connection.cursor()
    try:
        for statement in split_sql_script(PROJECT_ROOT / "sql" / filename, TEST_DB_NAME):
            cursor.execute(statement)
        connection.commit()
    finally:
        cursor.close()


@pytest.fixture(scope="session", autouse=True)
def initialized_database():
    try:
        connection = server_connection(include_database=False)
    except mysql.connector.Error as exc:
        pytest.skip(f"MySQL test server is unavailable: {exc}")

    try:
        for script in SCRIPTS:
            run_script(connection, script)
    finally:
        connection.close()


@pytest.fixture(autouse=True)
def clean_database(initialized_database):
    connection = server_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        for table in TABLES:
            cursor.execute(f"TRUNCATE TABLE {table}")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        cursor.execute(
            """
            INSERT INTO BRANCH (BranchID, BranchName, IFSCCode, Address, City, State, ContactNumber)
            VALUES (1, 'Test Branch', 'TEST0000001', '1 Test Road', 'Test City', 'Test State', '9000000001')
            """
        )
        connection.commit()
    finally:
        cursor.close()
        connection.close()


@pytest.fixture
def db():
    connection = server_connection()
    try:
        yield connection
    finally:
        connection.close()


@pytest.fixture
def client():
    flask_app.config.update(
        TESTING=True,
        WTF_CSRF_ENABLED=False,
        DB_HOST=DB_CONFIG["host"],
        DB_PORT=DB_CONFIG["port"],
        DB_USER=DB_CONFIG["user"],
        DB_PASSWORD=DB_CONFIG["password"],
        DB_NAME=TEST_DB_NAME,
        SECRET_KEY="test-secret-key",
    )
    return flask_app.test_client()


@pytest.fixture
def baseline(db):
    cursor = db.cursor()
    cursor.execute(
        """
        INSERT INTO CUSTOMER (FirstName, LastName, DateOfBirth, Gender, Mobile, Email, Address, City)
        VALUES ('Test', 'Customer', '1990-01-01', 'Male', '9999999999', 'test.customer@example.com', '1 Test Lane', 'Test City')
        """
    )
    customer_id = cursor.lastrowid
    cursor.execute(
        """
        INSERT INTO ACCOUNT (AccountNumber, AccountType, Balance, Status, BranchID)
        VALUES ('900000000001', 'Saving', 1000.00, 'Active', 1)
        """
    )
    account_id = cursor.lastrowid
    cursor.execute(
        """
        INSERT INTO ACCOUNT_HOLDER (CustomerID, AccountID, HolderType)
        VALUES (%s, %s, 'Primary')
        """,
        (customer_id, account_id),
    )
    db.commit()
    cursor.close()
    return {"customer_id": customer_id, "account_id": account_id}
