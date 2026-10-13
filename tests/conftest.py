import pytest
from fastapi.testclient import TestClient
from backend.app import app

@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv('DEALER_DB', str(tmp_path / 'test.sqlite3'))
    with TestClient(app) as client:
        yield client
