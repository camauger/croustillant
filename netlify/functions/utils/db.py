import os
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager

@contextmanager
def get_db_connection():
    """
    Create and return a PostgreSQL database connection using psycopg2.
    Uses Netlify-provided DATABASE_URL environment variable.
    Returns results as dictionaries for easy JSON serialization.
    """
    database_url = os.environ.get("DATABASE_URL")

    if not database_url:
        raise ValueError("DATABASE_URL must be set in environment variables")

    conn = None
    try:
        # Connect with SSL and return results as dictionaries
        conn = psycopg2.connect(
            database_url,
            sslmode='require',
            cursor_factory=RealDictCursor
        )
        yield conn
    finally:
        if conn:
            conn.close()

def execute_query(query: str, params: tuple = None, fetch: str = 'all'):
    """
    Execute a SQL query and return results.

    Args:
        query: SQL query string with %s placeholders
        params: Tuple of parameters to bind to query
        fetch: 'all', 'one', or 'none' to control result fetching

    Returns:
        List of dicts, single dict, or None depending on fetch parameter
    """
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, params)

            if fetch == 'all':
                return [dict(row) for row in cursor.fetchall()]
            elif fetch == 'one':
                row = cursor.fetchone()
                return dict(row) if row else None
            else:  # fetch == 'none'
                conn.commit()
                return None

def execute_insert(query: str, params: tuple):
    """
    Execute an INSERT query and return the inserted row.

    Args:
        query: SQL INSERT query with RETURNING *
        params: Tuple of parameters to bind to query

    Returns:
        Dict representing the inserted row
    """
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            conn.commit()
            result = cursor.fetchone()
            return dict(result) if result else None

def execute_update(query: str, params: tuple):
    """
    Execute an UPDATE query and return the updated row(s).

    Args:
        query: SQL UPDATE query with RETURNING *
        params: Tuple of parameters to bind to query

    Returns:
        Dict representing the updated row
    """
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            conn.commit()
            result = cursor.fetchone()
            return dict(result) if result else None

def execute_delete(query: str, params: tuple):
    """
    Execute a DELETE query.

    Args:
        query: SQL DELETE query
        params: Tuple of parameters to bind to query

    Returns:
        Number of rows deleted
    """
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            rows_deleted = cursor.rowcount
            conn.commit()
            return rows_deleted

def format_response(status_code: int, body: dict, headers: dict = None) -> dict:
    """Format response for Netlify Functions"""
    default_headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS"
    }

    if headers:
        default_headers.update(headers)

    return {
        "statusCode": status_code,
        "headers": default_headers,
        "body": json.dumps(body, ensure_ascii=False)
    }

def handle_error(error: Exception, status_code: int = 500) -> dict:
    """Handle errors consistently"""
    error_message = str(error)
    print(f"Error: {error_message}")

    return format_response(status_code, {
        "error": error_message,
        "success": False
    })
