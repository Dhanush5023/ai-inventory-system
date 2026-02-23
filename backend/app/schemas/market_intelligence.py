from pydantic import BaseModel
from typing import List, Optional

class BusinessInsight(BaseModel):
    title: str
    description: str
    impact_level: str # 'High', 'Medium', 'Low'
    category: str # 'Revenue', 'Efficiency', 'Risk'

class MarketBrief(BaseModel):
    summary: str
    headline_insight: str
    roi_score: float
    top_efficiency_gain: str

class ProactiveOptimization(BaseModel):
    id: str
    action: str
    potential_savings: float
    urgency: str

class MarketIntelligenceResponse(BaseModel):
    brief: MarketBrief
    insights: List[BusinessInsight]
    optimizations: List[ProactiveOptimization]
