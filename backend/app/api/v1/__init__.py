"""
API v1 Router
"""

from fastapi import APIRouter
from . import auth, users, products, sales, suppliers, orders, predictions, alerts, analytics, dashboard

api_router = APIRouter()

# Core route modules
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(products.router, prefix="/products", tags=["Products"])
api_router.include_router(sales.router, prefix="/sales", tags=["Sales"])
api_router.include_router(suppliers.router, prefix="/suppliers", tags=["Suppliers"])
api_router.include_router(orders.router, prefix="/orders", tags=["Orders"])
api_router.include_router(predictions.router, prefix="/predictions", tags=["Predictions"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["Alerts"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])

# AI Features (isolated to prevent dependency issues from crashing the whole API)
try:
    from . import chatbot
    api_router.include_router(chatbot.router, prefix="/ai/chatbot", tags=["AI Chatbot"])
except Exception as e:
    print(f"[WARNING] Could not load Chatbot router: {e}")

try:
    from . import optimization
    api_router.include_router(optimization.router, prefix="/ai/optimization", tags=["AI Optimization"])
except Exception as e:
    print(f"[WARNING] Could not load Optimization router: {e}")

try:
    from . import autonomous
    api_router.include_router(autonomous.router, prefix="/ai/autonomous", tags=["Autonomous Operations"])
except Exception as e:
    print(f"[WARNING] Could not load Autonomous router: {e}")

try:
    from . import perception
    api_router.include_router(perception.router, prefix="/ai/perception", tags=["Perception & Security"])
except Exception as e:
    print(f"[WARNING] Could not load Perception router: {e}")
