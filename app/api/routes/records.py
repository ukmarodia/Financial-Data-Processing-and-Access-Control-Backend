from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, UserRole
from app.models.record import RecordType
from app.schemas.record import RecordCreate, RecordUpdate, RecordResponse, PaginatedRecords
from app.services.record_service import RecordService
from app.api.deps import get_current_user, require_role


router = APIRouter(prefix="/records", tags=["Records"])


@router.get("", response_model=PaginatedRecords)
def list_records(
    type: Optional[RecordType] = None,
    category: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    q: Optional[str] = Query(None, description="Search term for category or notes"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List records. 
    Viewers see only their own. Analysts and Admins see all.
    Supports filtering and pagination.
    """
    return RecordService.get_records(
        db, current_user, type, category, date_from, date_to, q, page, per_page
    )


@router.get("/{record_id}", response_model=RecordResponse)
def get_record(
    record_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific record. Viewers can only request their own."""
    return RecordService.get_record(db, current_user, record_id)


@router.post("", response_model=RecordResponse, status_code=status.HTTP_201_CREATED)
def create_record(
    req: RecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """Create a new financial record. Admin ONLY."""
    return RecordService.create_record(db, current_user, req)


@router.put("/{record_id}", response_model=RecordResponse)
def update_record(
    record_id: int,
    req: RecordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """Update an existing record entirely or partially. Admin ONLY."""
    return RecordService.update_record(db, current_user, record_id, req)


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """Soft delete a record. Admin ONLY."""
    RecordService.delete_record(db, current_user, record_id)
