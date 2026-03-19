from pydantic import BaseModel


class LoginModel(BaseModel):
    phone: str
    password: str


class PasswordChangeModel(BaseModel):
    oldPassword: str
    newPassword: str
    confirmPassword: str
