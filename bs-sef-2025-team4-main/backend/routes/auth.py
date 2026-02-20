from datetime import timedelta
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from jose import JWTError, jwt
from passlib.context import CryptContext

from db import get_db
from models import User
# אנחנו משתמשים בסכמות המעודכנות שלך
from schemas import UserOut, RegisterIn, LoginOk, LoginIn, RoleUpdate

# --- הגדרות אבטחה (נמצאות כאן כדי למנוע תלות בקבצים חיצוניים) ---
SECRET_KEY = "YOUR_SUPER_SECRET_KEY"  # במציאות שים ב-.env
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 שעות

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

router = APIRouter(prefix="/auth", tags=["auth"])

ALLOWED_ROLES = {"STUDENT", "LECTURER", "ADMIN"}


def _normalize_role(role: str) -> str:
    return (role or "").strip().upper()


# --- פונקציות עזר לאבטחה ---
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict):
    to_encode = data.copy()
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# --- Dependencies ---
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user


def get_current_admin(current_user: User = Depends(get_current_user)):
    if _normalize_role(current_user.role) != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return current_user


# --- Routes ---

@router.post("/register", response_model=UserOut, status_code=201)
def register(payload: RegisterIn, db: Session = Depends(get_db)):
    email = payload.email.lower().strip()
    role = _normalize_role(payload.role) or "STUDENT"

    if role not in ALLOWED_ROLES:
        raise HTTPException(status_code=400, detail="ROLE לא חוקי")

    if len(payload.password) < 6:
        raise HTTPException(status_code=400, detail="סיסמה חייבת להיות לפחות 6 תווים")

    exists = db.query(User).filter(User.email == email).first()
    if exists:
        raise HTTPException(status_code=409, detail="האימייל כבר קיים במערכת")

    user = User(
        first_name=(payload.first_name.strip() if payload.first_name else None),
        last_name=(payload.last_name.strip() if payload.last_name else None),
        email=email,
        role=role,
        password_hash=get_password_hash(payload.password),  # שימוש בפונקציה הפנימית
    )

    try:
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="האימייל כבר קיים במערכת")
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"DB error: {str(e)}")


@router.post("/login", response_model=LoginOk)
def login(payload: LoginIn, db: Session = Depends(get_db)):
    email = payload.email.lower().strip()

    # חיפוש משתמש
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="שם משתמש או סיסמה שגויים")

    # יצירת טוקן
    access_token = create_access_token(data={"sub": str(user.id), "role": user.role})

    # ✅ החלק החשוב: החזרת המילואים בתגובה
    return LoginOk(
        id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        role=user.role,
        access_token=access_token,
        token_type="bearer",
        miluim_group_code=user.miluim_group_code  # הוספנו את זה!
    )


# --- ניהול משתמשים (Admin) ---

@router.get("/users", response_model=List[UserOut])
def get_all_users(
        db: Session = Depends(get_db),
        admin: User = Depends(get_current_admin)
):
    return db.query(User).all()


@router.patch("/users/{user_id}/role")
def update_user_role(
        user_id: str,
        role_data: RoleUpdate,
        admin: User = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    new_role = _normalize_role(role_data.role)
    if new_role not in ALLOWED_ROLES:
        raise HTTPException(status_code=400, detail="ROLE לא חוקי")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="משתמש לא נמצא")

    user.role = new_role
    db.commit()
    return {"message": f"התפקיד של {user.email} עודכן ל-{user.role} בהצלחה"}