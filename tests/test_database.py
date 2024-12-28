import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from waitlist_service import Base, get_supabase_client, WaitlistEntry

@pytest.fixture
def test_db():
    """Create a test database session."""
    # Use SQLite in-memory database for testing
    engine = create_engine("sqlite:///:memory:")
    
    # Create tables
    Base.metadata.create_all(engine)
    
    # Create session factory
    TestingSessionLocal = sessionmaker(bind=engine)
    
    # Create a test session
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        # Drop all tables after tests
        Base.metadata.drop_all(engine)

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
    
    # Add and commit
    test_db.add(entry)
    test_db.commit()
    
    # Query the entry
    db_entry = test_db.query(WaitlistEntry).filter(WaitlistEntry.email == "test@example.com").first()
    
    # Verify the entry
    assert db_entry is not None
    assert db_entry.name == "Test User"
    assert db_entry.email == "test@example.com"
    assert db_entry.ip_address == "127.0.0.1"
    assert db_entry.comment == "Test comment"
    assert db_entry.referral_source == "test"
    assert db_entry.is_active is True

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
    
    # Should raise an IntegrityError
    with pytest.raises(Exception) as excinfo:
        test_db.commit()
    assert "UNIQUE constraint failed" in str(excinfo.value)

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
    assert db_entry.is_active is True

def test_supabase_connection(supabase_client):
    """Test Supabase connection"""
    assert supabase_client is not None
