from app.models.database import SessionLocal, User
from app.core.security import verify_password, get_password_hash
import sys

def test_auth():
    db = SessionLocal()
    try:
        email = "admin@inventory.com"
        password = "admin123"
        
        user = db.query(User).filter(User.email == email).first()
        if not user:
            print(f"User {email} not found in database!")
            return
            
        print(f"User found: {user.email}")
        print(f"Hashed password in DB: {user.hashed_password}")
        
        # Test hashing again for comparison
        re_hashed = get_password_hash(password)
        print(f"Newly hashed for comparison: {re_hashed}")
        
        is_valid = verify_password(password, user.hashed_password)
        print(f"Authentication result: {is_valid}")
        
        if is_valid:
            print("AUTH TEST PASSED")
        else:
            print("AUTH TEST FAILED")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_auth()
