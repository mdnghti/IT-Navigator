from pydantic import BaseModel, ConfigDict, EmailStr


class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr
    full_name: str | None = None


class UserCreate(UserBase):
    """Schema for user registration."""

    password: str


class UserRead(UserBase):
    """Schema for user response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    is_admin: bool


class UserInDB(UserBase):
    """Schema for user in database."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    hashed_password: str
    is_active: bool
    is_admin: bool


class Token(BaseModel):
    """Token response schema."""

    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Token payload schema."""

    sub: str | None = None
