# User Service - Imports Auth Service creating a Circular Import Cycle!
from auth_service import authenticate_token

def get_user_profile(user_id: str):
    return {"id": user_id, "role": "admin"}

def verify_user_permissions(token: str):
    return authenticate_token(token)
