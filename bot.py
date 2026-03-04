import os
import logging
from collections import defaultdict

import anthropic
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-20250514")
MAX_HISTORY = int(os.environ.get("MAX_HISTORY", "20"))
SYSTEM_PROMPT = os.environ.get(
    "SYSTEM_PROMPT",
    "You are a helpful AI assistant on Telegram. Be concise and friendly.",
)

claude = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# Per-user conversation history: {user_id: [{"role": ..., "content": ...}]}
conversations: dict[int, list[dict]] = defaultdict(list)


def trim_history(user_id: int) -> list[dict]:
    """Keep conversation history within limits."""
    history = conversations[user_id]
    if len(history) > MAX_HISTORY:
        conversations[user_id] = history[-MAX_HISTORY:]
    return conversations[user_id]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command."""
    user = update.effective_user
    conversations[user.id] = []
    await update.message.reply_text(
        f"Hi {user.first_name}! I'm an AI assistant powered by Claude.\n\n"
        "Send me any message and I'll respond.\n"
        "Use /clear to reset our conversation."
    )


async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /clear command - reset conversation history."""
    user_id = update.effective_user.id
    conversations[user_id] = []
    await update.message.reply_text("Conversation cleared. Fresh start!")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming text messages."""
    user_id = update.effective_user.id
    user_message = update.message.text

    if not user_message:
        return

    conversations[user_id].append({"role": "user", "content": user_message})
    history = trim_history(user_id)

    try:
        response = claude.messages.create(
            model=MODEL,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=history,
        )
        assistant_text = response.content[0].text
        conversations[user_id].append({"role": "assistant", "content": assistant_text})

        # Telegram has a 4096 char limit per message
        if len(assistant_text) <= 4096:
            await update.message.reply_text(assistant_text)
        else:
            for i in range(0, len(assistant_text), 4096):
                await update.message.reply_text(assistant_text[i : i + 4096])

    except anthropic.APIError as e:
        logger.error("Claude API error: %s", e)
        await update.message.reply_text(
            "Sorry, I'm having trouble connecting to my brain. Try again in a moment."
        )
    except Exception as e:
        logger.error("Unexpected error: %s", e)
        await update.message.reply_text("Something went wrong. Please try again.")


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors."""
    logger.error("Exception while handling update: %s", context.error)


def main() -> None:
    """Start the bot."""
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("clear", clear))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error_handler)

    logger.info("Bot started. Polling for updates...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
