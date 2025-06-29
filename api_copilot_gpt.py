from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI()


# Pydantic model for User
class User(BaseModel):
    id: int
    name: str
    email: str


# In-memory storage for users
users = []


@app.post("/users/", response_model=User)
def add_user(user: User):
    # Check if user with the same ID already exists
    if any(u.id == user.id for u in users):
        raise HTTPException(status_code=400, detail="User with this ID already exists.")
    users.append(user)
    return user


@app.put("/users/{user_id}", response_model=User)
def update_user(user_id: int, updated_user: User):
    for index, user in enumerate(users):
        if user.id == user_id:
            users[index] = updated_user
            return updated_user
    raise HTTPException(status_code=404, detail="User not found.")


@app.get("/users/", response_model=List[User])
def list_users():
    return users
