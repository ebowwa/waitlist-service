# Waitlist Service

## Overview
This service manages the waitlist functionality, extracted as a standalone module. It handles user registration and waitlist status management.

### Repository Structure

This repository implements a FastAPI-based waitlist microservice. Key components include:

- `src/waitlist_service/main.py` configures the FastAPI app, sets CORS, registers database events, and mounts the waitlist router.
- `src/waitlist_service/router.py` exposes CRUD endpoints for waitlist entries and sends Telegram notifications when a user signs up.
- `src/waitlist_service/db.py` handles asynchronous database setup and supports SQLite or PostgreSQL via the `DATABASE_URL` setting.
- `src/waitlist_service/models.py` defines the `WaitlistEntry` ORM model with fields for name, email, comments, referral source, and timestamps.
- `src/waitlist_service/notifications.py` provides a `TelegramNotifier` used to alert on new signups.
- `src/waitlist_service/events.py` registers startup and shutdown handlers to manage the database connection and notifier lifecycle.
- `src/waitlist_service/state.py` loads environment variables and exposes helper functions for interacting with the `databases.Database` instance.
- Pydantic schemas for waitlist operations live in `src/waitlist_service/schemas`.
- `src/verify_db.py` verifies SQLite and Supabase connections by creating test entries.
- The `tests` directory contains unit tests for the ORM model, Supabase integration, and Telegram notification logic.
- `docker-compose.yml` defines a PostgreSQL service and the waitlist app container; initialization SQL resides in `sql_queries/`.
- `templates/fastapi/` includes example scripts and boilerplate for running a FastAPI project.
- `requirements.txt` lists the service dependencies, while `setup.py` packages the project and defines test extras.

Overall, the service provides a modular waitlist API capable of notifying via Telegram and running in Docker with either PostgreSQL or SQLite backends.

## Features
- User registration for waitlist
- Waitlist position tracking
- Admin management interface
- Flexible database support (SQLite for local development, Supabase for production)

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
```

For local development, SQLite will be used by default. You can configure other database backends by editing the `.env` file.

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
- `DATABASE_URL`: SQLAlchemy database URL (defaults to SQLite for local development)
- `SUPABASE_URL`: Your Supabase project URL (optional, for production)
- `SUPABASE_KEY`: Your Supabase API key (optional, for production)

## Contributing
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License
This project is proprietary and confidential. All rights reserved.
