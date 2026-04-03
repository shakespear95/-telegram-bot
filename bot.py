import io
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

from cv_generator import generate_cv_pdf
from job_search import execute_search, execute_get_details
from profile import PROFILE

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-20250514")
MAX_HISTORY = int(os.environ.get("MAX_HISTORY", "20"))
_BASE_PROMPT = os.environ.get(
    "SYSTEM_PROMPT",
    "You are a helpful AI job-hunting assistant on Telegram. Be concise and friendly. "
    "You can:\n"
    "1. SEARCH for job offers using the search_jobs tool — when the user asks to find "
    "jobs, look for positions, or search for openings in a specific field/location.\n"
    "2. GET DETAILS about a specific job posting using the get_job_details tool — "
    "fetch the full description from any job URL.\n"
    "3. GENERATE tailored CV/resume PDFs using the generate_cv_pdf tool — "
    "customised for the specific job the user wants to apply to.\n\n"
    "WORKFLOW: When the user wants to apply, first search for jobs, present the "
    "results as a numbered list with company, title, and link. When they pick one, "
    "fetch the full details, then offer to generate a tailored CV. Use the candidate "
    "profile below to generate CVs without asking for information already known.",
)
SYSTEM_PROMPT = f"{_BASE_PROMPT}\n\n{PROFILE}"

claude = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# Per-user conversation history: {user_id: [{"role": ..., "content": ...}]}
conversations: dict[int, list[dict]] = defaultdict(list)

TOOLS = [
    {
        "name": "generate_cv_pdf",
        "description": (
            "Generate a professional CV/resume as a PDF document. "
            "Use this tool whenever the user wants a CV, resume, or professional "
            "profile as a PDF file. Collect information through conversation first, "
            "then call this tool with the gathered details."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Full name of the person",
                },
                "contact": {
                    "type": "object",
                    "properties": {
                        "email": {"type": "string"},
                        "phone": {"type": "string"},
                        "location": {"type": "string"},
                        "linkedin": {"type": "string"},
                        "website": {"type": "string"},
                    },
                },
                "summary": {
                    "type": "string",
                    "description": "Professional summary or career objective",
                },
                "experience": {
                    "type": "array",
                    "description": "Work experience, most recent first",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "company": {"type": "string"},
                            "dates": {"type": "string"},
                            "location": {"type": "string"},
                            "highlights": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Key achievements and responsibilities",
                            },
                        },
                        "required": ["title", "company"],
                    },
                },
                "education": {
                    "type": "array",
                    "description": "Education, most recent first",
                    "items": {
                        "type": "object",
                        "properties": {
                            "degree": {"type": "string"},
                            "institution": {"type": "string"},
                            "dates": {"type": "string"},
                            "details": {"type": "string"},
                        },
                        "required": ["degree", "institution"],
                    },
                },
                "skills": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of professional skills",
                },
                "sections": {
                    "type": "array",
                    "description": "Additional sections (certifications, languages, etc.)",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "items": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                        },
                        "required": ["title", "items"],
                    },
                },
            },
            "required": ["name"],
        },
    },
    {
        "name": "search_jobs",
        "description": (
            "Search for job offers and listings online. Use this when the user "
            "asks to find jobs, look for positions, search for openings, or find "
            "companies hiring in a specific field and/or location. Returns a list "
            "of job postings with titles, URLs, and snippets."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": (
                        "Job search query — the role, field, or keywords "
                        "(e.g. 'datacenter engineer', 'IT support', 'network admin')"
                    ),
                },
                "location": {
                    "type": "string",
                    "description": (
                        "City, region, or country to search in "
                        "(e.g. 'Stuttgart', 'Berlin Germany', 'Switzerland')"
                    ),
                },
                "num_results": {
                    "type": "integer",
                    "description": "Number of results to return (default 10, max 25)",
                    "default": 10,
                },
            },
            "required": ["query", "location"],
        },
    },
    {
        "name": "get_job_details",
        "description": (
            "Fetch the full content of a job posting from its URL. Use this when "
            "the user wants more details about a specific job listing, or when you "
            "need the full job description to tailor a CV for an application."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The URL of the job posting to fetch details from",
                },
            },
            "required": ["url"],
        },
    },
]


