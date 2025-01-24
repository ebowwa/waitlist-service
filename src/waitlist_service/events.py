from fastapi import FastAPI
import logging
from .db import database
from .notifications import notifier

logger = logging.getLogger(__name__)

def register_db_events(app: FastAPI):
    @app.on_event("startup")
    async def startup():
        # Connect to database
        logger.info("Starting up and connecting to the database")
        try:
            await database.connect()
            logger.info("Successfully connected to the database")
        except Exception as e:
            logger.error(f"Error connecting to database: {e}")
            raise

        # Initialize Telegram notifications
        try:
            # The notifier is already initialized at import, just log its status
            if notifier.enabled:
                logger.info("Telegram notifications are enabled")
                # Send a test message
                await notifier.send_message("🚀 Waitlist service started successfully!")
            else:
                logger.warning("Telegram notifications are disabled - check your environment variables")
        except Exception as e:
            logger.error(f"Error initializing Telegram notifications: {e}")
            # Don't raise here - we can still run without notifications

    @app.on_event("shutdown")
    async def shutdown():
        logger.info("Shutting down services")
        try:
            await database.disconnect()
            await notifier.close()
            logger.info("Successfully shut down all services")
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
            raise
