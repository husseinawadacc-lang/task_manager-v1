from pydantic import BaseModel



class TokenResponse(BaseModel):
    """
    البيانات اللي بترجع للـ frontend بعد login
    """
    access_token: str
    token_type: str = "bearer"
    refresh_token: str
