# Authentication Service - Tightly coupled with User Service
from user_service import get_user_profile, verify_user_permissions

def authenticate_token(token: str):
    if not token:
        return None
    return get_user_profile(user_id="user_123")
