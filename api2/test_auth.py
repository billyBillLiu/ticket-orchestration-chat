#!/usr/bin/env python3
"""
Test authentication and create test user if needed
"""
from app.models import SessionLocal, User
from app.routes.auth import get_password_hash, create_access_token
from datetime import timedelta

def test_auth():
    """Test authentication and create test user"""
    print("Testing authentication...")
    
    db = SessionLocal()
    try:
        # Check if test user exists
        test_user = db.query(User).filter(User.email == "test@example.com").first()
        
        if not test_user:
            print("Creating test user...")
            # Create test user
            hashed_password = get_password_hash("testpassword123")
            test_user = User(
                email="test@example.com",
                password=hashed_password,
                name="Test User",
                role="USER",
                provider="local",
                email_verified=True
            )
            db.add(test_user)
            db.commit()
            db.refresh(test_user)
            print(f"Created test user with ID: {test_user.id}")
        else:
            print(f"Test user already exists with ID: {test_user.id}")
        
        # Create access token
        access_token_expires = timedelta(minutes=30)
        access_token = create_access_token(
            data={"sub": str(test_user.id)}, expires_delta=access_token_expires
        )
        
        print(f"Access token: {access_token}")
        print(f"User ID: {test_user.id}")
        
        return access_token, test_user.id
        
    finally:
        db.close()

if __name__ == "__main__":
    test_auth() 