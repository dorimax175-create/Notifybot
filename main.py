import os
import logging
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, ChatJoinRequestHandler, ContextTypes, CommandHandler, MessageHandler, filters

# Configuration
# Railway automatically sets PORT and RAILWAY_PUBLIC_DOMAIN
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
PORT = int(os.environ.get("PORT", 8080))

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Your custom message text
JOIN_MESSAGE = "Welcome! Please click the link below to verify you are human to continue."

async def handle_join_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles new join requests by sending a private message."""
    request = update.chat_join_request

    # Try to send the user a private message
    try:
        # Note: user_chat_id is used because the user may not have started the bot
        await context.bot.send_message(chat_id=request.user_chat_id, text=JOIN_MESSAGE)
        logger.info(f"Message sent to {request.from_user.id}")
    except Exception as e:
        # If we can't message the user, log it and decline
        logger.error(f"Failed to message {request.from_user.id}: {e}")
        # Auto-decline if we can't verify them
        await context.bot.decline_chat_join_request(
            chat_id=request.chat.id,
            user_id=request.from_user.id
        )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Standard /start command for ad moderation."""
    await update.message.reply_text(
        "Hello! This bot helps manage channel access. Use /help for more info."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Standard /help command for ad moderation."""
    await update.message.reply_text(
        "This bot automatically processes join requests for a private channel."
    )

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Log errors."""
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

def main():
    """Start the bot using webhooks for Railway."""
    # Build the application
    application = ApplicationBuilder().token(TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(ChatJoinRequestHandler(handle_join_request))

    # Error handler
    application.add_error_handler(error_handler)

    # Railway uses webhooks. Set the webhook URL.
    # The URL is derived from Railway's public domain.
    webhook_url = f"https://{os.environ.get('RAILWAY_PUBLIC_DOMAIN')}/{TOKEN}"
    
    logger.info(f"Starting webhook on port {PORT}")

    # Run the webhook server
    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN,
        webhook_url=webhook_url
    )

if __name__ == "__main__":
    main()
