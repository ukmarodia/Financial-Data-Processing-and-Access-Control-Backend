from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, field_validator, ConfigDict

from app.models.record import RecordType


class RecordCreate(BaseModel):
    """Payload for creating a new financial record."""
    amount: float
    type: RecordType
    category: str
    date: date
    description: Optional[str] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "amount": 2500.50,
                "type": "income",
                "category": "salary",
                "date": "2024-03-20",
                "description": "March paycheck"
            }
        }
    )

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Amount must be greater than zero")
        return round(v, 2)

    @field_validator("category")
    @classmethod
    def category_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Category cannot be empty")
        return v.lower()


class RecordUpdate(BaseModel):
    """Payload for updating a record. All fields optional — only send what changed."""
    amount: Optional[float] = None
    type: Optional[RecordType] = None
    category: Optional[str] = None
    date: Optional[date] = None
    description: Optional[str] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "amount": 35.00,
                "type": "expense",
                "category": "utilities",
                "date": "2024-03-22",
                "description": "Water bill"
            }
        }
    )

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v <= 0:
            raise ValueError("Amount must be greater than zero")
        return round(v, 2) if v is not None else v

    @field_validator("category")
    @classmethod
    def category_not_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("Category cannot be empty")
            return v.lower()
        return v


class RecordResponse(BaseModel):
    """What we send back when returning a financial record."""
    id: int
    amount: float
    type: RecordType
    category: str
    date: date
    description: Optional[str]
    created_by: int
    created_at: datetime

    class Config:
        from_attributes = True


class PaginatedRecords(BaseModel):
    """Paginated list response — includes metadata so the frontend knows total pages."""
    items: list[RecordResponse]
    total: int
    page: int
    per_page: int
    pages: int
