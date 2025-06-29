from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import uuid4, UUID

app = FastAPI(
    title="User Management API",
    description="API for managing users (add, update, list)",
    version="1.0.0",
)


# Pydantic models for request and response
class UserBase(BaseModel):
    name: str
    email: str
    age: Optional[int] = None
    is_active: bool = True


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    age: Optional[int] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    id: UUID

    class Config:
        schema_extra = {
            "example": {
                "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "name": "John Doe",
                "email": "john@example.com",
                "age": 30,
                "is_active": True,
            }
        }


# In-memory database
users_db = []


# API endpoints
@app.post("/users/", response_model=UserResponse, status_code=201)
async def create_user(user: UserCreate):
    """
    Create a new user with the provided details
    """
    user_id = uuid4()
    user_dict = user.dict()
    user_with_id = {**user_dict, "id": user_id}
    users_db.append(user_with_id)
    return user_with_id


@app.get("/users/", response_model=List[UserResponse])
async def list_users():
    """
    Get a list of all users
    """
    return users_db


@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: UUID):
    """
    Get a specific user by ID
    """
    for user in users_db:
        if user["id"] == user_id:
            return user
    raise HTTPException(status_code=404, detail="User not found")


@app.put("/users/{user_id}", response_model=UserResponse)
async def update_user(user_id: UUID, user_update: UserUpdate):
    """
    Update a specific user by ID
    """
    for index, user in enumerate(users_db):
        if user["id"] == user_id:
            update_data = user_update.dict(exclude_unset=True)
            users_db[index] = {**user, **update_data}
            return users_db[index]
    raise HTTPException(status_code=404, detail="User not found")


@app.delete("/users/{user_id}", status_code=204)
async def delete_user(user_id: UUID):
    """
    Delete a user by ID
    """
    for index, user in enumerate(users_db):
        if user["id"] == user_id:
            users_db.pop(index)
            return
    raise HTTPException(status_code=404, detail="User not found")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
