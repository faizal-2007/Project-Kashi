from contextlib import contextmanager

import mysql.connector
from flask import current_app


def _connection_settings(include_database=True):
    settings = {
        "host": current_app.config["DB_HOST"],
        "port": current_app.config["DB_PORT"],
        "user": current_app.config["DB_USER"],
        "password": current_app.config["DB_PASSWORD"],
        "autocommit": False,
        "connection_timeout": 8,
        "charset": "utf8mb4",
        "use_unicode": True,
    }
    if include_database:
        settings["database"] = current_app.config["DB_NAME"]
    return settings


def get_connection(include_database=True):
    return mysql.connector.connect(**_connection_settings(include_database))


def check_connection(include_database=True):
    connection = get_connection(include_database=include_database)
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
    finally:
        connection.close()
    return True


def query_all(sql, params=()):
    connection = get_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        cursor.close()
        return rows
    finally:
        connection.close()


def query_one(sql, params=()):
    connection = get_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(sql, params)
        row = cursor.fetchone()
        cursor.close()
        return row
    finally:
        connection.close()


def execute(sql, params=()):
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute(sql, params)
        connection.commit()
        result = (cursor.lastrowid, cursor.rowcount)
        cursor.close()
        return result
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def execute_many(sql, parameter_sets):
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.executemany(sql, parameter_sets)
        connection.commit()
        affected = cursor.rowcount
        cursor.close()
        return affected
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


@contextmanager
def transaction():
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    connection.start_transaction()
    try:
        yield connection, cursor
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()


def call_procedure(procedure_name, args):
    connection = get_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.callproc(procedure_name, args)
        result_sets = []
        for result in cursor.stored_results():
            result_sets.append(result.fetchall())
        connection.commit()
        cursor.close()
        return result_sets
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
