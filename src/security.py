from cryptography.fernet import Fernet

class SecurityManager:

    def __init__(self):
        # Generate key (in real system store in .env)
        self.key = Fernet.generate_key()
        self.cipher = Fernet(self.key)

    def encrypt_encoding(self, encoding):
        # Convert to bytes
        encoding_bytes = encoding.tobytes()
        return self.cipher.encrypt(encoding_bytes)

    def decrypt_encoding(self, encrypted_data):
        return self.cipher.decrypt(encrypted_data)