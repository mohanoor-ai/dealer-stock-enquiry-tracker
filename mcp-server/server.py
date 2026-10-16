"""Read-only V2 aggregates through the official SDK; no arbitrary query input."""
from pathlib import Path
import os
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from sqlalchemy import select, func
from backend_v2.database import build_engine
from backend_v2.models import Vehicle
from mcp.server.fastmcp import FastMCP

mcp = FastMCP('dealer-read-only')

@mcp.tool()
def stock_counts() -> dict:
    """Return stock counts only; never return customer data."""
    url=os.environ.get('MCP_DATABASE_URL')
    if not url:return {'error':'Configure a separately authorised read-only database connection'}
    engine=build_engine(url)
    try:
        with engine.connect() as connection:
            rows=connection.execute(select(Vehicle.status,func.count()).where(Vehicle.archived.is_(False)).group_by(Vehicle.status))
            return dict(rows.all())
    except Exception:
        return {'error':'Aggregate read unavailable'}
    finally:
        engine.dispose()

if __name__ == '__main__':
    mcp.run(transport='stdio')

