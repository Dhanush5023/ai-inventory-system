import os
from typing import List, Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from sqlalchemy.orm import Session
from datetime import datetime

from ...models.database import Product, Sale, Alert, Prediction
from ...ai.anomaly_detection.detector import anomaly_detector
from ...core.config import settings

class InventoryAssistant:
    """GenAI Smart Decision Assistant for Inventory Management"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.GOOGLE_API_KEY
        if not self.api_key:
            # Fallback for demonstration if no key is provided
            self.model = None
        else:
            print(f"[DEBUG] Initializing InventoryAssistant with model: gemini-flash-latest")
            self.model = ChatGoogleGenerativeAI(
                model="gemini-flash-latest",
                google_api_key=self.api_key,
                temperature=0.2
            )
            
    def get_system_context(self, db: Session) -> str:
        """Gather context from the database to inform the AI"""
        # Summary of low stock items
        low_stock = db.query(Product).filter(Product.current_stock <= Product.minimum_stock).all()
        # Summary of recent critical alerts
        alerts = db.query(Alert).filter(Alert.severity == "critical", Alert.is_resolved == False).limit(5).all()
        # Summary of recent security anomalies
        anomalies = anomaly_detector.detect_sales_anomalies(db)
        
        context = f"""
        Current Inventory Context:
        - Low stock products: {", ".join([p.name for p in low_stock]) if low_stock else "None"}
        - Critical Alerts: {", ".join([a.message for a in alerts]) if alerts else "None"}
        - Security Anomalies: {len(anomalies)} suspicious transactions detected.
        - System Date: {datetime.now().strftime('%Y-%m-%d')}
        """
        print(f"[DEBUG] Assistant Context: {len(low_stock)} low stock, {len(alerts)} alerts")
        return context

    async def answer_question(self, question: str, db: Session) -> str:
        """Answer a business question using context and GenAI"""
        if not self.model:
            return "AI Chatbot is in demonstration mode. Please provide a GOOGLE_API_KEY in the .env file to enable full functionality."
            
        context = self.get_system_context(db)
        
        prompt = ChatPromptTemplate.from_template("""
        You are the "GenAI Smart Decision Assistant" for an AI Inventory Management System.
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
            print(f"[DEBUG] Chatbot invoking model: {self.model.model}")
            response = await chain.ainvoke({"context": context, "question": question})
            return response.content
        except Exception as e:
            print(f"[ERROR] Chatbot Invocation Failed: {str(e)}")
            return f"Error communicating with AI: {str(e)}"

# Global instance
assistant = InventoryAssistant()
