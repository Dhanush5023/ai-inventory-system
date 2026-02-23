from flask import Blueprint, request, jsonify, send_file
from typing import Optional, List
from datetime import datetime
import os
import tempfile
from ...models.database import get_db
from ...schemas.analytics import AnalyticsDashboard, RecommendationRequest
from ...schemas.products import ProductResponse
from ...services.analytics_service import AnalyticsService
from ...services.reporting_service import ReportingService
from ...services.ai_market_service import AIMarketService
from ...schemas.market_intelligence import MarketIntelligenceResponse
from ...core.security import login_required, roles_required

bp = Blueprint("analytics", __name__)


@bp.route("", methods=["GET"])
@login_required
@roles_required("admin", "manager")
def get_analytics_dashboard():
    """Get comprehensive analytics dashboard"""
    db = get_db()
    
    start_date_str = request.args.get("start_date")
    start_date = datetime.fromisoformat(start_date_str) if start_date_str else None
    
    end_date_str = request.args.get("end_date")
    end_date = datetime.fromisoformat(end_date_str) if end_date_str else None
    
    data = AnalyticsService.get_analytics_dashboard(db, start_date, end_date)
    return jsonify(AnalyticsDashboard.model_validate(data).model_dump())


@bp.route("/recommendations", methods=["POST"])
@login_required
def get_recommendations():
    """Get AI product recommendations based on cart items"""
    db = get_db()
    try:
        rec_request = RecommendationRequest(**request.json)
    except Exception as e:
        return jsonify({"detail": str(e)}), 400
        
    recommendations = AnalyticsService.get_recommendations(db, rec_request.cart_product_ids)
    return jsonify([ProductResponse.model_validate(p).model_dump() for p in recommendations])


@bp.route("/export", methods=["GET"])
@login_required
@roles_required("admin", "manager")
def export_report():
    """Generate and download weekly AI insight PDF report"""
    db = get_db()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        ReportingService.generate_weekly_ai_report(db, tmp.name)
        return send_file(
            tmp.name, 
            mimetype="application/pdf", 
            as_attachment=True,
            download_name=f"AI_Inventory_Report_{datetime.now().strftime('%Y%m%d')}.pdf"
        )

@bp.route("/market-intelligence", methods=["GET"])
@login_required
@roles_required("admin", "manager")
def get_market_intelligence():
    """Get high-end business intelligence and proactive insights"""
    db = get_db()
    data = AIMarketService.get_market_intelligence(db)
    return jsonify(MarketIntelligenceResponse.model_validate(data).model_dump())
