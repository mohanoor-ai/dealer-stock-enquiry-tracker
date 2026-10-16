"""Restore only into a new SQLite file or explicitly empty PostgreSQL database."""
import argparse
import os
from pathlib import Path
import sqlite3
from contextlib import closing
import subprocess
from scripts.backup import pg_environment


def restore(source,url):
    source=Path(source).resolve()
    if not source.is_file():raise ValueError('Backup not found')
    if url.startswith('sqlite:///'):
        target=Path(url.removeprefix('sqlite:///')).resolve()
        if target.exists():raise ValueError('Restore target must be new')
        target.parent.mkdir(parents=True,exist_ok=True)
        with closing(sqlite3.connect(source.as_uri()+'?mode=ro',uri=True)) as db,closing(sqlite3.connect(target)) as dest:
            if db.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise ValueError('Invalid backup')
            db.backup(dest)
    else:
        env=pg_environment(url)
        check=subprocess.run(['psql','--no-psqlrc','-Atc',"SELECT count(*) FROM information_schema.tables WHERE table_schema='public'"],env=env,text=True,capture_output=True,check=True)
        if check.stdout.strip()!='0':raise ValueError('PostgreSQL restore target must be empty')
        subprocess.run(['pg_restore','--no-owner','--no-acl','--exit-on-error','--dbname',env['PGDATABASE'],str(source)],env=env,check=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('source');p.add_argument('--target',required=True);a=p.parse_args()
    try:restore(a.source,a.target);print('Restore completed. Verify counts and application behavior before use.')
    except Exception:raise SystemExit('Restore failed. Check the empty target and client tools; no credentials are printed.')
