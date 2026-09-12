from datetime import datetime, timezone
from typing import Optional, Literal, Annotated
from pydantic import BaseModel, Field, ConfigDict, BeforeValidator
from bson import ObjectId


def validate_object_id(v: str | ObjectId) -> ObjectId:
    if isinstance(v, ObjectId):
        return v
    if not ObjectId.is_valid(v):
        raise ValueError("Invalid ObjectId")
    return ObjectId(v)


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


PyObjectId = Annotated[
    ObjectId,
    BeforeValidator(validate_object_id),
    Field(alias="_id")
]


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    role: Literal["admin", "staff"] = "staff"
    is_active: bool = True


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=100)


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    role: Optional[Literal["admin", "staff"]] = None
    is_active: Optional[bool] = None
    password: Optional[str] = Field(None, min_length=6, max_length=100)


class UserInDB(UserBase):
    id: PyObjectId = Field(default_factory=ObjectId)
    password_hash: str
    created_at: datetime = Field(default_factory=utcnow)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )


class UserResponse(UserBase):
    id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserListResponse(BaseModel):
    users: list[UserResponse]
    total: int