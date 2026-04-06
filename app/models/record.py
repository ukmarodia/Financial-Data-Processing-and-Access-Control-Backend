import enum
from datetime import datetime, date, timezone

from sqlalchemy import (
    String, Float, Enum, DateTime, Date, Integer, Boolean, ForeignKey, Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class RecordType(str, enum.Enum):
    INCOME = "income"
    EXPENSE = "expense"


class FinancialRecord(Base):
    __tablename__ = "financial_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    type: Mapped[RecordType] = mapped_column(Enum(RecordType), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # who created this record — links back to the User table
    created_by: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    creator: Mapped["User"] = relationship("User", back_populates="records")

    # soft delete: financial records should never truly disappear
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self):
        return f"<Record #{self.id} {self.type.value} {self.amount}>"
