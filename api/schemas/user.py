from pydantic import BaseModel
from pydantic import EmailStr
from datetime import datetime
from core.enums.user_role import UserRole

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str 

class RegisterResponse(BaseModel):
    id: int
    email: EmailStr
    
class UserResponse(BaseModel):
    id: int
    email: EmailStr
    role: UserRole
    is_active:bool
    created_at:datetime

    class Config:
        from_attributes = True # for orm/domin model compatibility

class loginRequest(BaseModel):
    email: EmailStr
    password: str        

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str  

class PasswordResetConfirmRequest(BaseModel):
    token:str
    password:str      

class PasswordResetRequest(BaseModel):
    email:EmailStr    