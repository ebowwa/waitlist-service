import asyncio
import logging
import pytest
from src.waitlist_service.notifications import notifier

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@pytest.mark.asyncio
async def test_telegram():
    logger.info("Testing Telegram notifications")
    
    if notifier.enabled:
        logger.info("Telegram notifications are enabled")
        await notifier.notify_new_signup(
            email="test@example.com",
            name="Test User",
            referral_source="manual test"
        )
    else:
        logger.warning(
            "Telegram notifications are disabled. Check your environment variables:\n"
            f"TELEGRAM_BOT_TOKEN: {'set' if notifier.TELEGRAM_BOT_TOKEN else 'not set'}\n"
            f"TELEGRAM_CHAT_ID: {'set' if notifier.TELEGRAM_CHAT_ID else 'not set'}"
        )
    
    await notifier.close()

if __name__ == "__main__":
    asyncio.run(test_telegram())
