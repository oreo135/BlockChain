from cryptography.fernet import Fernet


# Генерация ключа шифрования
def generate_key():
    return Fernet.generate_key()

# Создание объекта шифрования с использованием ключа
def create_cipher(key: bytes):
    return Fernet(key)

# Шифрование данных
def encrypt_data(cipher: Fernet, data: str) -> str:
    return cipher.encrypt(data.encode()).decode()

# Дешифрование данных
def decrypt_data(cipher: Fernet, encrypted_data: str) -> str:
    return cipher.decrypt(encrypted_data.encode()).decode()
