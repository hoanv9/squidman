import pytest
from app import create_app, db

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['LOGIN_DISABLED'] = True  # Disable login for route tests
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

def test_dashboard(client):
    response = client.get('/dashboard')
    assert response.status_code == 200

def test_manage_clients(client):
    response = client.get('/clients')
    assert response.status_code == 200

def test_add_client(client):
    response = client.get('/clients/add')
    assert response.status_code == 200