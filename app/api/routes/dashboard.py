from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import UserRole
from app.schemas.dashboard import SummaryResponse, CategoryBreakdownResponse, TrendsResponse
from app.schemas.record import RecordResponse
from app.services.dashboard_service import DashboardService
from app.api.deps import require_role



router = APIRouter(
    prefix="/dashboard", 
    tags=["Dashboard"],
    dependencies=[Depends(require_role(UserRole.ADMIN, UserRole.ANALYST, UserRole.VIEWER))]
)


@router.get("/summary", response_model=SummaryResponse)
def get_summary(db: Session = Depends(get_db)):
    
    return DashboardService.get_summary(db)


@router.get("/category-breakdown", response_model=CategoryBreakdownResponse)
def get_category_breakdown(db: Session = Depends(get_db)):
  
    return DashboardService.get_category_breakdown(db)


@router.get("/trends", response_model=TrendsResponse)
def get_trends(db: Session = Depends(get_db)):
    
    return DashboardService.get_trends(db)


@router.get("/recent", response_model=list[RecordResponse])
def get_recent_activity(db: Session = Depends(get_db)):
   
    return DashboardService.get_recent_activity(db, limit=10)
