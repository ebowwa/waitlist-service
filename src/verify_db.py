import os
from dotenv import load_dotenv
from src.database import init_db, get_supabase_client
from src.models import WaitlistEntry
from sqlalchemy import create_engine, exc
from sqlalchemy.orm import sessionmaker
from datetime import datetime

def verify_sqlite_connection(db_url: str, environment: str):
    print(f"\nTesting {environment} database connection...")
    print(f"Database URL: {db_url}")
    
    db = None
    try:
        SessionLocal = init_db(db_url)
        db = SessionLocal()
        
        # Create a test entry
        test_entry = WaitlistEntry(
            email=f"test_{environment}@example.com",
            name=f"Test User ({environment})",
            ip_address="127.0.0.1",
            comment="Test entry",
            referral_source="verification_script"
        )
        
        try:
            db.add(test_entry)
            db.commit()
            print("✅ Successfully added new test entry")
        except exc.IntegrityError:
            db.rollback()
            print("ℹ️ Test entry already exists (this is okay)")
        
        # Query the entry
        entries = db.query(WaitlistEntry).all()
        print(f"Found {len(entries)} entries in the database:")
        for entry in entries:
            print(f"- {entry.name} ({entry.email})")
            
        print(f"✅ {environment} database connection successful!")
        
    except Exception as e:
        print(f"❌ Error connecting to {environment} database:")
        print(f"  {str(e)}")
    finally:
        if db is not None:
            db.close()

def verify_supabase_connection():
    print("\nTesting Production Supabase connection...")
    
    try:
        # Get Supabase client
        supabase = get_supabase_client()
        
        # Create a test entry
        test_data = {
            "email": "test_supabase@example.com",
            "name": "Test User (Supabase)",
            "ip_address": "127.0.0.1",
            "comment": "Test entry",
            "referral_source": "verification_script"
        }
        
        try:
            # Insert data
            result = supabase.table('waitlist').insert(test_data).execute()
            print("✅ Successfully added new test entry")
        except Exception as e:
            if "duplicate key value" in str(e):
                print("ℹ️ Test entry already exists (this is okay)")
            else:
                raise
        
        # Query data
        result = supabase.table('waitlist').select("*").execute()
        entries = result.data
        
        print(f"Found {len(entries)} entries in the database:")
        for entry in entries:
            print(f"- {entry['name']} ({entry['email']})")
            
        print("✅ Production Supabase connection successful!")
        
    except Exception as e:
        print(f"❌ Error connecting to Production Supabase:")
        print(f"  {str(e)}")

def verify_all_databases():
    # Load environment variables
    load_dotenv()
    
    # Test in-memory SQLite (for tests)
    memory_url = "sqlite:///:memory:"
    verify_sqlite_connection(memory_url, "In-memory SQLite")
    
    # Test file-based SQLite (for development)
    dev_url = "sqlite:///instance/waitlist.db"
    verify_sqlite_connection(dev_url, "Development SQLite")
    
    # Test Supabase (for production)
    verify_supabase_connection()

if __name__ == "__main__":
    verify_all_databases()
