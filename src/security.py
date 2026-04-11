from cryptography.fernet import Fernet
import hashlib


class SecurityManager:

    def __init__(self):
        # Generate key (in real system store in .env)
        self.key = Fernet.generate_key()
        self.cipher = Fernet(self.key)

    def encrypt_encoding(self, encoding):
        encoding_bytes = encoding.tobytes()
        return self.cipher.encrypt(encoding_bytes)

    def decrypt_encoding(self, encrypted_data):
        return self.cipher.decrypt(encrypted_data)


class AuthManager:

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def verify_password(self, input_password, stored_hash):
        return self.hash_password(input_password) == stored_hash