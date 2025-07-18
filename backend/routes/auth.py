from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from typing import Optional, Dict
from security.key_manager import key_manager

router = APIRouter(prefix="/api/auth", tags=["authentication"])

class SessionResponse(BaseModel):
    session_id: str
    message: str

class ApiKeyRequest(BaseModel):
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    replicate_api_key: Optional[str] = None

class ApiKeyResponse(BaseModel):
    stored_keys: Dict[str, str]  # key name -> masked version
    message: str

@router.post("/session", response_model=SessionResponse)
async def create_session():
    """Create a new secure session for API key storage"""
    session_id = key_manager.create_session()
    return SessionResponse(
        session_id=session_id,
        message="Session created successfully. Use this session ID for all API requests."
    )

@router.post("/keys", response_model=ApiKeyResponse)
async def store_api_keys(
    keys: ApiKeyRequest,
    session_id: str = Header(..., alias="X-Session-ID")
):
    """Store API keys securely on the server"""
    if not key_manager.validate_session(session_id):
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    
    stored_keys = {}
    
    # Store each provided API key
    if keys.openai_api_key:
        if key_manager.store_api_key(session_id, "openai", keys.openai_api_key):
            stored_keys["openai"] = key_manager.hash_api_key_for_display(keys.openai_api_key)
    
    if keys.anthropic_api_key:
        if key_manager.store_api_key(session_id, "anthropic", keys.anthropic_api_key):
            stored_keys["anthropic"] = key_manager.hash_api_key_for_display(keys.anthropic_api_key)
    
    if keys.gemini_api_key:
        if key_manager.store_api_key(session_id, "gemini", keys.gemini_api_key):
            stored_keys["gemini"] = key_manager.hash_api_key_for_display(keys.gemini_api_key)
    
    if keys.replicate_api_key:
        if key_manager.store_api_key(session_id, "replicate", keys.replicate_api_key):
            stored_keys["replicate"] = key_manager.hash_api_key_for_display(keys.replicate_api_key)
    
    return ApiKeyResponse(
        stored_keys=stored_keys,
        message="API keys stored securely on server"
    )

@router.get("/keys", response_model=ApiKeyResponse)
async def get_stored_keys(session_id: str = Header(..., alias="X-Session-ID")):
    """Get list of stored API keys (masked for security)"""
    if not key_manager.validate_session(session_id):
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    
    stored_keys = {}
    
    # Check which keys are stored
    for key_name in ["openai", "anthropic", "gemini", "replicate"]:
        api_key = key_manager.get_api_key(session_id, key_name)
        if api_key:
            stored_keys[key_name] = key_manager.hash_api_key_for_display(api_key)
    
    return ApiKeyResponse(
        stored_keys=stored_keys,
        message="Stored API keys retrieved"
    )

@router.post("/session/extend")
async def extend_session(session_id: str = Header(..., alias="X-Session-ID")):
    """Extend the expiration time of a session"""
    if not key_manager.extend_session(session_id):
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    
    return {"message": "Session extended successfully"}

@router.delete("/session")
async def delete_session(session_id: str = Header(..., alias="X-Session-ID")):
    """Delete a session and all associated API keys"""
    if session_id in key_manager.sessions:
        del key_manager.sessions[session_id]
        return {"message": "Session deleted successfully"}
    
    raise HTTPException(status_code=404, detail="Session not found")