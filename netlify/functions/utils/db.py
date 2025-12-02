import os
import json
from supabase import create_client, Client

def get_supabase_client() -> Client:
    """Create and return a Supabase client instance"""
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")

    if not url or not key:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")

    return create_client(url, key)

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
