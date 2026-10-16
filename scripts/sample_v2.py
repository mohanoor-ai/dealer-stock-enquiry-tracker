"""Explicit, repeat-safe sample import. Run locally against the intended database."""
import json
from pathlib import Path
from sqlalchemy import select, func
from backend_v2.models import Base, Vehicle
from backend_v2.database import build_engine, session_factory
from backend_v2.schemas import VehicleCreate
from backend_v2.service import create


def main():
    engine=build_engine()
    with session_factory(engine).begin() as db:
        if db.scalar(select(func.count()).select_from(Vehicle)):
            raise SystemExit('Import refused: stock must be empty. Existing records were preserved.')
        rows=json.loads((Path(__file__).resolve().parents[1]/'frontend-v2/src/education-stock.json').read_text())
        for row in rows:
            create(db,Vehicle,VehicleCreate(**{k:row[k] for k in ['make','model','year','price_pence','approved_facts']}))
    engine.dispose()
    print('Historical samples imported. Availability is simulated; prices are not current valuations.')


if __name__=='__main__':main()
