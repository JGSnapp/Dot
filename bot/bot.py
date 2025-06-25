# -*- coding: utf-8 -*-
"""Telegram bot integrated with Gemini API and LangGraph.

This bot receives text, documents and images, processes them using
Google's Gemini generative model via LangGraph and responds with text or
generated files (LaTeX, Docx, PDF). Images can be searched online or
produced using generative services.
"""

import os
from io import BytesIO
from typing import Optional

from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Placeholders for LangGraph and Gemini
try:
    import google.generativeai as genai
    from langgraph.graph import Graph
except Exception:  # pragma: no cover - library may be missing
    genai = None
    Graph = None


TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    await update.message.reply_text("Hi! Send me text or a file and I'll process it with Gemini.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming text, images or files."""
    if not GEMINI_API_KEY:
        await update.message.reply_text("Gemini API key not configured.")
        return

    text: Optional[str] = update.message.text
    file_id = None

    if update.message.document:
        file_id = update.message.document.file_id
    elif update.message.photo:
        file_id = update.message.photo[-1].file_id

    data = None
    if file_id:
        file = await context.bot.get_file(file_id)
        data = await file.download_as_bytearray()

    response = await process_with_gemini(text=text, file_bytes=data)
    await send_response(update, context, response)


async def process_with_gemini(text: Optional[str] = None, file_bytes: Optional[bytes] = None) -> str:
    """Process data with Gemini through LangGraph. Stub implementation."""
    if genai is None:
        return "Gemini libraries not installed."

    genai.configure(api_key=GEMINI_API_KEY)

    prompt = text or ""
    if file_bytes:
        prompt += "\n[File received of size {} bytes]".format(len(file_bytes))

    # Here we would build a LangGraph pipeline to analyze the inputs.
    # For brevity we just send the prompt to the Gemini model directly.
    model = genai.GenerativeModel("gemini-pro")
    result = model.generate_content(prompt)
    return result.text


async def send_response(update: Update, context: ContextTypes.DEFAULT_TYPE, message: str) -> None:
    """Send text or file back to the user."""
    # Simple heuristic: if response length is huge, send as a document
    if len(message) > 4000:
        bio = BytesIO(message.encode("utf-8"))
        bio.name = "response.tex"
        await update.message.reply_document(InputFile(bio))
    else:
        await update.message.reply_text(message)


def main() -> None:
    """Start the bot."""
    if not TELEGRAM_TOKEN:
        raise RuntimeError("TELEGRAM_TOKEN environment variable not set")

    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.ALL, handle_message))

    application.run_polling()


if __name__ == "__main__":  # pragma: no cover
    main()
