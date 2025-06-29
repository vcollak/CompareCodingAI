# 35_api_gemini.py

from typing import List, Optional
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
import uuid

app = FastAPI()

# --- Data Models (Pydantic) ---


class UserCreate(BaseModel):
    """Model for creating a new user."""

    first_name: str = Field(..., example="John", description="User's first name")
    last_name: str = Field(..., example="Doe", description="User's last name")
    email: str = Field(
        ..., example="john.doe@example.com", description="User's email address"
    )


class UserUpdate(BaseModel):
    """Model for updating an existing user."""

    first_name: Optional[str] = Field(
        None, example="Jane", description="User's first name"
    )
    last_name: Optional[str] = Field(
        None, example="Smith", description="User's last name"
    )
    email: Optional[str] = Field(
        None, example="jane.smith@example.com", description="User's email address"
    )


class User(BaseModel):
    """Model for representing a user (including ID)."""

    id: str = Field(
        ...,
        example="a1b2c3d4-e5f6-7890-1234-567890abcdef",
        description="Unique user ID",
    )
    first_name: str = Field(..., example="John", description="User's first name")
    last_name: str = Field(..., example="Doe", description="User's last name")
    email: str = Field(
        ..., example="john.doe@example.com", description="User's email address"
    )


# --- Data Storage (In-Memory - Replace with a database in production) ---

users_db: dict[str, User] = {}


# --- API Endpoints ---


@app.post("/users/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user_create: UserCreate):
    """Creates a new user."""
    user_id = str(uuid.uuid4())
    new_user = User(id=user_id, **user_create.model_dump())
    users_db[user_id] = new_user
    return new_user


@app.get("/users/", response_model=List[User])
async def list_users():
    """Lists all users."""
    return list(users_db.values())


@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: str):
    """Retrieves a user by ID."""
    if user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return users_db[user_id]


@app.put("/users/{user_id}", response_model=User)
async def update_user(user_id: str, user_update: UserUpdate):
    """Updates an existing user."""
    if user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    existing_user = users_db[user_id]
    updated_data = user_update.model_dump(exclude_unset=True)
    updated_user = existing_user.model_copy(update=updated_data)
    users_db[user_id] = updated_user
    return updated_user


@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: str):
    """Deletes a user by ID"""
    if user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    del users_db[user_id]
    return
