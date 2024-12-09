import pytest
from blockchain_func import Blockchain
from models import Role, User


@pytest.fixture
def blockchain():
    return Blockchain()

@pytest.fixture
def admin_user():
    return User(username="admin", hashed_password="admin_hashed", role=Role.ADMIN)

@pytest.fixture
def regular_user():
    return User(username="user", hashed_password="user_hashed", role=Role.USER)

def test_add_user(blockchain, regular_user):
    blockchain.add_user(regular_user)
    assert blockchain.get_user("user") is not None
    assert blockchain.get_user("user").username == "user"

def test_assign_role(blockchain, admin_user, regular_user):
    blockchain.add_user(admin_user)
    blockchain.add_user(regular_user)
    success = blockchain.assign_role(admin_user, regular_user, Role.ADMIN)
    assert success is True
    assert blockchain.get_user("user").role == Role.ADMIN

def test_generate_unique_key(blockchain, regular_user):
    blockchain.add_user(regular_user)
    unique_key = blockchain.generate_unique_key(regular_user)
    assert unique_key is not None
    assert blockchain.get_user("user").unique_key == unique_key

def test_add_contract_change(blockchain, regular_user):
    blockchain.add_user(regular_user)
    contract_data = {"position": "developer", "salary": "1000"}
    blockchain.add_contract_change(regular_user, contract_data)
    assert len(blockchain.chain) > 1  # проверка, что новый блок был добавлен

def test_create_vote(blockchain):
    votes = {"voter1": "yes", "voter2": "no"}
    blockchain.create_vote("test_issue", votes)
    vote_results = blockchain.get_vote_results("test_issue")
    assert vote_results == votes

def test_close_vote(blockchain):
    votes = {"voter1": "yes", "voter2": "no"}
    blockchain.create_vote("test_issue", votes)
    results = blockchain.close_vote("test_issue")
    assert results == votes
