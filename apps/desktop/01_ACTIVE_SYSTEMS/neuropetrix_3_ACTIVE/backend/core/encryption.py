from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os
import secrets
from typing import Union, Dict, Any
import json

class EncryptionService:
    def __init__(self, password: str = None):
        """Initialize encryption service with password or generate new key."""
        if password:
            self.key = self._derive_key_from_password(password)
        else:
            # Generate a new key
            self.key = Fernet.generate_key()
        
        self.cipher = Fernet(self.key)
    
    def _derive_key_from_password(self, password: str, salt: bytes = None) -> bytes:
        """Derive encryption key from password using PBKDF2."""
        if salt is None:
            salt = os.urandom(16)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def encrypt_string(self, plaintext: str) -> str:
        """Encrypt a string and return base64 encoded result."""
        encrypted_data = self.cipher.encrypt(plaintext.encode())
        return base64.urlsafe_b64encode(encrypted_data).decode()
    
    def decrypt_string(self, encrypted_text: str) -> str:
        """Decrypt a base64 encoded string."""
        encrypted_data = base64.urlsafe_b64decode(encrypted_text.encode())
        decrypted_data = self.cipher.decrypt(encrypted_data)
        return decrypted_data.decode()
    
    def encrypt_dict(self, data: Dict[str, Any]) -> str:
        """Encrypt a dictionary by converting to JSON first."""
        json_data = json.dumps(data, ensure_ascii=False)
        return self.encrypt_string(json_data)
    
    def decrypt_dict(self, encrypted_data: str) -> Dict[str, Any]:
        """Decrypt data back to dictionary."""
        decrypted_json = self.decrypt_string(encrypted_data)
        return json.loads(decrypted_json)
    
    def encrypt_file(self, file_path: str, output_path: str = None) -> str:
        """Encrypt a file."""
        if output_path is None:
            output_path = file_path + ".encrypted"
        
        with open(file_path, 'rb') as file:
            file_data = file.read()
        
        encrypted_data = self.cipher.encrypt(file_data)
        
        with open(output_path, 'wb') as file:
            file.write(encrypted_data)
        
        return output_path
    
    def decrypt_file(self, encrypted_file_path: str, output_path: str = None) -> str:
        """Decrypt a file."""
        if output_path is None:
            output_path = encrypted_file_path.replace('.encrypted', '')
        
        with open(encrypted_file_path, 'rb') as file:
            encrypted_data = file.read()
        
        decrypted_data = self.cipher.decrypt(encrypted_data)
        
        with open(output_path, 'wb') as file:
            file.write(decrypted_data)
        
        return output_path
    
    def get_key(self) -> str:
        """Get the encryption key as base64 string."""
        return base64.urlsafe_b64encode(self.key).decode()

class DataProtection:
    """Data protection utilities for sensitive medical data."""
    
    def __init__(self):
        self.encryption_service = EncryptionService()
    
    def protect_patient_data(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Protect sensitive patient data."""
        sensitive_fields = [
            'name', 'surname', 'tc_no', 'phone', 'address', 
            'email', 'insurance_number', 'medical_history'
        ]
        
        protected_data = patient_data.copy()
        
        for field in sensitive_fields:
            if field in protected_data and protected_data[field]:
                protected_data[field] = self.encryption_service.encrypt_string(
                    str(protected_data[field])
                )
        
        return protected_data
    
    def unprotect_patient_data(self, protected_data: Dict[str, Any]) -> Dict[str, Any]:
        """Unprotect sensitive patient data."""
        sensitive_fields = [
            'name', 'surname', 'tc_no', 'phone', 'address', 
            'email', 'insurance_number', 'medical_history'
        ]
        
        unprotected_data = protected_data.copy()
        
        for field in sensitive_fields:
            if field in unprotected_data and unprotected_data[field]:
                try:
                    unprotected_data[field] = self.encryption_service.decrypt_string(
                        str(unprotected_data[field])
                    )
                except Exception:
                    # If decryption fails, keep original value
                    pass
        
        return unprotected_data
    
    def hash_sensitive_data(self, data: str) -> str:
        """Create a one-way hash of sensitive data."""
        import hashlib
        return hashlib.sha256(data.encode()).hexdigest()
    
    def anonymize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Anonymize data by replacing sensitive fields with hashes."""
        sensitive_fields = ['name', 'surname', 'tc_no', 'phone', 'email']
        anonymized_data = data.copy()
        
        for field in sensitive_fields:
            if field in anonymized_data and anonymized_data[field]:
                anonymized_data[field] = self.hash_sensitive_data(
                    str(anonymized_data[field])
                )
        
        return anonymized_data

class SecureStorage:
    """Secure storage for sensitive data."""
    
    def __init__(self, encryption_key: str = None):
        self.encryption_service = EncryptionService(encryption_key) if encryption_key else EncryptionService()
        self.storage_path = "secure_storage"
        os.makedirs(self.storage_path, exist_ok=True)
    
    def store_secure_data(self, key: str, data: Dict[str, Any]) -> str:
        """Store encrypted data."""
        encrypted_data = self.encryption_service.encrypt_dict(data)
        file_path = os.path.join(self.storage_path, f"{key}.enc")
        
        with open(file_path, 'w') as file:
            file.write(encrypted_data)
        
        return file_path
    
    def retrieve_secure_data(self, key: str) -> Dict[str, Any]:
        """Retrieve and decrypt data."""
        file_path = os.path.join(self.storage_path, f"{key}.enc")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Secure data not found for key: {key}")
        
        with open(file_path, 'r') as file:
            encrypted_data = file.read()
        
        return self.encryption_service.decrypt_dict(encrypted_data)
    
    def delete_secure_data(self, key: str) -> bool:
        """Delete secure data."""
        file_path = os.path.join(self.storage_path, f"{key}.enc")
        
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        
        return False

# Global instances
data_protection = DataProtection()
secure_storage = SecureStorage()

# Utility functions
def encrypt_sensitive_field(value: str) -> str:
    """Encrypt a single sensitive field."""
    return data_protection.encryption_service.encrypt_string(value)

def decrypt_sensitive_field(encrypted_value: str) -> str:
    """Decrypt a single sensitive field."""
    return data_protection.encryption_service.decrypt_string(encrypted_value)

def generate_secure_token(length: int = 32) -> str:
    """Generate a secure random token."""
    return secrets.token_urlsafe(length)

def mask_sensitive_data(data: str, visible_chars: int = 4) -> str:
    """Mask sensitive data showing only last few characters."""
    if len(data) <= visible_chars:
        return "*" * len(data)
    
    return "*" * (len(data) - visible_chars) + data[-visible_chars:]
