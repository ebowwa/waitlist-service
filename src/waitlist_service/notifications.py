import os
import logging
from typing import Optional
from aiogram import Bot
import asyncio
from dotenv import load_dotenv

load_dotenv()

class TelegramNotifier:
    def __init__(self):
        # Initialize logger
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        )
        handler.setFormatter(formatter)
        if not self.logger.handlers:
            self.logger.addHandler(handler)

        # Load environment variables
        self.TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
        self.TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

        # Validate environment variables
        if not self.TELEGRAM_BOT_TOKEN or not self.TELEGRAM_CHAT_ID:
            self.logger.warning("Telegram credentials not set. Notifications will be disabled.")
            self.enabled = False
            return
        
        self.enabled = True
        # Initialize the bot
        self.bot = Bot(token=self.TELEGRAM_BOT_TOKEN)
        self.logger.info("TelegramNotifier initialized successfully.")

    async def send_message(self, message: str) -> None:
        if not self.enabled:
            self.logger.info("Telegram notifications disabled. Skipping message.")
            return
            
        self.logger.debug(f"Sending Telegram message: {message}")
        try:
            await self.bot.send_message(
                chat_id=self.TELEGRAM_CHAT_ID,
                text=message,
                parse_mode="Markdown"
            )
            self.logger.info("Telegram notification sent successfully.")
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
        if self.enabled:
            await self.bot.session.close()

# Global instance
notifier = TelegramNotifier()
