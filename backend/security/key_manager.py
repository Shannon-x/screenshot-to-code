import hashlib
import secrets
from typing import Dict, Optional
from datetime import datetime, timedelta
import json
import os
from cryptography.fernet import Fernet

class SecureKeyManager:
    """
    Manages API keys securely by storing them encrypted on the server side.
    This prevents exposing sensitive keys to the client.
    """
    
    def __init__(self, secret_key: Optional[str] = None):
        # Use provided secret key or generate one
        if secret_key:
            self.cipher = Fernet(secret_key.encode() if isinstance(secret_key, str) else secret_key)
        else:
            # In production, this should come from environment variable
            key = os.environ.get("ENCRYPTION_KEY")
            if not key:
                # Generate a new key for development
                key = Fernet.generate_key()
                print("WARNING: Using generated encryption key. Set ENCRYPTION_KEY env var in production!")
            self.cipher = Fernet(key if isinstance(key, bytes) else key.encode())
        
        # In-memory session storage (use Redis or similar in production)
        self.sessions: Dict[str, Dict] = {}
        
    def create_session(self, user_id: str = None) -> str:
        """Create a new session and return session token"""
        session_id = secrets.token_urlsafe(32)
        session_data = {
            "user_id": user_id or secrets.token_urlsafe(16),
            "created_at": datetime.now().isoformat(),
            "api_keys": {},
            "expires_at": (datetime.now() + timedelta(hours=24)).isoformat()
        }
        self.sessions[session_id] = session_data
        return session_id
    
    def store_api_key(self, session_id: str, key_name: str, api_key: str) -> bool:
        """Store an encrypted API key for a session"""
        if session_id not in self.sessions:
            return False
            
        # Check if session is expired
        session = self.sessions[session_id]
        if datetime.fromisoformat(session["expires_at"]) < datetime.now():
            del self.sessions[session_id]
            return False
            
        # Encrypt and store the API key
        encrypted_key = self.cipher.encrypt(api_key.encode()).decode()
        session["api_keys"][key_name] = encrypted_key
        return True
    
    def get_api_key(self, session_id: str, key_name: str) -> Optional[str]:
        """Retrieve and decrypt an API key for a session"""
        if session_id not in self.sessions:
            return None
            
        session = self.sessions[session_id]
        
        # Check if session is expired
        if datetime.fromisoformat(session["expires_at"]) < datetime.now():
            del self.sessions[session_id]
            return None
            
        encrypted_key = session["api_keys"].get(key_name)
        if not encrypted_key:
            return None
            
        # Decrypt and return the API key
        try:
            decrypted_key = self.cipher.decrypt(encrypted_key.encode()).decode()
            return decrypted_key
        except Exception:
            return None
    
    def validate_session(self, session_id: str) -> bool:
        """Check if a session is valid and not expired"""
        if session_id not in self.sessions:
            return False
            
        session = self.sessions[session_id]
        if datetime.fromisoformat(session["expires_at"]) < datetime.now():
            del self.sessions[session_id]
            return False
            
        return True
    
    def extend_session(self, session_id: str, hours: int = 24) -> bool:
        """Extend the expiration time of a session"""
        if session_id not in self.sessions:
            return False
            
        session = self.sessions[session_id]
        session["expires_at"] = (datetime.now() + timedelta(hours=hours)).isoformat()
        return True
    
    def cleanup_expired_sessions(self):
        """Remove all expired sessions"""
        expired = []
        for session_id, session in self.sessions.items():
            if datetime.fromisoformat(session["expires_at"]) < datetime.now():
                expired.append(session_id)
        
        for session_id in expired:
            del self.sessions[session_id]
    
    def hash_api_key_for_display(self, api_key: str) -> str:
        """Create a safe display version of an API key (first 8 chars + hash)"""
        if len(api_key) < 8:
            return "****"
        
        # Show first 8 characters and a hash of the rest
        visible_part = api_key[:8]
        hash_part = hashlib.sha256(api_key[8:].encode()).hexdigest()[:8]
        return f"{visible_part}...{hash_part}"


# Global instance (in production, use dependency injection)
key_manager = SecureKeyManager()