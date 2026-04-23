import os
from fastapi import HTTPException , Request

SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")

def get_current_user(request: Request):
    user = request.state.user
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return user