import os
import traceback
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from ...models.database import Product, Sale, Alert, Prediction
from ...core.config import settings


class InventoryAssistant:
    """GenAI Smart Decision Assistant for Inventory Management"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.GOOGLE_API_KEY
        self._model = None  # Lazy initialization — do NOT connect at startup
        
    @property
    def model(self):
        """Lazily initialize the AI model only when first needed."""
        if self._model is None and self.api_key:
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI
                print(f"[DEBUG] Lazy-initializing InventoryAssistant with model: gemini-flash-latest")
                self._model = ChatGoogleGenerativeAI(
                    model="gemini-flash-latest",
                    google_api_key=self.api_key,
                    temperature=0.2
                )
            except Exception as e:
                print(f"[WARNING] Could not initialize AI model: {e}")
                self._model = None
        return self._model
            
    def get_system_context(self, db: Session) -> str:
        """Gather context from the database to inform the AI"""
        from ...ai.anomaly_detection.detector import anomaly_detector
        from ...services.analytics_service import AnalyticsService
        
        # Summary of financial metrics
        financials = AnalyticsService.get_financial_metrics(db)
        overview = AnalyticsService.get_dashboard_overview(db)
        
        # Summary of low stock items
        low_stock = db.query(Product).filter(Product.current_stock <= Product.minimum_stock).all()
        # Summary of recent critical alerts
        alerts = db.query(Alert).filter(Alert.severity == "critical", Alert.is_resolved == False).limit(5).all()
        # Summary of recent security anomalies
        try:
            anomalies = anomaly_detector.detect_sales_anomalies(db)
        except Exception:
            anomalies = []
        
        context = f"""
        Current System Context:
        - Financial Health:
            * Total Revenue (Last 30 days): {overview.kpis[1].value}
            * Total Revenue (All-time): INR {financials.total_revenue:,.2f}
            * Gross Profit: INR {financials.gross_profit:,.2f}
            * Profit Margin: {financials.profit_margin}%
        - Inventory Status:
            * Low stock products: {", ".join([p.name for p in low_stock]) if low_stock else "None"}
            * Total Products: {overview.kpis[0].value}
        - Operational Security:
            * Critical Alerts: {", ".join([a.message for a in alerts]) if alerts else "None"}
            * Security Anomalies: {len(anomalies)} suspicious transactions detected.
        - System Date: {datetime.now().strftime('%Y-%m-%d')}
        """
        return context

    def answer_question(self, question: str, db: Session) -> str:
        """Answer a business question using context and GenAI"""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        if not self.model:
            return "AI Chatbot is in demonstration mode. Please provide a GOOGLE_API_KEY in the .env file to enable full functionality."
            
        from langchain.prompts import ChatPromptTemplate
        context = self.get_system_context(db)
        
        prompt = ChatPromptTemplate.from_template("""
        You are the "GenAI Smart Decision Assistant" for QUANTUM NEXUS (AI Inventory Management System).
        Use the following system context and your internal knowledge to answer the user's business question.
        
        System Context:
        {context}
        
        User Question: {question}
        
        Helpful Instructions:
        - Be concise and professional.
        - If the question is about stock levels or predictions, refer to the provided context.
        - If you don't know the answer based on context, say so and suggest what data might be needed.
        - Provide actionable insights where possible.
        
        Answer:
        """)
        
        chain = prompt | self.model
        
        try:
            response = chain.invoke({"context": context, "question": question})
            return response.content
        except Exception as e:
            print(f"[ERROR] Chatbot Invocation Failed: {str(e)}")
            traceback.print_exc()
            return f"Error communicating with AI: {str(e)}"

# Global instance — model not loaded until first use
assistant = InventoryAssistant()
