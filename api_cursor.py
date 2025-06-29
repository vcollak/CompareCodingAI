#!/usr/bin/env python3
"""
FastAPI application for managing users with CRUD operations
using Pydantic for data validation.
"""

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
import uuid

# Initialize FastAPI app
app = FastAPI(
    title="User Management API",
    description="A simple API to manage users with FastAPI and Pydantic",
    version="1.0.0",
)

# In-memory database for users
users_db = {}


# Pydantic models for data validation
class UserBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=50, description="User's full name")
    email: str = Field(..., description="User's email address")
    age: Optional[int] = Field(None, ge=0, description="User's age")
    is_active: bool = Field(default=True, description="Whether the user is active")


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="User's password")


class UserUpdate(BaseModel):
    name: Optional[str] = Field(
        None, min_length=2, max_length=50, description="User's full name"
    )
    email: Optional[str] = Field(None, description="User's email address")
    age: Optional[int] = Field(None, ge=0, description="User's age")
    is_active: Optional[bool] = Field(None, description="Whether the user is active")
    password: Optional[str] = Field(None, min_length=8, description="User's password")


class UserResponse(UserBase):
    id: str = Field(..., description="User's unique identifier")

    class Config:
        schema_extra = {
            "example": {
                "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
                "name": "John Doe",
                "email": "john.doe@example.com",
                "age": 30,
                "is_active": True,
            }
        }


# API endpoints
@app.get("/", tags=["Root"])
async def root():
    return {"message": "Welcome to the User Management API"}


@app.post(
    "/users/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Users"],
)
async def create_user(user: UserCreate):
    """
    Create a new user with the provided user information.
    """
    user_id = str(uuid.uuid4())
    user_data = user.dict()

    # Store user in database
    users_db[user_id] = user_data

    # Return user with id (without password)
    return {**user_data, "id": user_id, "password": None}


@app.get("/users/", response_model=List[UserResponse], tags=["Users"])
async def list_users():
    """
    Retrieve a list of all users.
    """
    return [
        {"id": user_id, **user_data, "password": None}
        for user_id, user_data in users_db.items()
    ]


@app.get("/users/{user_id}", response_model=UserResponse, tags=["Users"])
async def get_user(user_id: str):
    """
    Retrieve a specific user by id.
    """
    if user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found",
        )

    user_data = users_db[user_id]
    return {"id": user_id, **user_data, "password": None}


@app.put("/users/{user_id}", response_model=UserResponse, tags=["Users"])
async def update_user(user_id: str, user_update: UserUpdate):
    """
    Update a user's information.
    """
    if user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found",
        )

    stored_user = users_db[user_id]

    # Only update fields that were provided
    update_data = user_update.dict(exclude_unset=True)
    updated_user = {**stored_user, **update_data}
    users_db[user_id] = updated_user

    return {"id": user_id, **updated_user, "password": None}


@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Users"])
async def delete_user(user_id: str):
    """
    Delete a user.
    """
    if user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found",
        )

    # Remove user from database
    del users_db[user_id]

    return None


# Run this application with: uvicorn 35_api:app --reload
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("35_api:app", host="0.0.0.0", port=8000, reload=True)
