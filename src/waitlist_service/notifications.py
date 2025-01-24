import os
import logging
from typing import Optional
from aiogram import Bot
import asyncio
from dotenv import load_dotenv

# Configure root logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

class TelegramNotifier:
    def __init__(self):
        self.logger = logger
        self.enabled = False
        self.bot = None
        
        # Load environment variables
        self.TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
        self.TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

        # Validate environment variables
        if not self.TELEGRAM_BOT_TOKEN or not self.TELEGRAM_CHAT_ID:
            self.logger.warning(
                "Telegram notifications disabled: Missing credentials in environment "
                f"(TELEGRAM_BOT_TOKEN={'set' if self.TELEGRAM_BOT_TOKEN else 'not set'}, "
                f"TELEGRAM_CHAT_ID={'set' if self.TELEGRAM_CHAT_ID else 'not set'})"
            )
            return
        
        try:
            self.bot = Bot(token=self.TELEGRAM_BOT_TOKEN)
            self.enabled = True
            self.logger.info("TelegramNotifier initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Telegram bot: {e}")

    async def send_message(self, message: str) -> None:
        if not self.enabled:
            self.logger.info(f"Telegram notifications disabled. Would have sent: {message}")
            return
            
        if not self.bot:
            self.logger.error("Bot not initialized but enabled flag is True")
            return
            
        self.logger.debug(f"Sending Telegram message: {message}")
        try:
            await self.bot.send_message(
                chat_id=self.TELEGRAM_CHAT_ID,
                text=message,
                parse_mode="Markdown"
            )
            self.logger.info("Telegram notification sent successfully")
        except Exception as e:
            self.logger.error(f"Failed to send Telegram notification: {e}")

    async def notify_new_signup(
        self, 
        email: str,
        name: Optional[str] = None,
        referral_source: Optional[str] = None,
        waitlist_type: str = "default"
    ) -> None:
        message = f"🎉 *New Waitlist Signup*\n\n"
        message += f"*Type:* {waitlist_type}\n"
        message += f"*Email:* {email}\n"
        
        if name:
            message += f"*Name:* {name}\n"
        if referral_source:
            message += f"*Source:* {referral_source}"

        await self.send_message(message)

    async def close(self) -> None:
        if self.enabled and self.bot:
            try:
                await self.bot.session.close()
                self.logger.info("Telegram bot session closed")
            except Exception as e:
                self.logger.error(f"Error closing Telegram bot session: {e}")

# Global instance
notifier = TelegramNotifier()
