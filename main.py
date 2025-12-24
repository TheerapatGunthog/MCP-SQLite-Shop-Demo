import os
from mcp.server.fastmcp import FastMCP, Context
import sqlite3
import json
from typing import List, Dict, Any

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "shop.db")

mcp = FastMCP("ShopDB_Service")

def get_db_connection():
    """Create a database connection with row factory enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@mcp.resource("sqlite://schema")
def get_database_schema() -> str:
    """
    Returns the full SQL schema of the database. 
    Use this to understand table structures, column names, and relationships.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND sql IS NOT NULL")
            schemas = [row["sql"] for row in cursor.fetchall()]
            return "\n\n".join(schemas)
    except Exception as e:
        return f"Error reading schema: {str(e)}"

@mcp.tool()
def list_tables() -> List[str]:
    """
    List all available table names in the database.
    Useful for a quick overview before querying specific tables.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        return [row["name"] for row in cursor.fetchall()]

@mcp.tool()
def read_query(sql_query: str, ctx: Context = None) -> str:
    """
    Execute a SELECT SQL query to retrieve data.
    
    Args:
        sql_query: The SQL SELECT statement to execute. 
                   MUST be a read-only query (SELECT only).
    
    Returns:
        JSON string containing the query results or error message.
    """
    normalized_query = sql_query.strip().upper()
    if not normalized_query.startswith("SELECT"):
        return "Error: Security Violation. Only SELECT queries are allowed via this tool."
    
    if ctx:
        ctx.info(f"Executing Query: {sql_query}")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql_query)
            rows = cursor.fetchall()
            
            results = [dict(row) for row in rows]
            
            if not results:
                return "Result: [] (No data found matching the query)"
            
            if len(results) > 100:
                return json.dumps(results[:100], default=str) + "\n...(truncated to first 100 rows)"
                
            return json.dumps(results, default=str, indent=2)

    except sqlite3.Error as e:
        return f"SQL Execution Error: {str(e)}"

if __name__ == "__main__":
    mcp.run()