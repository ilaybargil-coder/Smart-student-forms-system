from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from db import get_db
from models import User
from schemas import LoginIn, LoginOk

router = APIRouter(prefix="/auth", tags=["auth"])
pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/login", response_model=LoginOk)
def login(payload: LoginIn, db: Session = Depends(get_db)):
    email = payload.email.lower().strip()
    role = payload.role.strip().upper()

    # מחפשים משתמש לפי אימייל
    user = db.query(User).filter(User.email == email).first()

    # הודעת שגיאה אחידה (לא מסגירה מה לא נכון)
    bad = HTTPException(status_code=401, detail="שם משתמש וסיסמא שגויים")

    if not user:
        raise bad

    # בודקים סיסמה
    if not pwd.verify(payload.password, user.password_hash):
        raise bad

    # בודקים ROLE תואם
    if user.role.upper() != role:
        raise bad

    return user