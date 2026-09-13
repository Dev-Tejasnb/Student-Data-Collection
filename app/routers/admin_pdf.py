from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, status, Depends, Query
from fastapi.responses import StreamingResponse
from typing import Optional
from app.database import get_database
from app.services.pdf_service import generate_all_students_pdf, generate_student_pdf
from app.dependencies import require_staff_or_admin
from app.models.student import BATCH_VALUES
from bson import ObjectId
import io


BATCH_VALUES_LIST = ["FTB", "Batch - 1", "Batch - 2", "Batch - 3"]


router = APIRouter(prefix="/api/admin/students", tags=["Admin Students"])


@router.get(
    "/export/pdf",
    summary="Export all students as PDF",
    description="Generate and download PDF with all student records. Staff or admin access required."
)
async def export_all_students_pdf(
    search: Optional[str] = Query(None, description="Search filter"),
    admission_through: Optional[str] = Query(None, description="Admission method filter"),
    batch: Optional[str] = Query(None, description="Batch filter"),
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

    if admission_through and admission_through in ["KCET", "NEET", "NUCAT", "MANAGEMENT"]:
        query["admission_through"] = admission_through

    if batch and batch in BATCH_VALUES_LIST:
        query["batch"] = batch

    students = []
    async for student_doc in database.students.find(query).sort("created_at", 1):
        student_doc["id"] = str(student_doc["_id"])
        del student_doc["_id"]
        students.append(student_doc)

    pdf_bytes = generate_all_students_pdf(students)

    # Determine filename based on filters
    filename_parts = ["student_records"]
    if batch:
        filename_parts.append(batch.replace(" ", "_").replace("-", "_"))
    elif search:
        filename_parts.append("search")
    if admission_through:
        filename_parts.append(admission_through)
    filename_parts.append(datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S'))
    filename = "_".join(filename_parts) + ".pdf"

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


@router.get(
    "/{student_id}/pdf",
    summary="Export individual student as PDF",
    description="Generate and download PDF for a single student. Staff or admin access required."
)
async def export_student_pdf(
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

    pdf_bytes = generate_student_pdf(student_doc)

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=student_{student_doc['name'].replace(' ', '_')}_{datetime.now(timezone.utc).strftime('%Y%m%d')}.pdf"
        }
    )