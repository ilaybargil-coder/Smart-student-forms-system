from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db import get_db
from models import RequestType
from schemas import RequestTypeOut

router = APIRouter(prefix="/request-types", tags=["request-types"])


@router.get("", response_model=list[RequestTypeOut])
def list_request_types(db: Session = Depends(get_db)):
    return (
        db.query(RequestType)
        .filter(RequestType.is_active == True)
        .order_by(RequestType.code.asc())
        .all()
    )