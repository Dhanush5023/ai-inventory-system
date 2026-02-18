from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from ...models.database import get_db
from ...schemas.analytics import AnalyticsDashboard, DateRangeFilter, RecommendationRequest
from ...schemas.products import ProductResponse
from ...services.analytics_service import AnalyticsService
from ...services.reporting_service import ReportingService
from fastapi.responses import FileResponse
import os
import tempfile
from typing import List
from ...core.security import get_current_user_id

router = APIRouter()


@router.get("", response_model=AnalyticsDashboard)
def get_analytics_dashboard(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get comprehensive analytics dashboard"""
    return AnalyticsService.get_analytics_dashboard(db, start_date, end_date)


@router.post("/recommendations", response_model=List[ProductResponse])
def get_recommendations(
    request: RecommendationRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get AI product recommendations based on cart items"""
    return AnalyticsService.get_recommendations(db, request.cart_product_ids)


@router.get("/export")
def export_report(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Generate and download weekly AI insight PDF report"""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        ReportingService.generate_weekly_ai_report(db, tmp.name)
        return FileResponse(
            tmp.name, 
            media_type="application/pdf", 
            filename=f"AI_Inventory_Report_{datetime.now().strftime('%Y%m%d')}.pdf"
        )
