from datetime import timedelta
import pytest
from sqlalchemy import select
from pydantic import ValidationError
from backend_v2.database import build_engine, session_factory
from backend_v2.models import Base, Vehicle, Enquiry, Task, AuditEvent
from backend_v2 import service as svc, schemas as s, limits, ai


@pytest.fixture
def sessions(tmp_path):
    engine = build_engine('sqlite:///' + (tmp_path / 'v2.sqlite3').as_posix())
    Base.metadata.create_all(engine)
    yield session_factory(engine)
    engine.dispose()


def stock(db):
    return svc.create(db, Vehicle, s.VehicleCreate(make='Demo', model='City', year=2020, price_pence=1230000, approved_facts=['Blue paint']))


def test_persistent_full_journey_and_archive(sessions):
    with sessions.begin() as db:
        v = stock(db)
        e = svc.create(db, Enquiry, s.EnquiryCreate(vehicle_id=v['id'], customer='Fictional', message='Visit'))
        t = svc.create(db, Task, s.TaskCreate(enquiry_id=e['id'], due_date=svc.today()))
    with sessions.begin() as db:
        assert svc.dashboard(db)['open_tasks'] == 1
        svc.change(db, Task, t['id'], s.TaskUpdate(revision=1, completed=True))
        assert svc.dashboard(db)['open_tasks'] == 0
        svc.change(db, Vehicle, v['id'], s.VehicleUpdate(revision=1, archived=True))
        result = svc.change(db, Vehicle, v['id'], s.VehicleUpdate(revision=2, status='sold'))
        assert result['archived'] is True
        assert svc.page(db, Vehicle)['total'] == 0
        assert svc.page(db, Vehicle, include_archived=True)['total'] == 1
        with pytest.raises(svc.Problem) as error:
            svc.create(db, Enquiry, s.EnquiryCreate(vehicle_id=v['id'], customer='Demo', message='Hi'))
        assert error.value.status == 409
        svc.change(db, Vehicle, v['id'], s.VehicleUpdate(revision=3, status='available', archived=False))
        assert svc.dashboard(db)['stock_value_pence'] == 1230000
        assert len(db.scalars(select(AuditEvent)).all()) == 7


def test_stale_write_cannot_overwrite(sessions):
    with sessions.begin() as db:
        v = stock(db)
    with sessions.begin() as db:
        svc.change(db, Vehicle, v['id'], s.VehicleUpdate(revision=1, status='reserved'))
    with sessions.begin() as db:
        with pytest.raises(svc.Problem) as error:
            svc.change(db, Vehicle, v['id'], s.VehicleUpdate(revision=1, status='sold'))
        assert error.value.current_revision == 2
        assert svc.record(db, Vehicle, v['id']).status == 'reserved'


def test_literal_search_and_pagination(sessions):
    with sessions.begin() as db:
        stock(db)
        svc.create(db, Vehicle, s.VehicleCreate(make='100%', model='Demo', year=2021, price_pence=0))
        assert svc.page(db, Vehicle, q='%')['total'] == 1
        assert svc.page(db, Vehicle, offset=1, limit=1)['items'][0]['make'] == 'Demo'


def test_dates_closed_enquiries_and_transitions(sessions):
    with sessions.begin() as db:
        v=stock(db)
        e=svc.create(db, Enquiry, s.EnquiryCreate(vehicle_id=v['id'], customer='Demo', message='Hi'))
        with pytest.raises(svc.Problem):
            svc.create(db, Task, s.TaskCreate(enquiry_id=e['id'], due_date=svc.today()-timedelta(days=1)))
        svc.change(db, Enquiry, e['id'], s.EnquiryUpdate(revision=1,status='closed'))
        with pytest.raises(svc.Problem):
            svc.create(db, Task, s.TaskCreate(enquiry_id=e['id'], due_date=svc.today()))
        svc.change(db, Vehicle, v['id'], s.VehicleUpdate(revision=1,status='sold'))
        with pytest.raises(svc.Problem):
            svc.change(db, Vehicle, v['id'], s.VehicleUpdate(revision=2,status='reserved'))


def test_strict_models_and_nonempty_updates():
    for values in [{'revision':True,'archived':True},{'revision':1},{'revision':1,'archived':'false'},{'revision':1,'make':None}]:
        with pytest.raises(ValidationError):s.VehicleUpdate(**values)
    with pytest.raises(ValidationError):s.VehicleCreate(make=' ',model='One',year=2020,price_pence=100)
    with pytest.raises(ValidationError):s.VehicleCreate(make='Demo',model='One',year=2020,price_pence=1.5)


def test_shared_quota(sessions):
    limits.consume(sessions,'test','operator',2,86400)
    limits.consume(sessions,'test','operator',2,86400)
    with pytest.raises(svc.Problem) as error:limits.consume(sessions,'test','operator',2,86400)
    assert error.value.status == 429


def test_ai_fact_validation_and_disabled_default(monkeypatch):
    v=Vehicle(make='Demo',model='City',year=2020,approved_facts=['Blue'])
    monkeypatch.setenv('AI_PROVIDER','disabled')
    with pytest.raises(svc.Problem):ai.draft(v)
    with pytest.raises(svc.Problem):ai.render(v,ai.Selection(fact_indexes=[9]))
    result=ai.render(v,ai.Selection(fact_indexes=[0]))
    assert result['text']=='2020 Demo City. Approved details: Blue'
    assert result['requires_review'] is True
