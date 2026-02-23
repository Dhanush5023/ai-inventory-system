"""
API v1 Blueprint
"""

from flask import Blueprint

api_v1_bp = Blueprint("api_v1", __name__)

from . import auth, users, products, sales, suppliers, orders, predictions, alerts, analytics, dashboard

# The blueprints from submodules will be registered to api_v1_bp
# or we can just import the modules and they register themselves to api_v1_bp
# In this case, I'll have the submodules define their own blueprints and register them here.

api_v1_bp.register_blueprint(auth.bp, url_prefix="/auth")
api_v1_bp.register_blueprint(users.bp, url_prefix="/users")
api_v1_bp.register_blueprint(products.bp, url_prefix="/products")
api_v1_bp.register_blueprint(sales.bp, url_prefix="/sales")
api_v1_bp.register_blueprint(suppliers.bp, url_prefix="/suppliers")
api_v1_bp.register_blueprint(orders.bp, url_prefix="/orders")
api_v1_bp.register_blueprint(predictions.bp, url_prefix="/predictions")
api_v1_bp.register_blueprint(alerts.bp, url_prefix="/alerts")
api_v1_bp.register_blueprint(analytics.bp, url_prefix="/analytics")
api_v1_bp.register_blueprint(dashboard.bp, url_prefix="/dashboard")

# AI Features (isolated to prevent dependency issues)
try:
    from . import chatbot
    api_v1_bp.register_blueprint(chatbot.bp, url_prefix="/ai/chatbot")
except Exception as e:
    print(f"[WARNING] Could not load Chatbot blueprint: {e}")

try:
    from . import optimization
    api_v1_bp.register_blueprint(optimization.bp, url_prefix="/ai/optimization")
except Exception as e:
    print(f"[WARNING] Could not load Optimization blueprint: {e}")

try:
    from . import autonomous
    api_v1_bp.register_blueprint(autonomous.bp, url_prefix="/ai/autonomous")
except Exception as e:
    print(f"[WARNING] Could not load Autonomous blueprint: {e}")

try:
    from . import perception
    api_v1_bp.register_blueprint(perception.bp, url_prefix="/ai/perception")
except Exception as e:
    print(f"[WARNING] Could not load Perception blueprint: {e}")
