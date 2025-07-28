from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import time
import logging

# Setup Logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[logging.FileHandler("bot.log"), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Bot Configuration
# TOKEN = "7954557212:AAHfLzKZad3CxklU62yyAo0OQ25sJ9ef8V-"  # Replace with new token from @BotFather
import os
TOKEN = os.getenv("7954557212:AAHfLzKZad3CxklU62yyAo0OQ25sJ9ef8V-")
CHANNEL_ID = "-1002888728398"  # Your private channel ID
UPI_ID = "75204arisiastar@axl"  # Your UPI ID
UPI_NAME = "all upi"  # Your name
UPI_AMOUNT = 49  # Amount in INR

# Generate UPI QR Code URL
def generate_upi_qr(order_id):
    upi_link = f"upi://pay?pa={UPI_ID}&pn={UPI_NAME}&am={UPI_AMOUNT}&cu=INR&tn={order_id}"
    qr_api_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={upi_link}"
    return qr_api_url, upi_link

# Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    order_id = f"ORDER_{user_id}_{int(time.time())}"
    logger.info(f"User {user_id} started with order {order_id}")

    try:
        qr_code_url, upi_link = generate_upi_qr(order_id)
        await update.message.reply_text(
            f"Channel join ke liye ₹{UPI_AMOUNT} pay karo:\nUPI Link: {upi_link}\nYa QR code scan karo:"
        )
        await update.message.reply_photo(qr_code_url)
        await update.message.reply_text(
            f"Payment ke baad transaction ID bhejo: /verify <transaction_id>\nExample: /verify TXN123456789"
        )
    except Exception as e:
        logger.error(f"Error for user {user_id}: {e}")
        await update.message.reply_text(f"Error: {e}\nUPI Link: {upi_link}")

# Verify Command (Sends channel link directly)
async def verify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    transaction_id = context.args[0] if context.args else None
    logger.info(f"User {user_id} submitted transaction ID: {transaction_id}")

    if not transaction_id:
        await update.message.reply_text("Please provide a transaction ID: /verify <transaction_id>")
        return

    try:
        invite_link = await context.bot.create_chat_invite_link(
            chat_id=CHANNEL_ID,
            member_limit=1,
            expire_date=int(time.time()) + 86400
        )
        logger.info(f"Generated link for user {user_id}: {invite_link.invite_link}")
        await update.message.reply_text(f"Join the channel: {invite_link.invite_link}")
    except Exception as e:
        logger.error(f"Invite link error for user {user_id}: {e}")
        await update.message.reply_text(f"Error generating invite link: {e}")

def main():
    try:
        application = Application.builder().token(TOKEN).build()
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("verify", verify))
        logger.info("Bot is starting...")
        application.run_polling(allowed_updates=Update.ALL_TYPES, timeout=30)
    except Exception as e:
        logger.error(f"Bot error: {e}")

if __name__ == "__main__":
    main()