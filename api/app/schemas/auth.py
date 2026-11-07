from pydantic import BaseModel, EmailStr, Field

# E.164 format, e.g. +380501234567 or +48501234567
PHONE_PATTERN = r"^\+[1-9]\d{7,14}$"

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    first_name: str | None = None
    last_name: str | None = None
    phone_number: str | None = Field(default=None, pattern=PHONE_PATTERN)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    role: str
    status: str

    model_config = {
        "from_attributes": True,
    }
    
class MessageResponse(BaseModel):
    message: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)