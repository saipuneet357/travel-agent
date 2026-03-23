"""
This file contains the functions to connect to the database and get or create a user.
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor

def get_conn():
    """
    Connect to the database and retrieve connection object.
    Uses environment variables with defaults for backward compatibility.
    """
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        dbname=os.getenv("DB_NAME", "lara"),
        user=os.getenv("DB_USER", "puneet"),
        password=os.getenv("DB_PASSWORD", "puneet"),
    )

def get_or_create_user(subid: str, provider: str):
    """
    Get or create a user in the database
    """
    conn = get_conn()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM lara.users WHERE subid = %s", (subid,))
        row = cur.fetchone()
        if row:
            return row
        cur.execute(
            """
            INSERT INTO lara.users (subid, provider)
            VALUES (%s, %s)
            RETURNING *
            """,
            (subid, provider),
        )
        conn.commit()
        return cur.fetchone()
