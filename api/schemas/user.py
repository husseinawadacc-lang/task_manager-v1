from pydantic import BaseModel
from pydantic import EmailStr
from datetime import datetime
from core.enums.user_role import UserRole

class RegisterRequest(BaseModel):
    username: str 
    email: EmailStr
    password: str 
    role: UserRole= UserRole.USER  

class RegisterResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: UserRole
    is_active:bool
    created_at:datetime    

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: UserRole
    is_active:bool
    created_at:datetime

    class Config:
        from_attributes = True

class loginRequest(BaseModel):
    email: EmailStr
    password: str        

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str    