#!/usr/bin/env python3
"""
Test database connection and tables
"""
from app.models import engine, SessionLocal, User, Conversation, Message
from sqlalchemy import text

def test_database():
    """Test database connection and tables"""
    print("Testing database connection...")
    
    try:
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
            tables = [row[0] for row in result]
            print(f"Available tables: {tables}")
        
        # Test session
        db = SessionLocal()
        try:
            # Try to query users
            users = db.query(User).all()
            print(f"Found {len(users)} users")
            
            # Try to query conversations
            conversations = db.query(Conversation).all()
            print(f"Found {len(conversations)} conversations")
            
            # Try to query messages
            messages = db.query(Message).all()
            print(f"Found {len(messages)} messages")
            
        finally:
            db.close()
            
        print("Database test successful!")
        
    except Exception as e:
        print(f"Database test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_database() 