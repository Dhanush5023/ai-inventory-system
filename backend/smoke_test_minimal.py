import time

def test_import(module_name):
    print(f"Importing {module_name}...", flush=True)
    start = time.time()
    try:
        __import__(module_name)
        elapsed = time.time() - start
        print(f"DONE: {module_name} in {elapsed:.2f}s", flush=True)
        return True
    except Exception as e:
        print(f"FAILED: {module_name}: {e}", flush=True)
        return False

# Start with the basics we know work
test_import("flask")
test_import("app.core.config")
test_import("app.models.database")

# Now trace the auth chain
test_import("app.schemas.auth")
test_import("app.schemas.users")
test_import("app.core.security")
test_import("app.services.auth_service")
test_import("app.api.v1.auth")

# Prediction chain (the likely culprit due to ML libraries)
test_import("app.ai.forecasting.prediction_service")
test_import("app.services.product_service")

# Analytics 
test_import("app.services.analytics_service")
test_import("app.api.v1.analytics")

print("ALL DONE", flush=True)
