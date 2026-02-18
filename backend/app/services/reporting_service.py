import os
from datetime import datetime
from typing import List, Dict, Any
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from sqlalchemy.orm import Session

from .analytics_service import AnalyticsService
from ..models.database import Product, Alert

class ReportingService:
    """Service for generating PDF business reports"""

    @staticmethod
    def generate_weekly_ai_report(db: Session, output_path: str) -> str:
        """Generate a comprehensive weekly AI insight report"""
        
        # 1. Fetch Data
        dashboard = AnalyticsService.get_analytics_dashboard(db)
        low_stock = db.query(Product).filter(Product.current_stock <= Product.minimum_stock).all()
        recent_alerts = db.query(Alert).order_by(Alert.created_at.desc()).limit(10).all()
        
        # 2. Setup PDF
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []

        # Title
        title_style = ParagraphStyle(
            'ReportTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.indigo
        )
        elements.append(Paragraph("Weekly AI Inventory Insights", title_style))
        elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
        elements.append(Spacer(1, 20))

        # Executive Summary
        elements.append(Paragraph("Executive Summary", styles['Heading2']))
        summary_text = f"""
        This week, the AI system analyzed {dashboard.inventory_metrics.total_products} products. 
        Total revenue recorded is ₹{dashboard.sales_metrics.total_revenue:,.2f} with a gross profit margin of {dashboard.financial_metrics.profit_margin:.1f}%.
        Currently, there are {dashboard.inventory_metrics.low_stock_products} products requiring immediate attention.
        """
        elements.append(Paragraph(summary_text, styles['Normal']))
        elements.append(Spacer(1, 15))

        # KPI Table
        data = [
            ["Metric", "Value"],
            ["Total Revenue", f"₹{dashboard.sales_metrics.total_revenue:,.2f}"],
            ["Stock Value", f"₹{dashboard.inventory_metrics.total_stock_value:,.2f}"],
            ["Inventory Turnover", f"{dashboard.inventory_metrics.inventory_turnover_ratio:.2f}"],
            ["Active Alerts", str(dashboard.overview.critical_alerts)]
        ]
        t = Table(data, colWidths=[200, 200])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.indigo),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0,0), (-1,-1), 1, colors.black)
        ]))
        elements.append(t)
        elements.append(Spacer(1, 20))

        # Critical Stock Table
        elements.append(Paragraph("Critical Stock Items", styles['Heading3']))
        if low_stock:
            stock_data = [["Product", "SKU", "Current", "Minimum"]]
            for p in low_stock[:15]: # Limit to top 15
                stock_data.append([p.name, p.sku, str(p.current_stock), str(p.minimum_stock)])
            
            st = Table(stock_data, colWidths=[150, 100, 75, 75])
            st.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.red),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('GRID', (0,0), (-1,-1), 0.5, colors.grey)
            ]))
            elements.append(st)
        else:
            elements.append(Paragraph("No low stock items detected.", styles['Italic']))

        # Build PDF
        doc.build(elements)
        return output_path
