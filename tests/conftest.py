import sys
import os
import pytest

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BASE_DIR)

from app import create_app
from extensions import db as _db

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "postgresql://postgres:Aass13579@localhost:5002/Database",
        "WTF_CSRF_ENABLED": False,
    })

    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def db(app):
    return _db


@pytest.fixture
def login_user(client):
    client.post("/login", data={
        "username": "user",
        "password": "P@ssw0rdF$t"
    })
    return client

@pytest.fixture
def admin_login(client):
    client.post("/login", data={
        "username": "admin",
        "password": "P@ssw0rdF$tIT"
    })
    return client
