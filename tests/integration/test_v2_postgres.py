import os
import pytest
from sqlalchemy import select
from backend_v2.database import build_engine, session_factory
from backend_v2.models import Base, Vehicle
from backend_v2 import limits, service, schemas


@pytest.mark.skipif(not os.environ.get('TEST_POSTGRES_URL'),reason='Requires an explicitly configured disposable PostgreSQL database')
def test_postgres_persistence_and_revision():
    engine=build_engine(os.environ['TEST_POSTGRES_URL']);Base.metadata.create_all(engine)
    sessions=session_factory(engine)
    with sessions.begin() as db:
        v=service.create(db,Vehicle,schemas.VehicleCreate(make='Integration',model='Demo',year=2020,price_pence=1))
    with sessions.begin() as db:
        assert service.record(db,Vehicle,v['id']).price_pence==1
        service.change(db,Vehicle,v['id'],schemas.VehicleUpdate(revision=1,status='reserved'))
    with sessions.begin() as db:
        with pytest.raises(service.Problem):service.change(db,Vehicle,v['id'],schemas.VehicleUpdate(revision=1,status='sold'))
    engine.dispose()
