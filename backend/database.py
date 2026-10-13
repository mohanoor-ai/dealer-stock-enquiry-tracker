"""Small SQLite helpers. Each operation uses a short connection."""
import os
import sqlite3
from pathlib import Path


def connect():
    path = Path(os.environ.get('DEALER_DB', 'data/dealer.sqlite3'))
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute('PRAGMA foreign_keys = ON')
    return connection


def initialize():
    connection = connect()
    with connection:
        connection.executescript('''
        CREATE TABLE IF NOT EXISTS vehicles (
            id INTEGER PRIMARY KEY,
            make TEXT NOT NULL,
            model TEXT NOT NULL,
            year INTEGER NOT NULL,
            price_pence INTEGER NOT NULL CHECK(price_pence >= 0),
            status TEXT NOT NULL DEFAULT 'available'
                CHECK(status IN ('available','reserved','sold')),
            archived INTEGER NOT NULL DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS enquiries (
            id INTEGER PRIMARY KEY,
            vehicle_id INTEGER NOT NULL REFERENCES vehicles(id),
            customer TEXT NOT NULL,
            message TEXT NOT NULL,
            follow_up TEXT NOT NULL DEFAULT '',
            completed INTEGER NOT NULL DEFAULT 0
        );
        ''')
    connection.close()


def rows(sql, values=()):
    connection = connect()
    try:
        return [dict(row) for row in connection.execute(sql, values).fetchall()]
    finally:
        connection.close()


def write(sql, values=()):
    connection = connect()
    try:
        with connection:
            cursor = connection.execute(sql, values)
        return cursor.lastrowid
    finally:
        connection.close()
