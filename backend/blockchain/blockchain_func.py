import datetime as _dt
import hashlib as _hashlib
import json as _json
import os
import sys

from passlib.context import CryptContext

from cryptography.fernet import Fernet
from backend.models import Role, User

# Инициализация контекста для хэширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Blockchain:
    def __init__(self) -> None:
        self.chain = []
        self.users = {}
        self.encryption_key = Fernet.generate_key()
        self.cipher = Fernet(self.encryption_key)

        # Генезис блок
        genesis_block = self._create_block(data='Genesis Block', proof=1, previous_hash="0", index=0)
        self.chain.append(genesis_block)

    # Шифрование и дешифрование данных
    def encrypt_data(self, data: str) -> str:
        return self.cipher.encrypt(data.encode()).decode()

    def decrypt_data(self, encrypted_data: str) -> str:
        return self.cipher.decrypt(encrypted_data.encode()).decode()

    # Управление пользователями
    def add_user(self, user: User):
        self.users[user.username] = user

    def get_user(self, username: str) -> User:
        return self.users.get(username)

    def assign_role(self, admin: User, target_user: User, role: Role):
        if admin.role == Role.ADMIN:
            target_user.role = role
            self.add_user(target_user)
            return True
        return False

    def generate_unique_key(self, user: User):
        key_data = f"{user.username}{_dt.datetime.now().isoformat()}"
        unique_key = _hashlib.sha256(key_data.encode()).hexdigest()
        user.unique_key = unique_key
        self.add_user(user)
        return unique_key

    # Управление контрактами сотрудников
    def add_contract_change(self, user: User, contract_data: dict):
        contract_hash = _hashlib.sha256(_json.dumps(contract_data, sort_keys=True).encode()).hexdigest()
        data = {
            "type": "contract_change",
            "username": user.username,
            "contract_hash": contract_hash,
            "details": contract_data
        }
        self.mine_block(data=_json.dumps(data))
        self.log_security_event(f"Contract change added for {user.username}")

    def get_employee_info(self, username: str):
        user = self.get_user(username)
        if user:
            return {
                "username": user.username,
                "position": user.position,
                "contract_active": user.contract_active,
                "last_update": user.last_update
            }
        return None

    def get_current_employee_info(self):
        return [
            {
                "username": user.username,
                "position": user.position,
                "contract_active": user.contract_active,
                "last_update": user.last_update
            }
            for user in self.users.values()
        ]

    # Управление голосованиями
    def create_vote(self, issue: str, votes: dict):
        vote_data = {
            "type": "vote",
            "issue": issue,
            "votes": votes,
            "timestamp": str(_dt.datetime.now())
        }
        self.mine_block(data=_json.dumps(vote_data))

    def collect_votes(self, issue: str, votes: list):
        vote_dict = {vote['voter']: vote['vote'] for vote in votes}
        self.create_vote(issue, vote_dict)
        return vote_dict

    def get_vote_results(self, issue: str):
        for block in reversed(self.chain):
            # Проверяем, есть ли ключ 'type' и 'issue' в блоке
            if "type" in block and "issue" in block:
                if block["type"] == "vote" and block["issue"] == issue:
                    return block["votes"]
        return {}

    def close_vote(self, issue: str):
        # Находим блок с голосованием и помечаем его как закрытое
        for block in reversed(self.chain):
            if "type" in block and "issue" in block:
                if block["type"] == "vote" and block["issue"] == issue:
                    block["closed"] = True
                    self.mine_block(data=_json.dumps(block))
                    self.log_security_event(f"Vote on issue '{issue}' closed.")
                    return block["votes"]
        return None

    # Логирование событий доступа к данным
    def log_data_access(self, accessing_user: User, target_user: User, key: str):
        access_log = {
            "type": "data_access",
            "accessing_user": accessing_user.username,
            "target_user": target_user.username,
            "data_key": key,
            "timestamp": str(_dt.datetime.now())
        }
        self.mine_block(data=_json.dumps(access_log))
        self.log_security_event(f"Data access by {accessing_user.username} to {target_user.username}'s data key {key}")

    def check_access(self, user: User, key: str) -> bool:
        if user.role == Role.ADMIN:
            return True
        # Проверка доступа к данным (может быть настроено по-другому)
        return False

    # Блокчейн функции
    def mine_block(self, data: str) -> dict:
        previous_block = self.get_previous_block()
        previous_proof = previous_block["proof"]
        index = len(self.chain)

        proof = self._proof_of_work(previous_proof, index, data)
        previous_hash = self._hash(previous_block)

        block = self._create_block(data, proof, previous_hash, index)
        self.chain.append(block)

        return block

    def _hash(self, block: dict) -> str:
        encoded_block = _json.dumps(block, sort_keys=True).encode()
        return _hashlib.sha256(encoded_block).hexdigest()

    def _to_digest(self, new_proof: int, previous_proof: int, index: int, data: str):
        return f"{new_proof ** 2 - previous_proof ** 2 + index}{data}".encode()

    def _proof_of_work(self, previous_proof: int, index: int, data: str) -> int:
        new_proof = 1
        check_proof = False

        while not check_proof:
            to_digest = self._to_digest(new_proof, previous_proof, index, data)
            hash_value = _hashlib.sha256(to_digest).hexdigest()

            if hash_value[:4] == '0000':  # Условие завершения работы
                check_proof = True
            else:
                new_proof += 1

        return new_proof

    def get_previous_block(self) -> dict:
        return self.chain[-1]

    def _create_block(self, data: str, proof: int, previous_hash: str, index: int) -> dict:
        block = {
            "index": index,
            "timestamp": str(_dt.datetime.now()),
            "data": data,
            "proof": proof,
            "previous_hash": previous_hash,
        }
        return block

    # Проверка целостности цепочки блоков
    def is_chain_valid(self) -> bool:
        current_block = self.chain[0]
        block_index = 1

        while block_index < len(self.chain):
            next_block = self.chain[block_index]

            if next_block["previous_hash"] != self._hash(current_block):
                print('Invalid block:', next_block["index"])
                return False

            current_proof = current_block["proof"]
            next_index, next_data, next_proof = (
                next_block["index"],
                next_block["data"],
                next_block["proof"]
            )

            hash_value = _hashlib.sha256(
                self._to_digest(new_proof=next_proof, previous_proof=current_proof, index=next_index, data=next_data)
            ).hexdigest()

            if hash_value[:4] != '0000':  # Условие для проверки корректности блока
                print('Invalid block:', next_block["index"])
                return False

            current_block = next_block
            block_index += 1

        return True

    # Логирование и аудит безопасности
    def log_security_event(self, event: str):
        log_data = {
            "type": "security_event",
            "event": event,
            "timestamp": str(_dt.datetime.now())
        }
        self.mine_block(data=_json.dumps(log_data))

    def audit_chain(self):
        if not self.is_chain_valid():
            self.log_security_event("Blockchain integrity check failed")
            self.notify_admin("Blockchain integrity check failed")
        else:
            self.log_security_event("Blockchain integrity check passed")

    def notify_admin(self, message: str):
        print(f"Admin notification: {message}")

