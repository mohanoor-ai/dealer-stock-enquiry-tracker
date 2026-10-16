"""Opt-in V1 SQLite → empty V2 database. Dry run unless --apply is supplied."""
import argparse
from datetime import date
from pathlib import Path
import sqlite3
from contextlib import closing
from sqlalchemy import select, func
from backend_v2.database import build_engine, session_factory
from backend_v2.models import Base, Vehicle, Enquiry, Task


def migrate(source, target, apply=False):
    source=Path(source).resolve()
    if not source.is_file():raise ValueError('Source database does not exist')
    with closing(sqlite3.connect(source.as_uri()+'?mode=ro',uri=True)) as old:
        old.row_factory=sqlite3.Row
        vehicles=[dict(r) for r in old.execute('SELECT * FROM vehicles')]
        enquiries=[dict(r) for r in old.execute('SELECT * FROM enquiries')]
    engine=build_engine(target)
    try:
        with session_factory(engine).begin() as db:
            for model in [Vehicle,Enquiry,Task]:
                if db.scalar(select(func.count()).select_from(model)):
                    raise ValueError('Target must be empty; repeat import refused')
            scheduled=[e for e in enquiries if e['follow_up']]
            for e in scheduled:date.fromisoformat(e['follow_up'])
            report={'vehicles':len(vehicles),'enquiries':len(enquiries),'tasks':len(scheduled),'undated_followups':sum(not e['follow_up'] for e in enquiries),'applied':False}
            if not apply:return report
            backup=source.with_name(source.name+'.before-v2.bak')
            if backup.exists():raise ValueError('Backup already exists; preserve it and choose another source copy')
            with closing(sqlite3.connect(source.as_uri()+'?mode=ro',uri=True)) as old, closing(sqlite3.connect(backup)) as dest:old.backup(dest)
            vehicle_ids={}
            for v in vehicles:
                row=Vehicle(make=v['make'],model=v['model'],year=v['year'],price_pence=v['price_pence'],status=v['status'],archived=bool(v['archived']),approved_facts=[])
                db.add(row);db.flush();vehicle_ids[v['id']]=row.id
            for e in enquiries:
                row=Enquiry(vehicle_id=vehicle_ids[e['vehicle_id']],customer=e['customer'],message=e['message'],status='closed' if e['completed'] else 'new')
                db.add(row);db.flush()
                if e['follow_up']:db.add(Task(enquiry_id=row.id,due_date=date.fromisoformat(e['follow_up']),completed=bool(e['completed']),note='Imported baseline follow-up'))
            db.flush()
            report['applied']=True
            return report
    finally:engine.dispose()


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('source');p.add_argument('--target',required=True);p.add_argument('--apply',action='store_true');a=p.parse_args()
    print(migrate(a.source,a.target,a.apply))
