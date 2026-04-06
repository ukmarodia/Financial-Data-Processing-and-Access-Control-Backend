from datetime import date
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import desc, or_

from app.models.record import FinancialRecord, RecordType
from app.models.user import User, UserRole
from app.schemas.record import RecordCreate, RecordUpdate, PaginatedRecords
from app.exceptions import NotFoundError, ForbiddenError


class RecordService:
    @staticmethod
    def _apply_visibility(query, user: User):
        """
        Admins and Analysts can see all records.
        Viewers can only see their own records.
        (This handles the ownership requirement).
        """
        if user.role == UserRole.VIEWER:
            return query.filter(FinancialRecord.created_by == user.id)
        return query

    @staticmethod
    def get_records(
        db: Session,
        current_user: User,
        type: Optional[RecordType] = None,
        category: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        q: Optional[str] = None,
        page: int = 1,
        per_page: int = 20
    ) -> PaginatedRecords:
        """Fetch paginated, filtered records, respecting soft deletes and visibility."""
        
        # Base query: exclude soft deleted
        query = db.query(FinancialRecord).filter(FinancialRecord.is_deleted == False)

        # Apply visibility scoping based on role
        query = RecordService._apply_visibility(query, current_user)

        # Apply Optional Filters
        if type:
            query = query.filter(FinancialRecord.type == type)
        if category:
            query = query.filter(FinancialRecord.category == category)
        if date_from:
            query = query.filter(FinancialRecord.date >= date_from)
        if date_to:
            query = query.filter(FinancialRecord.date <= date_to)

        if q:
            query = query.filter(
                or_(
                    FinancialRecord.category.ilike(f"%{q}%"),
                    FinancialRecord.notes.ilike(f"%{q}%")
                )
            )

        # Count total before paginating
        total = query.count()

        # Paginate
        records = query.order_by(desc(FinancialRecord.date)).offset((page - 1) * per_page).limit(per_page).all()

        pages = (total + per_page - 1) // per_page

        return PaginatedRecords(
            items=records,
            total=total,
            page=page,
            per_page=per_page,
            pages=pages
        )

    @staticmethod
    def get_record(db: Session, current_user: User, record_id: int) -> FinancialRecord:
        record = db.query(FinancialRecord).filter(
            FinancialRecord.id == record_id,
            FinancialRecord.is_deleted == False
        ).first()

        if not record:
            raise NotFoundError("Financial record not found")

        # Viewers can only view their own items
        if current_user.role == UserRole.VIEWER and record.created_by != current_user.id:
            raise ForbiddenError("You can only view your own records")
            
        return record

    @staticmethod
    def create_record(db: Session, current_user: User, req: RecordCreate) -> FinancialRecord:
        record = FinancialRecord(
            **req.model_dump(),
            created_by=current_user.id
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    @staticmethod
    def update_record(db: Session, current_user: User, record_id: int, req: RecordUpdate) -> FinancialRecord:
        # Note: only Admins should route here (checked at API layer)
        record = RecordService.get_record(db, current_user, record_id)
        
        update_data = req.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(record, key, value)
            
        db.commit()
        db.refresh(record)
        return record

    @staticmethod
    def delete_record(db: Session, current_user: User, record_id: int):
        # Note: only Admins should route here (checked at API layer)
        record = RecordService.get_record(db, current_user, record_id)
        record.is_deleted = True # Soft delete
        db.commit()
