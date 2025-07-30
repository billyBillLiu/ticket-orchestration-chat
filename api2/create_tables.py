#!/usr/bin/env python3
"""
Create database tables if they don't exist
"""
from app.models import engine, Base

def create_tables():
    """Create all database tables"""
    print("Creating database tables...")
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully!")
        
    except Exception as e:
        print(f"Error creating tables: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_tables() 