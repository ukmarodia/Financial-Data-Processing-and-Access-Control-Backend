from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func, case

from app.models.record import FinancialRecord, RecordType
from app.schemas.dashboard import (
    SummaryResponse, CategoryBreakdownResponse, CategoryTotal,
    TrendsResponse, MonthlyTrend
)


class DashboardService:
   
    @staticmethod
    def _base_query(db: Session):
       
        return db.query(FinancialRecord).filter(FinancialRecord.is_deleted == False)

    @staticmethod
    def get_summary(db: Session) -> SummaryResponse:
       

        income_sum = DashboardService._base_query(db).filter(
            FinancialRecord.type == RecordType.INCOME
        ).with_entities(func.sum(FinancialRecord.amount)).scalar() or 0.0

        expense_sum = DashboardService._base_query(db).filter(
            FinancialRecord.type == RecordType.EXPENSE
        ).with_entities(func.sum(FinancialRecord.amount)).scalar() or 0.0

        count = DashboardService._base_query(db).count()

        return SummaryResponse(
            total_income=round(income_sum, 2),
            total_expenses=round(expense_sum, 2),
            net_balance=round(income_sum - expense_sum, 2),
            record_count=count
        )

    @staticmethod
    def get_category_breakdown(db: Session) -> CategoryBreakdownResponse:
       

        def fetch_grouped(record_type: RecordType) -> list[CategoryTotal]:
            results = DashboardService._base_query(db).filter(
                FinancialRecord.type == record_type
            ).with_entities(
                FinancialRecord.category,
                func.sum(FinancialRecord.amount).label("total"),
                func.count(FinancialRecord.id).label("count")
            ).group_by(FinancialRecord.category).order_by(
                func.sum(FinancialRecord.amount).desc()
            ).all()

            return [
                CategoryTotal(category=r.category, total=round(r.total, 2), count=r.count)
                for r in results
            ]

        return CategoryBreakdownResponse(
            income_by_category=fetch_grouped(RecordType.INCOME),
            expense_by_category=fetch_grouped(RecordType.EXPENSE)
        )

    @staticmethod
    def get_trends(db: Session) -> TrendsResponse:
      

       
        now = datetime.now()
        year = now.year
        month = now.month - 11
        if month <= 0:
            month += 12
            year -= 1
        twelve_months_ago = datetime(year, month, 1).date()

        
        results = DashboardService._base_query(db).filter(
            FinancialRecord.date >= twelve_months_ago
        ).with_entities(
            func.strftime('%Y-%m', FinancialRecord.date).label('month'),
            func.sum(
                case(
                    (FinancialRecord.type == RecordType.INCOME, FinancialRecord.amount),
                    else_=0
                )
            ).label('income'),
            func.sum(
                case(
                    (FinancialRecord.type == RecordType.EXPENSE, FinancialRecord.amount),
                    else_=0
                )
            ).label('expense'),
        ).group_by('month').order_by('month').all()

        trends = [
            MonthlyTrend(
                month=r.month,
                income=round(r.income or 0.0, 2),
                expense=round(r.expense or 0.0, 2),
                net=round((r.income or 0.0) - (r.expense or 0.0), 2)
            )
            for r in results
        ]

        return TrendsResponse(trends=trends)

    @staticmethod
    def get_recent_activity(db: Session, limit: int = 10) -> list[FinancialRecord]:
       
        return DashboardService._base_query(db).order_by(
            FinancialRecord.date.desc(),
            FinancialRecord.created_at.desc()
        ).limit(limit).all()
