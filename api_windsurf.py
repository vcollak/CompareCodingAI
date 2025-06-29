from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime

app = FastAPI(
    title="User Management API",
    description="API for managing users with CRUD operations",
    version="1.0.0",
)


# Pydantic models for request/response validation
class UserBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=50, description="User's full name")
    email: str = Field(..., description="User's email address")
    active: bool = Field(default=True, description="Whether the user is active")


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="User's password")


class UserUpdate(BaseModel):
    name: Optional[str] = Field(
        None, min_length=2, max_length=50, description="User's full name"
    )
    email: Optional[str] = Field(None, description="User's email address")
    active: Optional[bool] = Field(None, description="Whether the user is active")
    password: Optional[str] = Field(None, min_length=8, description="User's password")


class User(UserBase):
    id: str = Field(..., description="Unique user identifier")
    created_at: datetime = Field(..., description="When the user was created")
    updated_at: datetime = Field(..., description="When the user was last updated")

    class Config:
        from_attributes = True


# In-memory database for users
users_db = {}


# Helper functions
def get_current_time():
    return datetime.now()


# API Routes
@app.get("/")
async def root():
    return {"message": "Welcome to the User Management API"}


@app.post("/users/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    # Check if email already exists
    for existing_user in users_db.values():
        if existing_user["email"] == user.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

    # Create new user
    user_id = str(uuid.uuid4())
    current_time = get_current_time()

    new_user = {
        "id": user_id,
        "name": user.name,
        "email": user.email,
        "active": user.active,
        "created_at": current_time,
        "updated_at": current_time,
        # Note: In a real app, we would hash the password before storing
    }

    users_db[user_id] = new_user
    return new_user


@app.get("/users/", response_model=List[User])
async def list_users():
    return list(users_db.values())


@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: str):
    if user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return users_db[user_id]


@app.put("/users/{user_id}", response_model=User)
async def update_user(user_id: str, user_update: UserUpdate):
    if user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Get existing user
    user_data = users_db[user_id]

    # Update fields if provided
    if user_update.name is not None:
        user_data["name"] = user_update.name
    if user_update.email is not None:
        # Check if new email already exists for another user
        for uid, existing_user in users_db.items():
            if uid != user_id and existing_user["email"] == user_update.email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered",
                )
        user_data["email"] = user_update.email
    if user_update.active is not None:
        user_data["active"] = user_update.active
    if user_update.password is not None:
        # In a real app, we would hash the password
        pass

    # Update the timestamp
    user_data["updated_at"] = get_current_time()

    return user_data


@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: str):
    if user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    del users_db[user_id]
    return None


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("35_api_windsurf:app", host="0.0.0.0", port=8000, reload=True)
