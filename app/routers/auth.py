from fastapi import APIRouter, HTTPException, status, Depends, Body, Form, Request
from fastapi.security import OAuth2PasswordRequestForm
from app.database import get_database
from app.auth.security import verify_password, get_password_hash, create_access_token
from app.schemas.auth import LoginRequest, Token
from app.models.user import UserInDB, UserCreate, UserResponse
from app.schemas.response import SuccessResponse, ErrorResponse
from app.dependencies import require_admin
from bson import ObjectId
from datetime import datetime, timezone
from typing import Optional, Dict, Any
import json


router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post(
    "/login",
    response_model=Token,
    summary="User login",
    description="Authenticate user and return JWT access token. Uses OAuth2 Password flow for Swagger compatibility."
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends()
):
    username = form_data.username
    password = form_data.password
    
    if not username or not password:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid credentials format. Provide username and password as form data."
        )
    
    database = await get_database()
    
    user_doc = await database.users.find_one({"username": username})
    if not user_doc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not verify_password(password, user_doc["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user_doc.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is disabled",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user_doc["username"]})
    
    return Token(access_token=access_token, token_type="bearer")


@router.post(
    "/users",
    response_model=SuccessResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new user (admin only)",
    description="Create a new admin or staff account. Admin access required."
)
async def create_user(
    user_data: UserCreate = Body(...),
    current_user: UserInDB = Depends(require_admin)
):
    database = await get_database()

    existing_user = await database.users.find_one({"username": user_data.username})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )

    user_dict = user_data.model_dump()
    user_dict["password_hash"] = get_password_hash(user_data.password)
    del user_dict["password"]
    user_dict["created_at"] = datetime.now(timezone.utc)

    result = await database.users.insert_one(user_dict)

    created_user = await database.users.find_one({"_id": result.inserted_id})
    created_user["id"] = str(created_user["_id"])
    del created_user["_id"]
    del created_user["password_hash"]

    return SuccessResponse(
        message="User created successfully",
        data=UserResponse(**created_user)
    )


@router.get(
    "/users",
    response_model=SuccessResponse,
    summary="List all users (admin only)",
    description="Get list of all users. Admin access required."
)
async def list_users(current_user: UserInDB = Depends(require_admin)):
    database = await get_database()
    
    users = []
    async for user_doc in database.users.find():
        user_doc["id"] = str(user_doc["_id"])
        del user_doc["_id"]
        del user_doc["password_hash"]
        users.append(UserResponse(**user_doc))
    
    return SuccessResponse(
        message="Users retrieved successfully",
        data={"users": users, "total": len(users)}
    )


@router.put(
    "/users/{user_id}",
    response_model=SuccessResponse,
    summary="Update user (admin only)",
    description="Update user details. Admin access required."
)
async def update_user(
    user_id: str,
    user_data: UserCreate = Body(...),
    current_user: UserInDB = Depends(require_admin)
):
    if not ObjectId.is_valid(user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID"
        )
    
    database = await get_database()
    
    existing_user = await database.users.find_one({"_id": ObjectId(user_id)})
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if existing_user["username"] == current_user.username and user_data.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change your own admin role"
        )
    
    update_dict = {}
    if user_data.username != existing_user["username"]:
        username_check = await database.users.find_one({"username": user_data.username})
        if username_check:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
        update_dict["username"] = user_data.username
    
    if user_data.role != existing_user.get("role", "staff"):
        update_dict["role"] = user_data.role

    if user_data.is_active != existing_user.get("is_active", True):
        update_dict["is_active"] = user_data.is_active

    if user_data.password:
        update_dict["password_hash"] = get_password_hash(user_data.password)

    if update_dict:
        await database.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_dict}
        )

    updated_user = await database.users.find_one({"_id": ObjectId(user_id)})
    updated_user["id"] = str(updated_user["_id"])
    del updated_user["_id"]
    del updated_user["password_hash"]

    return SuccessResponse(
        message="User updated successfully",
        data=UserResponse(**updated_user)
    )


@router.delete(
    "/users/{user_id}",
    response_model=SuccessResponse,
    summary="Delete user (admin only)",
    description="Delete a user account. Admin access required. Cannot delete yourself or the last admin."
)
async def delete_user(
    user_id: str,
    current_user: UserInDB = Depends(require_admin)
):
    if not ObjectId.is_valid(user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID"
        )
    
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    database = await get_database()
    
    user_to_delete = await database.users.find_one({"_id": ObjectId(user_id)})
    if not user_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user_to_delete.get("role") == "admin":
        admin_count = await database.users.count_documents({"role": "admin", "is_active": True})
        if admin_count <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete the last active admin account"
            )
    
    await database.users.delete_one({"_id": ObjectId(user_id)})
    
    return SuccessResponse(
        message="User deleted successfully"
    )