import logging

import mysql.connector
from mysql.connector.pooling import MySQLConnectionPool

logger = logging.getLogger(__name__)

_pool: MySQLConnectionPool | None = None


def init_pool(config) -> None:
    global _pool
    _pool = MySQLConnectionPool(
        pool_name="biblioteca",
        pool_size=5,
        host=config.DB_HOST,
        port=config.DB_PORT,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        database=config.DB_NAME,
    )


def get_connection():
    if _pool is None:
        raise RuntimeError("Pool não inicializado. Chame init_pool antes de usar o banco.")
    return _pool.get_connection()


def fetch_all(query, params=None):
    connection = get_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(query, params or ())
            return cursor.fetchall()
        finally:
            cursor.close()
    finally:
        connection.close()


def fetch_one(query, params=None):
    connection = get_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(query, params or ())
            return cursor.fetchone()
        finally:
            cursor.close()
    finally:
        connection.close()


def execute(query, params=None):
    """INSERT/DELETE — returns last insert ID."""
    connection = get_connection()
    try:
        cursor = connection.cursor()
        try:
            cursor.execute(query, params or ())
            connection.commit()
            return cursor.lastrowid
        finally:
            cursor.close()
    finally:
        connection.close()


def execute_update(query, params=None):
    """UPDATE — returns number of affected rows."""
    connection = get_connection()
    try:
        cursor = connection.cursor()
        try:
            cursor.execute(query, params or ())
            connection.commit()
            return cursor.rowcount
        finally:
            cursor.close()
    finally:
        connection.close()
