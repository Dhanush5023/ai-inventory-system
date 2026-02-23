from flask import Blueprint, jsonify
from ...models.database import get_db
from ...schemas.analytics import DashboardOverview
from ...services.analytics_service import AnalyticsService
from ...core.security import login_required

bp = Blueprint("dashboard", __name__)


@bp.route("", methods=["GET"])
@login_required
def get_dashboard():
    """Get main dashboard overview with KPIs"""
    db = get_db()
    data = AnalyticsService.get_dashboard_overview(db)
    return jsonify(DashboardOverview.model_validate(data).model_dump())
