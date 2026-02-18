from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ...models.database import get_db
from ...schemas.analytics import DashboardOverview
from ...services.analytics_service import AnalyticsService
from ...core.security import get_current_user_id

router = APIRouter()


@router.get("", response_model=DashboardOverview)
def get_dashboard(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get main dashboard overview with KPIs"""
    return AnalyticsService.get_dashboard_overview(db)
