from fastapi import HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from cryptography.fernet import Fernet

from config import configs

# Define API key header
api_key_header = APIKeyHeader(name="X-API-Key")

# Dependency to check API key
def get_api_key(api_key: str = Security(api_key_header)):
    if api_key not in configs.fastapi_keys:
        raise HTTPException(status_code=403, detail="Could not validate credentials")
    return api_key

# Generate a key for encryption and decryption
# Note: In a real application, store this key securely and do not hardcode it
def encrypt_data(data: str) -> str:
    """Encrypt data using Fernet symmetric encryption."""
    encrypted_data = cipher_suite.encrypt(data.encode())
    return encrypted_data.decode()

def decrypt_data(encrypted_data: str) -> str:
    """Decrypt data using Fernet symmetric encryption."""
    decrypted_data = cipher_suite.decrypt(encrypted_data.encode())
    return decrypted_data.decode()

def __generate_encryption_key() -> bytes:
    """Generate a new encryption key."""
    return Fernet.generate_key()

def __get_cipher_suite() -> Fernet:
    """Get the Fernet cipher suite."""
    if not configs.auth_encryption_key:
        raise ValueError("Encryption key not found in configuration.")
    return Fernet(configs.auth_encryption_key.encode())

cipher_suite = __get_cipher_suite()
