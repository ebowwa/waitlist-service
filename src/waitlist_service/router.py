# backend/route/website_services/waitlist_router.py

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Request, status
from datetime import datetime
import logging

from sqlalchemy.exc import IntegrityError

# Import the database components from the db module
from .database import Base
from .db import database, metadata as waitlist_table

# Import Pydantic models from schemas
from .schemas.waitlist import WaitlistEntry, WaitlistCreate, WaitlistUpdate

# Configure logging
logger = logging.getLogger(__name__)

# Initialize the router
router = APIRouter(prefix="/waitlist", tags=["Waitlist CRUD"])

# Initialize a global variable for the TelegramNotifier
notifier = None  # We'll initialize this later when we have the utils module

# CRUD Endpoints

@router.post(
    "/",
    response_model=WaitlistEntry,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new waitlist entry",
)
async def create_entry(entry: WaitlistCreate, request: Request):
    """
    Create a new waitlist entry with the provided name, email, comment, and optional referral_source.
    The client's IP address is recorded from the request headers.
    """
    logger.info(f"Creating entry: {entry.dict()}")

    # Extract client IP
    ip_address = request.headers.get("X-Forwarded-For")
    if ip_address:
        ip_address = ip_address.split(",")[0].strip()
    else:
        ip_address = request.client.host
    logger.info(f"Client IP address: {ip_address}")

    # Insert the new entry, including the comment and referral_source
    query = waitlist_table.insert().values(
        name=entry.name,
        email=entry.email,
        ip_address=ip_address,
        comment=entry.comment,
        referral_source=entry.referral_source,  # Include referral_source
    )
    try:
        last_record_id = await database.execute(query)
        logger.info(f"Inserted entry with ID: {last_record_id}")
    except IntegrityError:
        logger.error(f"IntegrityError: Email {entry.email} already exists.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An entry with this email already exists.",
        )
    except Exception as e:
        logger.error(f"Unexpected error during insertion: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred.",
        )

    # Retrieve the created entry
    query = waitlist_table.select().where(waitlist_table.c.id == last_record_id)
    new_entry = await database.fetch_one(query)
    logger.info(f"New entry retrieved: {new_entry}")

    return new_entry


@router.get(
    "/{entry_id}",
    response_model=WaitlistEntry,
    summary="Retrieve a waitlist entry by ID",
)
async def get_entry(entry_id: int):
    """
    Retrieve a specific waitlist entry by its ID.
    """
    logger.info(f"Retrieving entry with ID: {entry_id}")
    query = waitlist_table.select().where(waitlist_table.c.id == entry_id)
    entry = await database.fetch_one(query)
    if entry is None:
        logger.warning(f"Entry with ID {entry_id} not found.")
        raise HTTPException(status_code=404, detail="Entry not found")
    logger.info(f"Entry found: {entry}")
    return entry


# TODO: DUE TO THE notifications with telegram we no longer need to make the list accessible via post requests i believe, its highly unsafe and bad user usage
@router.get(
    "/", response_model=List[WaitlistEntry], summary="List all waitlist entries"
)
async def list_entries():
    """
    Retrieve all waitlist entries, ordered by creation date descending.
    """
    logger.info("Listing all waitlist entries.")
    query = waitlist_table.select().order_by(waitlist_table.c.created_at.desc())
    entries = await database.fetch_all(query)
    logger.info(f"Number of entries retrieved: {len(entries)}")
    return entries


@router.put(
    "/{entry_id}", response_model=WaitlistEntry, summary="Update a waitlist entry by ID"
)
async def update_entry(entry_id: int, entry: WaitlistUpdate):
    """
    Update an existing waitlist entry's name, email, comment, and/or referral_source.
    Only provided fields will be updated.
    """
    logger.info(f"Updating entry ID {entry_id} with data: {entry.dict(exclude_unset=True)}")

    # Prepare the update data, including the comment and referral_source
    update_data = {k: v for k, v in entry.dict().items() if v is not None}
    if not update_data:
        logger.warning("No fields provided for update.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update.",
        )

    # Execute the update
    query = (
        waitlist_table.update()
        .where(waitlist_table.c.id == entry_id)
        .values(**update_data)
    )
    try:
        await database.execute(query)
        logger.info(f"Entry ID {entry_id} updated successfully.")
    except IntegrityError:
        logger.error(f"IntegrityError: Email {entry.email} already exists.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An entry with this email already exists.",
        )
    except Exception as e:
        logger.error(f"Unexpected error during update: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred.",
        )

    # Fetch the updated entry
    query = waitlist_table.select().where(waitlist_table.c.id == entry_id)
    updated_entry = await database.fetch_one(query)
    if updated_entry is None:
        logger.warning(f"Entry with ID {entry_id} not found after update.")
        raise HTTPException(status_code=404, detail="Entry not found")
    logger.info(f"Updated entry retrieved: {updated_entry}")

    return updated_entry


@router.delete(
    "/{entry_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a waitlist entry by ID",
)
async def delete_entry(entry_id: int):
    """
    Delete a waitlist entry by its ID.
    """
    logger.info(f"Deleting entry with ID: {entry_id}")

    # Check if the entry exists
    query = waitlist_table.select().where(waitlist_table.c.id == entry_id)
    entry = await database.fetch_one(query)
    if entry is None:
        logger.warning(f"Entry with ID {entry_id} not found for deletion.")
        raise HTTPException(status_code=404, detail="Entry not found")

    # Perform the deletion
    delete_query = waitlist_table.delete().where(waitlist_table.c.id == entry_id)
    try:
        await database.execute(delete_query)
        logger.info(f"Entry ID {entry_id} deleted successfully.")
    except Exception as e:
        logger.error(f"Unexpected error during deletion: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred.",
        )
    return {"message": "Entry deleted successfully", "entry_id": entry_id}


# Event handlers to connect/disconnect the database and initialize/close the TelegramNotifier

@router.on_event("startup")
async def startup():
    logger.info("Starting up and connecting to the database.")
    try:
        await database.connect()
        logger.info("Database connected successfully.")
    except Exception as e:
        logger.error(f"Error connecting to the database: {e}")
        raise


@router.on_event("shutdown")
async def shutdown():
    logger.info("Shutting down and disconnecting from the database.")
    try:
        await database.disconnect()
        logger.info("Database disconnected successfully.")
    except Exception as e:
        logger.error(f"Error disconnecting from the database: {e}")
