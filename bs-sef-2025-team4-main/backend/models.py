import uuid
from sqlalchemy import Column, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from db import Base


class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name = Column(Text, nullable=True)
    last_name = Column(Text, nullable=True)
    email = Column(Text, unique=True, index=True, nullable=False)
    role = Column(Text, nullable=False, default="STUDENT")
    password_hash = Column(Text, nullable=False)
    # 🔥🔥🔥 הוספתי את זה: העמודה שהייתה חסרה! 🔥🔥🔥
    miluim_group_code = Column(Text, nullable=True)


class Course(Base):
    __tablename__ = "courses"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(Text)
    name_he = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Enrollment(Base):
    __tablename__ = "enrollments"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class CourseLecturer(Base):
    __tablename__ = "course_lecturers"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id"))
    lecturer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    is_primary = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class RequestType(Base):
    __tablename__ = "request_types"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(Text, nullable=False)
    name_he = Column(Text, nullable=False)
    route_policy = Column(Text, nullable=False)
    default_lecturer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Request(Base):
    __tablename__ = "requests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    lecturer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    student_national_id = Column(Text, nullable=True)
    request_type = Column(Text, nullable=False)
    request_description = Column(Text, nullable=True)

    lecturer_note = Column(Text, nullable=True)

    files = Column(JSONB, nullable=False, server_default='[]')
    status = Column(Text, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id"), nullable=True)