from fastapi.testclient import TestClient
from main import app
from models import User, Role
from database import SessionLocal, engine
from sqlalchemy.orm import sessionmaker
import pytest

client = TestClient(app)

@pytest.fixture(scope="module")
def test_db():
    SessionLocal.configure(bind=engine)
    yield SessionLocal()

def test_register_user(test_db):
    response = client.post("/register/", json={
        "username": "testuser",
        "password": "testpass",
        "role": Role.USER.value
    })
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["role"] == Role.USER.value

def test_login_user(test_db):
    response = client.post("/token", data={
        "username": "testuser",
        "password": "testpass"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data

def test_assign_role(test_db):
    response = client.post("/assign_role/", json={
        "target_username": "testuser",
        "role": Role.ADMIN.value
    })
    assert response.status_code == 200

def test_add_contract_change(test_db):
    response = client.post("/add_contract_change/", json={
        "username": "testuser",
        "contract_data": {"position": "manager", "salary": "2000"}
    })
    assert response.status_code == 200
    assert response.json()["message"] == "Изменение контракта добавлено в блокчейн"

def test_create_vote(test_db):
    response = client.post("/create_vote/", json={
        "issue": "test_vote",
        "votes": {"user1": "yes", "user2": "no"}
    })
    assert response.status_code == 200
    assert response.json()["message"] == "Голосование добавлено в блокчейн"