def trim_history(user_id: int) -> list[dict]:
    """Keep conversation history within limits."""
    history = conversations[user_id]
    if len(history) > MAX_HISTORY:
        conversations[user_id] = history[-MAX_HISTORY:]
    return conversations[user_id]


def _serialize_content(content_blocks) -> list[dict]:
    """Convert API response content blocks to serializable dicts."""
    result = []
    for block in content_blocks:
        if block.type == "text":
            result.append({"type": "text", "text": block.text})
        elif block.type == "tool_use":
            result.append({
                "type": "tool_use",
                "id": block.id,
                "name": block.name,
                "input": block.input,
            })
    return result


def _extract_text(content_blocks) -> str:
    """Extract text from response content blocks."""
    parts = []
    for block in content_blocks:
        if hasattr(block, "text"):
            parts.append(block.text)
    return "\n".join(parts)


def _execute_tool(name: str, tool_input: dict) -> tuple[str, bytes | None, str | None]:
    """Execute a tool call. Returns (result_text, file_bytes, filename)."""
    if name == "generate_cv_pdf":
        pdf_bytes, filename = generate_cv_pdf(tool_input)
        return "PDF generated successfully.", pdf_bytes, filename
    if name == "search_jobs":
        return execute_search(tool_input), None, None
    if name == "get_job_details":
        return execute_get_details(tool_input), None, None
    return f"Unknown tool: {name}", None, None


async def _send_text(message, text: str) -> None:
    """Send text, splitting if over Telegram's 4096 char limit."""
    if not text:
        return
    if len(text) <= 4096:
        await message.reply_text(text)
    else:
        for i in range(0, len(text), 4096):
            await message.reply_text(text[i : i + 4096])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command."""
    user = update.effective_user
    conversations[user.id] = []
    await update.message.reply_text(
        f"Hi {user.first_name}! I'm your AI job-hunting assistant.\n\n"
        "Here's what I can do:\n"
        "- Search for job offers (e.g. 'Find datacenter jobs in Stuttgart')\n"
        "- Get details about specific job postings\n"
        "- Generate tailored CVs for applications\n\n"
        "Just tell me what role and location you're interested in!\n"
        "Use /clear to reset our conversation."
    )


async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /clear command - reset conversation history."""
    conversations[update.effective_user.id] = []
    await update.message.reply_text("Conversation cleared. Fresh start!")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming text messages with tool use support."""
    user_id = update.effective_user.id
    user_message = update.message.text

    if not user_message:
        return

    conversations[user_id].append({"role": "user", "content": user_message})
    history = trim_history(user_id)

    file_to_send = None  # (bytes, filename)

    try:
        response = claude.messages.create(
            model=MODEL,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            messages=history,
            tools=TOOLS,
        )

        # Tool use loop - Claude may call tools before giving a final response
        while response.stop_reason == "tool_use":
            conversations[user_id].append({
                "role": "assistant",
                "content": _serialize_content(response.content),
            })

            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    try:
                        result_text, file_bytes, filename = _execute_tool(
                            block.name, block.input,
                        )
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result_text,
                        })
                        if file_bytes:
                            file_to_send = (file_bytes, filename)
                    except Exception as e:
                        logger.error("Tool error (%s): %s", block.name, e)
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": f"Error: {e}",
                            "is_error": True,
                        })

            conversations[user_id].append({
                "role": "user",
                "content": tool_results,
            })
            history = trim_history(user_id)

            response = claude.messages.create(
                model=MODEL,
                max_tokens=4096,
                system=SYSTEM_PROMPT,
                messages=history,
                tools=TOOLS,
            )

        # Store final response
        conversations[user_id].append({
            "role": "assistant",
            "content": _serialize_content(response.content),
        })

        # Send text
        assistant_text = _extract_text(response.content)
        await _send_text(update.message, assistant_text)

        # Send file if a tool generated one
        if file_to_send:
            file_bytes, filename = file_to_send
            doc = io.BytesIO(file_bytes)
            doc.name = filename
            await update.message.reply_document(document=doc, filename=filename)

    except anthropic.APIError as e:
        logger.error("Claude API error: %s", e)
        await update.message.reply_text(
            "Sorry, I'm having trouble connecting right now. Try again in a moment."
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
