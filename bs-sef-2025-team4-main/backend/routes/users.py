from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db import get_db
from models import User
from schemas import UserOut
from routes.auth import get_current_user

# מגדירים ראוטר חדש שמתחיל ב-/users
router = APIRouter(prefix="/users", tags=["users"])

# הנה הפונקציה שהייתה חסרה!
@router.get("/me", response_model=UserOut)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user