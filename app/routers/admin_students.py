from fastapi import APIRouter, HTTPException, status, Query, Depends
from typing import Optional, List
from app.database import get_database
from app.models.student import StudentResponse, StudentUpdate, StudentListResponse, StudentInDB, BATCH_VALUES
from app.schemas.response import SuccessResponse
from app.dependencies import require_staff_or_admin, require_admin
from bson import ObjectId
from datetime import datetime, timezone
import math


router = APIRouter(prefix="/api/admin/students", tags=["Admin Students"])


BATCH_VALUES_LIST = ["FTB", "Batch - 1", "Batch - 2", "Batch - 3"]
ADMISSION_METHODS = ["KCET", "NEET", "NUCAT", "MANAGEMENT"]


@router.get(
    "",
    response_model=SuccessResponse,
    summary="List students with pagination, search, and filter",
    description="Get paginated list of students with optional search and filter. Staff or admin access required."
)
async def list_students(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search by name, course, or college"),
    admission_through: Optional[str] = Query(None, description="Filter by admission method"),
    batch: Optional[str] = Query(None, description="Filter by batch"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: int = Query(1, description="Sort order: 1 for ascending, -1 for descending"),
    current_user = Depends(require_staff_or_admin)
):
    database = await get_database()
    
    query = {}
    
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"course": {"$regex": search, "$options": "i"}},
            {"college": {"$regex": search, "$options": "i"}}
        ]
    
    if admission_through and admission_through in ADMISSION_METHODS:
        query["admission_through"] = admission_through
    
    if batch and batch in BATCH_VALUES_LIST:
        query["batch"] = batch
    
    total = await database.students.count_documents(query)
    pages = math.ceil(total / limit) if total > 0 else 1
    
    skip = (page - 1) * limit
    
    cursor = database.students.find(query).sort(sort_by, sort_order).skip(skip).limit(limit)
    
    students = []
    async for student_doc in cursor:
        student_doc["id"] = str(student_doc["_id"])
        del student_doc["_id"]
        students.append(StudentResponse(**student_doc))
    
    return SuccessResponse(
        message="Students retrieved successfully",
        data={
            "students": students,
            "page": page,
            "limit": limit,
            "total": total,
            "pages": pages
        }
    )


@router.get(
    "/stats",
    response_model=SuccessResponse,
    summary="Get student statistics",
    description="Get statistics for dashboard. Staff or admin access required."
)
async def get_student_stats(current_user = Depends(require_staff_or_admin)):
    database = await get_database()
    
    total = await database.students.count_documents({})
    
    pipeline = [
        {"$group": {"_id": "$admission_through", "count": {"$sum": 1}}}
    ]
    
    admission_stats = {}
    cursor = await database.students.aggregate(pipeline)
    async for doc in cursor:
        admission_stats[doc["_id"]] = doc["count"]
    
    batch_pipeline = [
        {"$group": {"_id": "$batch", "count": {"$sum": 1}}}
    ]
    
    batch_stats = {}
    cursor = await database.students.aggregate(batch_pipeline)
    async for doc in cursor:
        if doc["_id"]:
            batch_stats[doc["_id"]] = doc["count"]
    
    stats = {
        "total": total,
        "kcet": admission_stats.get("KCET", 0),
        "neet": admission_stats.get("NEET", 0),
        "nucat": admission_stats.get("NUCAT", 0),
        "management": admission_stats.get("MANAGEMENT", 0),
        "ftb": batch_stats.get("FTB", 0),
        "batch_1": batch_stats.get("Batch - 1", 0),
        "batch_2": batch_stats.get("Batch - 2", 0),
        "batch_3": batch_stats.get("Batch - 3", 0)
    }
    
    return SuccessResponse(
        message="Statistics retrieved successfully",
        data=stats
    )


@router.get(
    "/{student_id}",
    response_model=SuccessResponse,
    summary="Get student by ID",
    description="Get detailed student information. Staff or admin access required."
)
async def get_student(
    student_id: str,
    current_user = Depends(require_staff_or_admin)
):
    if not ObjectId.is_valid(student_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid student ID"
        )
    
    database = await get_database()
    
    student_doc = await database.students.find_one({"_id": ObjectId(student_id)})
    if not student_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    student_doc["id"] = str(student_doc["_id"])
    del student_doc["_id"]

    return SuccessResponse(
        message="Student retrieved successfully",
        data=StudentResponse(**student_doc)
    )


@router.put(
    "/{student_id}",
    response_model=SuccessResponse,
    summary="Update student",
    description="Update student details. Staff or admin access required."
)
async def update_student(
    student_id: str,
    student_data: StudentUpdate,
    current_user = Depends(require_staff_or_admin)
):
    if not ObjectId.is_valid(student_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid student ID"
        )
    
    database = await get_database()
    
    student_doc = await database.students.find_one({"_id": ObjectId(student_id)})
    if not student_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    update_dict = student_data.model_dump(exclude_unset=True)
    if not update_dict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )
    
    if "admission_through" in update_dict and update_dict["admission_through"] not in ADMISSION_METHODS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid admission method. Must be one of: {', '.join(ADMISSION_METHODS)}"
        )
    
    if "batch" in update_dict and update_dict["batch"] not in BATCH_VALUES_LIST:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid batch. Must be one of: {', '.join(BATCH_VALUES_LIST)}"
        )
    
    update_dict["updated_at"] = datetime.now(timezone.utc)
    
    await database.students.update_one(
        {"_id": ObjectId(student_id)},
        {"$set": update_dict}
    )
    
    updated_student = await database.students.find_one({"_id": ObjectId(student_id)})
    updated_student["id"] = str(updated_student["_id"])
    del updated_student["_id"]
    
    return SuccessResponse(
        message="Student updated successfully",
        data=StudentResponse(**updated_student)
    )


@router.delete(
    "/{student_id}",
    response_model=SuccessResponse,
    summary="Delete student",
    description="Delete a student record. Admin access required."
)
async def delete_student(
    student_id: str,
    current_user = Depends(require_admin)
):
    if not ObjectId.is_valid(student_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid student ID"
        )
    
    database = await get_database()
    
    student_doc = await database.students.find_one({"_id": ObjectId(student_id)})
    if not student_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    await database.students.delete_one({"_id": ObjectId(student_id)})
    
    return SuccessResponse(
        message="Student deleted successfully"
    )