from fastapi import APIRouter, Depends
import asyncpg

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/")
async def get_users(db=Depends(lambda: None)):  # db will be injected via dependency in main.py
    # Note: Adjust to use the actual db connection from main.py's get_db
    # For now, placeholder; in practice, pass db as param and query
    return {"users": ["user1", "user2"]}

@router.get("/{user_id}")
async def get_user(user_id: int, db: asyncpg.Connection = Depends(lambda: None)):
    # Example raw query; adjust based on your schema
    row = await db.fetchrow("SELECT id, name FROM users WHERE id = $1", user_id)
    if row:
        return {"user_id": row["id"], "name": row["name"]}
    return {"error": "User not found"}
