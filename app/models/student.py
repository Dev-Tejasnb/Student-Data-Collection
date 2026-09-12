from datetime import datetime, timezone
from typing import Optional, Annotated
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


class StudentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    course: str = Field(..., min_length=1, max_length=100)
    college: str = Field(..., min_length=1, max_length=200)
    admission_through: str = Field(..., pattern="^(KCET|NEET|NUCAT|MANAGEMENT)$")


class StudentCreate(StudentBase):
    pass


class StudentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    course: Optional[str] = Field(None, min_length=1, max_length=100)
    college: Optional[str] = Field(None, min_length=1, max_length=200)
    admission_through: Optional[str] = Field(None, pattern="^(KCET|NEET|NUCAT|MANAGEMENT)$")


class StudentInDB(StudentBase):
    id: PyObjectId = Field(default_factory=ObjectId)
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )


class StudentResponse(StudentBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StudentListResponse(BaseModel):
    students: list[StudentResponse]
    page: int
    limit: int
    total: int
    pages: int