#
# def blockchain_demo():
#     # Инициализация блокчейна
#     blockchain = Blockchain()
#
#     # Создание пользователей
#
#     # Создаем пользователей с хэшированными паролями
#     admin_user = User(
#         username="admin1",
#         role=Role.ADMIN,
#         hashed_password=pwd_context.hash("admin_password")
#     )
#
#     user1 = User(
#         username="user1",
#         role=Role.USER,
#         hashed_password=pwd_context.hash("user1_password")
#     )
#
#     user2 = User(
#         username="user2",
#         role=Role.USER,
#         hashed_password=pwd_context.hash("user2_password")
#     )
#
#     # Добавление пользователей в блокчейн
#     blockchain.add_user(admin_user)
#     blockchain.add_user(user1)
#     blockchain.add_user(user2)
#     print("\n=== Пользователи успешно добавлены в блокчейн ===")
#
#     # Назначение роли
#     blockchain.assign_role(admin_user, user1, Role.ADMIN)
#     print(f"\nРоль пользователя {user1.username}: {user1.role}")
#
#     # Генерация уникального ключа для пользователя
#     unique_key = blockchain.generate_unique_key(user1)
#     print(f"Уникальный ключ для {user1.username}: {unique_key}")
#
#     # Попытка добавления изменения контракта обычным пользователем (без прав администратора)
#     contract_data = {"salary": 5000, "position": "Engineer"}
#     try:
#         blockchain.add_contract_change(user2, contract_data)  # Это действие требует прав администратора
#     except PermissionError as e:
#         print(f"\nОшибка: {e}")
#
#     # Добавление изменения контракта администратором
#     blockchain.add_contract_change(admin_user, contract_data)
#     print(f"\nИзменение контракта добавлено администратором: {contract_data}")
#
#     # Получение информации о пользователе
#     employee_info = blockchain.get_employee_info("user1")
#     print(f"\nИнформация о {user1.username}: {employee_info}")
#
#     # Получение текущей информации о сотрудниках
#     current_employee_info = blockchain.get_current_employee_info()
#     print(f"\nТекущие сотрудники:\n{current_employee_info}")
#
#     # Создание и закрытие голосования
#     votes = [{"voter": "user1", "vote": "yes"}, {"voter": "user2", "vote": "no"}]
#     blockchain.collect_votes(issue="Approve project", votes=votes)
#     vote_results = blockchain.get_vote_results("Approve project")
#     print(f"\nРезультаты голосования по вопросу 'Approve project': {vote_results}")
#
#     blockchain.close_vote("Approve project")
#     print("\nГолосование по вопросу 'Approve project' закрыто.")
#
#     # Логирование доступа к данным
#     blockchain.log_data_access(accessing_user=admin_user, target_user=user1, key="contract")
#     print(f"\nДоступ к данным {user1.username} зафиксирован.")
#
#     # Проверка доступа к данным обычного пользователя (без прав)
#     access_granted = blockchain.check_access(user2, key="contract_active")
#     if not access_granted:
#         print(f"\nОшибка: У пользователя {user2.username} нет доступа к данным 'contract'.")
#
#     # Проверка доступа администратора к данным
#     access_granted_admin = blockchain.check_access(admin_user, key="contract")
#     print(f"\nДоступ администратора к данным: {access_granted_admin}")
#
#     # Майнинг блока
#     blockchain.mine_block("New block data")
#     print(f"\nПоследний блок:\n{blockchain.get_previous_block()}")
#
#     # Проверка целостности цепочки блоков
#     is_valid = blockchain.is_chain_valid()
#     print(f"\nЦелостность блокчейна: {is_valid}")
#
#     # Логирование и аудит безопасности
#     blockchain.log_security_event("Test security event")
#     blockchain.audit_chain()
#
# # Вызов функции для демонстрации работы блокчейна
# blockchain_demo()




