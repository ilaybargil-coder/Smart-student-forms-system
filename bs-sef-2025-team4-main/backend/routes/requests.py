import os
import uuid
import re
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from sqlalchemy.orm import Session
from uuid import UUID
from sqlalchemy import or_
from supabase import create_client, Client

from db import get_db
# 🔥 תיקון: הוספתי את Course לרשימת הייבוא כאן למטה 👇
from models import Request, User, Enrollment, CourseLecturer, RequestType, Course
from schemas import RequestOut, RequestRowOut, RequestStatusUpdate
from routes.auth import get_current_user

from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

router = APIRouter(prefix="/requests", tags=["requests"])

ALLOWED_STATUSES = {"SUBMITTED", "IN_PROGRESS", "APPROVED", "REJECTED"}

def extract_miluim_info(description: str) -> Optional[str]:
    """פונקציית עזר לבדיקות - מחלצת את אות המתווה מהתיאור"""
    if not description:
        return None
    match = re.search(r"בקשה למתווה:.*?([A-C])", description)
    return match.group(1) if match else None

@router.get("/miluim-groups")
def get_miluim_groups():
    try:
        response = supabase.table("miluim_groups").select("*").order("code").execute()
        return response.data
    except Exception as e:
        print(f"Error fetching miluim groups: {e}")
        return []


@router.post("", response_model=RequestOut)
async def create_request(
        request_type: str = Form(...),
        student_national_id: str = Form(None),
        request_description: str = Form(...),
        course_id: Optional[UUID] = Form(None),
        lecturer_id: Optional[UUID] = Form(None),
        files: List[UploadFile] = File(default=[]),
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
):
    # 1. וולידציה לתעודת זהות
    if student_national_id:
        clean_id = student_national_id.strip()
        if len(clean_id) != 9 or not clean_id.isdigit():
            # ההודעה הזו תחזור למשתמש ב-Frontend
            raise HTTPException(status_code=400, detail="תעודת הזהות חייבת להכיל בדיוק 9 ספרות.")

    role = (current_user.role or "").upper()
    if role != "STUDENT":
        raise HTTPException(status_code=403, detail="רק סטודנט מורשה לפתוח בקשה חדשה.")

    req_code = (request_type or "").strip().upper()
    rt = db.query(RequestType).filter(RequestType.code == req_code).first()

    # 2. בדיקה אם סוג הבקשה קיים
    if not rt:
        raise HTTPException(status_code=400, detail="סוג הבקשה שנבחר אינו תקין.")

    final_lecturer_id = None
    route_policy = (rt.route_policy or "").upper() if rt else "ADMIN"

    # 3. בדיקת חובת בחירת קורס
    if route_policy == "COURSE_LECTURER":
        if not course_id:
            raise HTTPException(status_code=400, detail="עבור סוג בקשה זה, חובה לבחור קורס מרשימת הקורסים שלך.")

        is_enrolled = db.query(Enrollment).filter(
            Enrollment.student_id == current_user.id,
            Enrollment.course_id == course_id
        ).first()

        if not is_enrolled:
            raise HTTPException(status_code=403, detail="אינך רשום לקורס שנבחר.")

        # לוגיקת בחירת מרצה (נשארת אותו דבר)
        if lecturer_id:
            final_lecturer_id = lecturer_id
        else:
            cl = db.query(CourseLecturer).filter(CourseLecturer.course_id == course_id,
                                                 CourseLecturer.is_primary == True).first()
            final_lecturer_id = cl.lecturer_id if cl else rt.default_lecturer_id
    else:
        final_lecturer_id = rt.default_lecturer_id

    uploaded_files_data = []
    for file in files:
        if file.filename:
            try:
                file_content = await file.read()
                file_ext = os.path.splitext(file.filename)[1] or ""
                safe_filename = f"{uuid.uuid4()}{file_ext}"
                path_on_storage = f"{current_user.id}/{safe_filename}"
                bucket_name = "request-files"
                supabase.storage.from_(bucket_name).upload(path=path_on_storage, file=file_content,
                                                           file_options={"content-type": file.content_type})
                base_url = SUPABASE_URL.rstrip("/")
                public_url = f"{base_url}/storage/v1/object/public/{bucket_name}/{path_on_storage}"
                uploaded_files_data.append(
                    {"name": file.filename, "size": file.size, "type": file.content_type, "url": public_url})
            except Exception as e:
                print(f"Error uploading file: {e}")

    r = Request(
        student_id=current_user.id,
        lecturer_id=final_lecturer_id,
        student_national_id=student_national_id,
        request_type=req_code,
        request_description=request_description,
        files=uploaded_files_data,
        status="SUBMITTED",
        course_id=course_id,
    )
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


