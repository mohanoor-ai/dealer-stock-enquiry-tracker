"""Create consistent SQLite or pg_dump backups outside the repository."""
import argparse
import os
from pathlib import Path
import sqlite3
from contextlib import closing
import subprocess
from urllib.parse import urlsplit, unquote


def pg_environment(url):
    parsed=urlsplit(url.replace('postgresql+psycopg://','postgresql://'))
    env=os.environ.copy()
    env.update(PGHOST=parsed.hostname or '',PGPORT=str(parsed.port or 5432),PGDATABASE=unquote(parsed.path.lstrip('/')),PGUSER=unquote(parsed.username or ''),PGPASSWORD=unquote(parsed.password or ''))
    env['PGSSLMODE']='require' if os.environ.get('APP_ENV')=='hosted' else 'prefer'
    return env


def backup(url, destination):
    dest=Path(destination).resolve()
    if dest.exists():raise ValueError('Backup destination already exists')
    if url.startswith('sqlite:///'):
        source=Path(url.removeprefix('sqlite:///')).resolve()
        if not source.exists():raise ValueError('Database not found')
        with closing(sqlite3.connect(source.as_uri()+'?mode=ro',uri=True)) as db, closing(sqlite3.connect(dest)) as out:db.backup(out)
    else:
        subprocess.run(['pg_dump','--format=custom','--file',str(dest)],env=pg_environment(url),check=True)
    return dest


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('destination');a=p.parse_args()
    try:print('Backup written:',backup(os.environ.get('MIGRATION_DATABASE_URL') or os.environ.get('DATABASE_URL','sqlite:///data/dealer-v2.sqlite3'),a.destination))
    except Exception as e:raise SystemExit('Backup failed. Check destination, database configuration and client tools; no credentials are printed.')
