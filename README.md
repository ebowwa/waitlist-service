# Waitlist Service

## Overview
This service manages the waitlist functionality for CaringMind, extracted from the monorepo as part of the modularization effort. It handles user registration, waitlist status management, and notifications.

## Features
- User registration for waitlist
- Waitlist position tracking
- Status updates and notifications
- Admin management interface
- Integration with Supabase for data storage

## Installation

### Prerequisites
- Python 3.8+
- pip
- virtualenv (recommended)

### Setup
```bash
# Clone the repository
git clone https://github.com/ebowwa/waitlist-service.git
cd waitlist-service

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your credentials
```

## Usage Examples

### Register a New User
```python
from waitlist_service.models import Waitlist
from waitlist_service.database import Session

def register_user(email, name):
    with Session() as session:
        waitlist_entry = Waitlist(
            email=email,
            name=name,
            status="pending"
        )
        session.add(waitlist_entry)
        session.commit()
        return waitlist_entry.id
```

### Check Waitlist Position
```python
def get_position(email):
    with Session() as session:
        entry = session.query(Waitlist).filter_by(email=email).first()
        if entry:
            position = session.query(Waitlist).filter(
                Waitlist.created_at < entry.created_at
            ).count()
            return position + 1
    return None
```

## API Endpoints

### POST /waitlist/register
Register a new user to the waitlist
```json
{
    "email": "user@example.com",
    "name": "John Doe"
}
```

### GET /waitlist/status/{email}
Get current waitlist status and position
```json
{
    "status": "pending",
    "position": 42
}
```

## Development

### Running Tests
```bash
pytest
```

### Database Migrations
```bash
# Create a new migration
alembic revision --autogenerate -m "description"

# Run migrations
alembic upgrade head
```

## Environment Variables
Required environment variables:
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_KEY`: Your Supabase API key
- `DATABASE_URL`: SQLAlchemy database URL

## Contributing
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License
This project is proprietary and confidential. All rights reserved.
