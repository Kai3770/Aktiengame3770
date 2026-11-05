import os

import psycopg
from psycopg.rows import dict_row


def get_db():
    """Neue Datenbankverbindung. Zeilen kommen als Dictionaries zurück."""
    return psycopg.connect(
        host=os.getenv("DB_HOST", "localhost"),
        dbname=os.getenv("DB_NAME", "postgres"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "postgres"),
        port=int(os.getenv("DB_PORT", "5432")),
        row_factory=dict_row,
    )
