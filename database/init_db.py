from pathlib import Path

import mysql.connector


def init_database(config):
    schema_path = Path(__file__).with_name("schema.sql")
    statements = _load_statements(schema_path)

    connection = mysql.connector.connect(
        host=config.DB_HOST,
        port=config.DB_PORT,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
    )
    cursor = connection.cursor()

    try:
        for statement in statements:
            cursor.execute(statement)
        connection.commit()
    finally:
        cursor.close()
        connection.close()


def _load_statements(schema_path):
    sql = schema_path.read_text(encoding="utf-8")
    return [
        statement.strip()
        for statement in sql.split(";")
        if statement.strip()
    ]
