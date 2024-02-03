from pydantic import BaseModel, SecretStr, EmailStr


class LoginRequest(BaseModel):
    email: str
    password: str


class SignupRequest(BaseModel):
    email: EmailStr
    password: SecretStr
