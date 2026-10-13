"""Optional official SDK example; install mcp separately before use."""
from pathlib import Path
import sqlite3
from mcp.server.fastmcp import FastMCP

mcp = FastMCP('dealer-read-only')
DB_PATH = Path(__file__).resolve().parents[1] / 'data/dealer.sqlite3'

@mcp.tool()
def stock_counts() -> dict:
    """Return stock counts only; never return customer data."""
    if not DB_PATH.exists():
        return {'error':'Run and seed the local app first.'}
    connection=sqlite3.connect(DB_PATH.resolve().as_uri()+'?mode=ro',uri=True)
    try:
        rows=connection.execute('SELECT status,COUNT(*) FROM vehicles WHERE archived=0 GROUP BY status').fetchall()
        return dict(rows)
    finally:
        connection.close()

if __name__ == '__main__':
    mcp.run(transport='stdio')
