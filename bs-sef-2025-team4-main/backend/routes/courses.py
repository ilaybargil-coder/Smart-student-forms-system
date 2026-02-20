from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from db import get_db
from models import Course, Enrollment, User, CourseLecturer
# תיקון: ייבוא המודלים הנכונים שקיימים ב-schemas.py שלך
from schemas import CourseOut, EnrollRequest, AssignLecturerRequest
from routes.auth import get_current_user

router = APIRouter(prefix="/courses", tags=["courses"])


# --- קריאת כל הקורסים (כללי) ---
@router.get("", response_model=List[CourseOut])
def list_courses(db: Session = Depends(get_db)):
    return db.query(Course).order_by(Course.code.asc()).all()


# --- קריאת כל הקורסים לאדמין ---
@router.get("/all", response_model=List[CourseOut])
def get_all_courses_for_admin(db: Session = Depends(get_db)):
    return db.query(Course).order_by(Course.code.asc()).all()


# --- קריאת קורסים של הסטודנט/מרצה המחובר ---
@router.get("/my", response_model=List[CourseOut])
def my_courses(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
):
    role = (current_user.role or "").upper()

    if role == "STUDENT":
        return (
            db.query(Course)
            .join(Enrollment, Enrollment.course_id == Course.id)
            .filter(Enrollment.student_id == current_user.id)
            .order_by(Course.code.asc())
            .all()
        )

    if role == "LECTURER":
        return (
            db.query(Course)
            .join(CourseLecturer, CourseLecturer.course_id == Course.id)
            .filter(CourseLecturer.lecturer_id == current_user.id)
            .order_by(Course.code.asc())
            .all()
        )

    if role == "ADMIN":
        return db.query(Course).order_by(Course.code.asc()).all()

    return []


# --- שליפת מרצים של קורס ספציפי ---
@router.get("/{course_id}/lecturers")
def get_course_lecturers(
        course_id: UUID,
        db: Session = Depends(get_db)
):
    results = db.query(User, CourseLecturer.is_primary) \
        .join(CourseLecturer, CourseLecturer.lecturer_id == User.id) \
        .filter(CourseLecturer.course_id == course_id) \
        .all()

    lecturers_list = []
    for user, is_primary in results:
        suffix = " (מרצה ראשי)" if is_primary else ""
        lecturers_list.append({
            "id": str(user.id),
            "name": f"{user.first_name} {user.last_name}{suffix}"
        })

    return lecturers_list


# --- אדמין: הרשמת סטודנט ---
# ✅ תיקון: הכתובת שונתה ל-/enroll כדי להתאים ל-HTML
@router.post("/enroll")
def enroll_student(
        payload: EnrollRequest, # שימוש במודל הנכון מ-schemas
        db: Session = Depends(get_db)
):
    # בדיקה אם הסטודנט כבר רשום
    exists = db.query(Enrollment).filter(
        Enrollment.student_id == payload.student_id,
        Enrollment.course_id == payload.course_id
    ).first()

    if exists:
        # מחזירים הודעה אבל לא שגיאה 400, כדי שהפרונט יציג אלרט יפה
        raise HTTPException(status_code=400, detail="הסטודנט כבר רשום לקורס הזה")

    new_enroll = Enrollment(
        student_id=payload.student_id,
        course_id=payload.course_id
    )
    db.add(new_enroll)
    db.commit()
    return {"message": "הסטודנט שויך לקורס בהצלחה"}


# --- אדמין: שיוך מרצה ---
# ✅ תיקון: הכתובת שונתה ל-/assign כדי להתאים ל-HTML
@router.post("/assign")
def assign_lecturer(
        payload: AssignLecturerRequest, # שימוש במודל הנכון מ-schemas
        db: Session = Depends(get_db)
):
    exists = db.query(CourseLecturer).filter(
        CourseLecturer.lecturer_id == payload.lecturer_id,
        CourseLecturer.course_id == payload.course_id
    ).first()

    if exists:
        raise HTTPException(status_code=400, detail="המרצה כבר משויך לקורס הזה")

    new_link = CourseLecturer(
        lecturer_id=payload.lecturer_id,
        course_id=payload.course_id,
        is_primary=False # ברירת מחדל
    )
    db.add(new_link)
    db.commit()
    return {"message": "המרצה שויך לקורס בהצלחה"}