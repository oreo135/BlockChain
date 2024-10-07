import datetime as _dt
import hashlib as _hashlib
import json as _json
from models import User, Role
from cryptography.fernet import Fernet


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
            if block["type"] == "vote" and block["issue"] == issue:
                return block["votes"]
        return {}

    def close_vote(self, issue: str):
        # Находим блок с голосованием и помечаем его как закрытое
        for block in reversed(self.chain):
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
        return key in user.data

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

