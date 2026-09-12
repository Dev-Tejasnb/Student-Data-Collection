from fastapi import APIRouter, HTTPException, status, Body
from typing import List
from app.database import get_database
from app.models.student import StudentCreate, StudentResponse, StudentInDB
from app.schemas.response import SuccessResponse, ErrorResponse
from bson import ObjectId
from datetime import datetime, timezone


router = APIRouter(prefix="/api/students", tags=["Public Students"])


ADMISSION_METHODS = ["KCET", "NEET", "NUCAT", "MANAGEMENT"]


@router.post(
    "",
    response_model=SuccessResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit student details",
    description="Create a new student submission. No authentication required."
)
async def create_student(student_data: StudentCreate = Body(...)):
    if student_data.admission_through not in ADMISSION_METHODS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid admission method. Must be one of: {', '.join(ADMISSION_METHODS)}"
        )

    database = await get_database()

    student_dict = student_data.model_dump()
    now = datetime.now(timezone.utc)
    student_dict["created_at"] = now
    student_dict["updated_at"] = now

    result = await database.students.insert_one(student_dict)

    created_student = await database.students.find_one({"_id": result.inserted_id})
    created_student["id"] = str(created_student["_id"])
    del created_student["_id"]

    return SuccessResponse(
        message="Student details submitted successfully",
        data=StudentResponse(**created_student)
    )