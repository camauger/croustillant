import os
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import SimpleConnectionPool
from contextlib import contextmanager

# Connection pool for reusing connections
_connection_pool = None

def get_connection_pool():
    """Get or create a connection pool"""
    global _connection_pool

    if _connection_pool is None:
        database_url = os.environ.get("DATABASE_URL")

        if not database_url:
            raise ValueError("DATABASE_URL must be set in environment variables")

        # Create a connection pool with min 1, max 10 connections
        _connection_pool = SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            dsn=database_url
        )

    return _connection_pool

@contextmanager
def get_db_connection():
    """
    Context manager for database connections
    Automatically handles connection acquisition and release
    """
    pool = get_connection_pool()
    conn = pool.getconn()

    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        pool.putconn(conn)

@contextmanager
def get_db_cursor(cursor_factory=RealDictCursor):
    """
    Context manager for database cursors
    Returns dict-like cursor by default for easier JSON serialization
    """
    with get_db_connection() as conn:
        cursor = conn.cursor(cursor_factory=cursor_factory)
        try:
            yield cursor
        finally:
            cursor.close()

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
        "body": json.dumps(body, ensure_ascii=False, default=str)
    }

def handle_error(error: Exception, status_code: int = 500) -> dict:
    """Handle errors consistently"""
    error_message = str(error)
    print(f"Error: {error_message}")

    # Don't expose internal errors in production
    user_message = "An internal error occurred" if status_code == 500 else error_message

    return format_response(status_code, {
        "error": user_message,
        "success": False
    })

def execute_query(query: str, params: tuple = None, fetch_one: bool = False):
    """
    Execute a SELECT query and return results

    Args:
        query: SQL query string with %s placeholders
        params: Tuple of parameters to substitute
        fetch_one: If True, return single row; if False, return all rows

    Returns:
        Single dict (fetch_one=True) or list of dicts
    """
    with get_db_cursor() as cursor:
        cursor.execute(query, params or ())

        if fetch_one:
            result = cursor.fetchone()
            return dict(result) if result else None
        else:
            results = cursor.fetchall()
            return [dict(row) for row in results]

def execute_insert(query: str, params: tuple = None, returning: bool = True):
    """
    Execute an INSERT query

    Args:
        query: SQL INSERT query
        params: Tuple of parameters
        returning: If True, expects RETURNING clause and returns the row

    Returns:
        Inserted row as dict if returning=True, otherwise None
    """
    with get_db_cursor() as cursor:
        cursor.execute(query, params or ())

        if returning:
            result = cursor.fetchone()
            return dict(result) if result else None
        return None

def execute_update(query: str, params: tuple = None, returning: bool = True):
    """
    Execute an UPDATE query

    Args:
        query: SQL UPDATE query
        params: Tuple of parameters
        returning: If True, expects RETURNING clause and returns updated rows

    Returns:
        Updated row(s) as dict/list if returning=True
    """
    with get_db_cursor() as cursor:
        cursor.execute(query, params or ())

        if returning:
            results = cursor.fetchall()
            if len(results) == 1:
                return dict(results[0])
            return [dict(row) for row in results]
        return None

def execute_delete(query: str, params: tuple = None):
    """
    Execute a DELETE query

    Args:
        query: SQL DELETE query
        params: Tuple of parameters

    Returns:
        Number of rows deleted
    """
    with get_db_cursor() as cursor:
        cursor.execute(query, params or ())
        return cursor.rowcount
