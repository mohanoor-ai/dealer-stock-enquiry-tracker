import os,tempfile
from datetime import date
from pathlib import Path
from alembic.config import Config
from alembic import command
from sqlalchemy import inspect,select
from sqlalchemy.exc import IntegrityError
from backend_v2.database import build_engine,session_factory
from backend_v2.models import Vehicle,Enquiry,Task
with tempfile.TemporaryDirectory() as folder:
    os.environ['DATABASE_URL']='sqlite:///'+str(Path(folder)/'test.sqlite3')
    config=Config('alembic.ini');command.upgrade(config,'head')
    engine=build_engine();Session=session_factory(engine)
    with Session.begin() as session:
        vehicle=Vehicle(make='Demo',model='City',year=2020,price_pence=950000);session.add(vehicle);session.flush()
        enquiry=Enquiry(vehicle_id=vehicle.id,customer='Demo buyer',message='Demo');session.add(enquiry);session.flush()
        session.add(Task(enquiry_id=enquiry.id,due_date=date(2026,10,20)))
    engine.dispose();engine=build_engine();Session=session_factory(engine)
    with Session() as session:assert session.scalars(select(Task)).one().due_date==date(2026,10,20)
    for model in [Vehicle(make='Demo',model='Bad',year=2020,price_pence=-1),Enquiry(vehicle_id=999,customer='Demo',message='Bad')]:
        try:
            with Session.begin() as session:session.add(model)
            raise AssertionError('Constraint not enforced')
        except IntegrityError:pass
    engine.dispose();command.downgrade(config,'base');engine=build_engine();assert set(inspect(engine).get_table_names())=={'alembic_version'};engine.dispose()
    command.upgrade(config,'head')
    print('PASS: migration up/down/up, persisted vehicle/enquiry/task, negative-price and missing-parent constraints.')
