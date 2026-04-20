from cryptography.fernet import Fernet
import hashlib


class SecurityManager:
    """
    Handles encryption and decryption of sensitive data, such as facial encodings,
    using Fernet symmetric encryption.
    """

    def __init__(self):
        # Generate key (in real system store in .env)
        self.key = Fernet.generate_key()
        self.cipher = Fernet(self.key)

    def encrypt_encoding(self, encoding):
        """
        Encrypts a numpy array representing a facial encoding into bytes.
        """
        encoding_bytes = encoding.tobytes()
        return self.cipher.encrypt(encoding_bytes)

    def decrypt_encoding(self, encrypted_data):
        """
        Decrypts an encrypted byte string back into the raw encoding bytes.
        """
        return self.cipher.decrypt(encrypted_data)


class AuthManager:
    """
    Manages password hashing and verification using SHA-256.
    """

    def hash_password(self, password):
        """
        Converts a plaintext password into a SHA-256 hashed string.
        """
        return hashlib.sha256(password.encode()).hexdigest()

    def verify_password(self, input_password, stored_hash):
        """
        Verifies if an inputted plaintext password matches a stored hash.
        """
        return self.hash_password(input_password) == stored_hash


class RBACManager:
    """
    Role-Based Access Control (RBAC) manager to handle user authorization.
    """

    def is_admin(self, role):
        """
        Checks if a given role is an Admin.
        """
        return role == "Admin"

    def authorize(self, role, action):
        """
        Authorizes specific actions based on the user's role.
        Certain actions like 'register_user' or 'export_data' require Admin privileges.
        """
        admin_actions = ["register_user", "export_data"]

        if action in admin_actions:
            return role == "Admin"

        return True
