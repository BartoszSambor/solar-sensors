from typing import Literal

from pydantic import Field

from ..schemas import CamelModel


class LoginRequest(CamelModel):
    username: str
    password: str


class LoginResponse(CamelModel):
    access_token: str
    token_type: Literal["Bearer"] = "Bearer"
    expires_in: int = Field(description="Access token lifetime in seconds")


class PasswordChangeRequest(CamelModel):
    current_password: str
    new_password: str = Field(min_length=8)
