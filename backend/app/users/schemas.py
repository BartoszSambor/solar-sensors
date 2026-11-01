import re
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

RESERVED_USERNAMES = {"abuse", "postmaster"}


def validate_username(username: str) -> str:
    """Validate username according to Google Workspace guidelines."""
    username = username.lower()
    if not username:
        raise ValueError("Username cannot be empty")
    if len(username) > 64:
        raise ValueError("Username cannot exceed 64 characters")
    if username in RESERVED_USERNAMES:
        raise ValueError(f"Username '{username}' is a reserved word and cannot be used")
    if not re.match(r"^[a-z0-9\-_'.]+$", username):
        raise ValueError(
            "Username can only contain letters (a-z), numbers (0-9),"
            " dashes (-), underscores (_), apostrophes ('), and periods (.)"
        )
    if ".." in username:
        raise ValueError("Username cannot contain consecutive periods")
    if username.startswith("."):
        raise ValueError("Username cannot start with a period")
    if username.endswith("."):
        raise ValueError("Username cannot end with a period")
    return username


class UserBase(BaseModel):
    username: str = Field(..., min_length=1, max_length=64)

    @field_validator("username")
    @classmethod
    def validate_username_field(cls, v: str) -> str:
        return validate_username(v)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserRead(UserBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserFilter(BaseModel):
    username: str | None = None
    created_at_from: datetime | None = None
    created_at_to: datetime | None = None


class UserSort(BaseModel):
    field: str = "id"
    direction: str = "asc"


class UserListResponse(BaseModel):
    users: list[UserRead]
    total: int
    skip: int
    limit: int
