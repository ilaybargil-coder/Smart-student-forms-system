from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict, Field, field_validator


# --- Auth / Users ---
class RegisterIn(BaseModel):
    email: EmailStr
    password: str
    role: str = "STUDENT"
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class LoginOk(BaseModel):
    id: UUID
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: EmailStr
    role: str
    access_token: str
    token_type: str = "bearer"
    # ✅ חדש: המתווה חוזר בלוגין
    miluim_group_code: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class RoleUpdate(BaseModel):
    role: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    email: EmailStr
    role: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    # ✅ חדש
    miluim_group_code: Optional[str] = None


# --- Courses ---
class CourseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    code: Optional[str] = None
    name_he: Optional[str] = None


class EnrollRequest(BaseModel):
    student_id: UUID
    course_id: UUID


class AssignLecturerRequest(BaseModel):
    lecturer_id: UUID
    course_id: UUID


# --- Requests ---
class RequestTypeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    code: str
    name_he: str
    route_policy: str
    is_active: bool
    default_lecturer_id: Optional[UUID] = None


class FileSchema(BaseModel):
    name: str
    size: int
    type: str
    url: Optional[str] = None


class RequestCreate(BaseModel):
    request_type: str
    course_id: Optional[UUID] = None
    lecturer_id: Optional[UUID] = None
    student_national_id: Optional[str] = None
    request_description: Optional[str] = None
    files: List[FileSchema] = []

    @field_validator('student_national_id')
    @classmethod
    def validate_id(cls, v):
        if v and (len(v) != 9 or not v.isdigit()):
            raise ValueError('תעודת זהות חייבת להכיל בדיוק 9 ספרות')
        return v


class RequestStatusUpdate(BaseModel):
    status: str
    lecturer_note: Optional[str] = None


class RequestOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    student_id: UUID
    status: str
    created_at: datetime
    request_type: str
    request_description: Optional[str] = None
    lecturer_note: Optional[str] = None
    course_id: Optional[UUID] = None
    files: List[Dict[str, Any]] = []


class RequestRowOut(RequestOut):
    student_name: Optional[str] = None
    course_name: Optional[str] = None
    lecturer_name: Optional[str] = None
    student_national_id: Optional[str] = None
    # ✅ חדש: המרצה יראה את המתווה בבקשה
    student_miluim_group: Optional[str] = None
