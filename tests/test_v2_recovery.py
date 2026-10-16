from pathlib import Path
from contextlib import closing
import sqlite3
import pytest
from backend_v2.database import build_engine
from backend_v2.models import Base
from scripts.migrate_baseline import migrate
from scripts.backup import backup
from scripts.restore import restore


def test_backup_restore_and_repeat_import_refused(tmp_path):
    source=tmp_path/'baseline.sqlite3'
    with closing(sqlite3.connect(source)) as db, db:
        db.executescript("CREATE TABLE vehicles(id INTEGER PRIMARY KEY,make TEXT,model TEXT,year INTEGER,price_pence INTEGER,status TEXT,archived INTEGER); CREATE TABLE enquiries(id INTEGER PRIMARY KEY,vehicle_id INTEGER,customer TEXT,message TEXT,follow_up TEXT,completed INTEGER);")
        db.execute("INSERT INTO vehicles VALUES (1,'Demo','City',2020,123,'available',0)")
        db.execute("INSERT INTO enquiries VALUES (1,1,'Fictional','Visit','2026-10-20',0)")
    target='sqlite:///'+(tmp_path/'v2.sqlite3').as_posix()
    engine=build_engine(target);Base.metadata.create_all(engine);engine.dispose()
    assert migrate(source,target)['applied'] is False
    result=migrate(source,target,True)
    assert result['tasks']==1 and result['applied'] is True
    assert source.with_name(source.name+'.before-v2.bak').exists()
    with pytest.raises(ValueError):migrate(source,target,True)
    archive=tmp_path/'saved.sqlite3';backup(target,archive)
    restored=tmp_path/'restored.sqlite3';restore(archive,'sqlite:///'+restored.as_posix())
    with closing(sqlite3.connect(restored)) as db:
        assert db.execute('SELECT count(*) FROM vehicles_v2').fetchone()[0]==1
        assert db.execute('SELECT count(*) FROM tasks_v2').fetchone()[0]==1