@router.get("", response_model=list[RequestRowOut])
def list_requests(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    role = (current_user.role or "").upper()

    # שאילתה שמושכת גם את פרטי המשתמש והקורס (כדי להציג שמות ומתווה)
    q = db.query(Request, User, Course) \
        .join(User, Request.student_id == User.id) \
        .outerjoin(Course, Request.course_id == Course.id)

    if role == "ADMIN":
        pass
    elif role == "LECTURER":
        my_courses = db.query(CourseLecturer.course_id).filter(CourseLecturer.lecturer_id == current_user.id).all()
        my_course_ids = [c[0] for c in my_courses]

        q = q.filter(
            or_(
                Request.lecturer_id == current_user.id,
                Request.course_id.in_(my_course_ids)
            )
        )
    elif role == "STUDENT":
        q = q.filter(Request.student_id == current_user.id)
    else:
        raise HTTPException(status_code=403, detail="ROLE לא מורשה")

    results = q.order_by(Request.created_at.desc()).all()

    response = []
    for req, student, course in results:
        r_out = RequestRowOut(
            id=req.id,
            student_id=req.student_id,
            student_national_id=req.student_national_id,
            request_type=req.request_type,
            request_description=req.request_description,
            status=req.status,
            lecturer_note=req.lecturer_note,
            created_at=req.created_at,
            updated_at=req.updated_at,
            course_id=req.course_id,
            files=req.files,

            # פרטים נוספים לתצוגה
            student_name=f"{student.first_name} {student.last_name}",
            student_miluim_group=student.miluim_group_code,
            course_name=course.name_he if course else None
        )
        response.append(r_out)

    return response


@router.patch("/{request_id}/status", response_model=RequestRowOut)
def update_request_status(
        request_id: UUID,
        payload: RequestStatusUpdate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
):
    role = (current_user.role or "").upper()
    if role not in {"ADMIN", "LECTURER"}:
        raise HTTPException(status_code=403, detail="רק מרצה/אדמין יכולים לעדכן סטטוס")

    new_status = (payload.status or "").strip().upper()
    if new_status not in ALLOWED_STATUSES:
        raise HTTPException(status_code=400, detail=f"סטטוס לא חוקי")

    req = db.query(Request).filter(Request.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="בקשה לא נמצאה")

    if role == "LECTURER" and req.lecturer_id != current_user.id:
        raise HTTPException(status_code=403, detail="אין לך הרשאה לבקשה זו")

    req.status = new_status
    if payload.lecturer_note is not None:
        req.lecturer_note = payload.lecturer_note

    db.commit()
    db.refresh(req)

    # ------------------------------------------------------------------
    # 🔥 עדכון מילואים בטוח בטבלת USERS 🔥
    # ------------------------------------------------------------------
    if new_status == "APPROVED" and req.request_type == "RESERVE_DUTY_JOIN":
        try:
            print(f"\n--- ATTEMPTING MILUIM UPDATE (Direct User Table) ---")

            match = re.search(r"בקשה למתווה:.*?([A-C])", req.request_description or "")
            if match:
                group_code = match.group(1)
                student_id = str(req.student_id)
                print(f">> Code found: {group_code} for Student: {student_id}")

                response = supabase.table("users").update({
                    "miluim_group_code": group_code
                }).eq("id", student_id).execute()

                print(">> SUCCESS! User updated safely.")
            else:
                print(">> No group code found in description.")

        except Exception as e:
            print(f"WARNING: Miluim update failed: {e}")

    return req


@router.delete("/{request_id}")
def delete_request(request_id: UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    role = (current_user.role or "").upper()
    if role != "ADMIN":
        raise HTTPException(status_code=403, detail="רק מנהל מערכת יכול למחוק בקשות")
    req = db.query(Request).filter(Request.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="בקשה לא נמצאה")
    db.delete(req)
    db.commit()
    return {"message": "Request deleted successfully"}