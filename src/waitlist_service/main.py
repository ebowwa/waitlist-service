from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .router import waitlist_router
from .events import register_db_events

app = FastAPI(
    title="Waitlist Service",
    description="Service for managing waitlist entries",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register database event handlers
register_db_events(app)

# Include the waitlist router
app.include_router(waitlist_router, prefix="/waitlist", tags=["waitlist"])
