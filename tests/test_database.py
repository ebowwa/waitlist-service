import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from src.database import Base, get_supabase_client
from src.models import WaitlistEntry
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables at module level
load_dotenv()

@pytest.fixture
def test_db():
    """SQLite test database fixture"""
    # Use SQLite in-memory database for testing
    SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def supabase_client():
    """Supabase client fixture"""
    if not os.getenv("SUPABASE_URL") or not os.getenv("SUPABASE_KEY"):
        pytest.skip("Supabase credentials not found")
    return get_supabase_client()

def test_create_waitlist_entry(test_db):
    """Test basic waitlist entry creation"""
    # Create a test entry
    entry = WaitlistEntry(
        email="test@example.com",
        name="Test User",
        ip_address="127.0.0.1",
        comment="Test comment",
        referral_source="test"
    )
    test_db.add(entry)
    test_db.commit()
    
    # Query the entry
    db_entry = test_db.query(WaitlistEntry).filter(WaitlistEntry.email == "test@example.com").first()
    assert db_entry is not None
    assert db_entry.name == "Test User"
    assert db_entry.ip_address == "127.0.0.1"
    assert db_entry.comment == "Test comment"
    assert db_entry.referral_source == "test"

def test_duplicate_email(test_db):
    """Test that duplicate emails are not allowed"""
    # Create first entry
    entry1 = WaitlistEntry(
        email="duplicate@example.com",
        name="First User",
        ip_address="127.0.0.1"
    )
    test_db.add(entry1)
    test_db.commit()
    
    # Try to create second entry with same email
    entry2 = WaitlistEntry(
        email="duplicate@example.com",
        name="Second User",
        ip_address="127.0.0.2"
    )
    test_db.add(entry2)
    
    # Should raise IntegrityError
    with pytest.raises(IntegrityError):
        test_db.commit()

def test_optional_fields(test_db):
    """Test that optional fields can be null"""
    # Create entry with minimal fields
    entry = WaitlistEntry(
        email="minimal@example.com",
        name="Minimal User"
    )
    test_db.add(entry)
    test_db.commit()
    
    # Query the entry
    db_entry = test_db.query(WaitlistEntry).filter(WaitlistEntry.email == "minimal@example.com").first()
    assert db_entry is not None
    assert db_entry.name == "Minimal User"
    assert db_entry.ip_address is None
    assert db_entry.comment is None
    assert db_entry.referral_source is None

def test_supabase_connection(supabase_client):
    """Test Supabase connection"""
    # Create test entry with unique email
    test_data = {
        "email": f"test_supabase_{datetime.now().timestamp()}@example.com",
        "name": "Test Supabase User",
        "ip_address": "127.0.0.1",
        "comment": "Supabase test",
        "referral_source": "pytest"
    }
    
    # Insert data
    result = supabase_client.table('waitlist').insert(test_data).execute()
    assert result.data is not None, "Failed to insert data into Supabase"
    inserted_id = result.data[0]['id']
    
    # Query the inserted data
    result = supabase_client.table('waitlist').select("*").eq('id', inserted_id).execute()
    assert len(result.data) == 1, "Failed to retrieve inserted data"
    
    entry = result.data[0]
    assert entry['name'] == test_data['name']
    assert entry['email'] == test_data['email']
    assert entry['ip_address'] == test_data['ip_address']
    assert entry['comment'] == test_data['comment']
    assert entry['referral_source'] == test_data['referral_source']
