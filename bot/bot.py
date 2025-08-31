# -*- coding: utf-8 -*-
"""Telegram-бот, интегрированный с Gemini API и LangGraph.

Бот принимает текст, документы и изображения, обрабатывает их с помощью
генеративной модели Gemini от Google через LangGraph и отвечает текстом
или сгенерированными файлами (LaTeX, Docx, PDF). Изображения могут быть
найдены в сети или сгенерированы внешними сервисами.
"""

import os
from io import BytesIO
from typing import Optional

from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Заглушки для LangGraph и Gemini
try:
    import google.generativeai as genai
    from langgraph.graph import Graph
except Exception:  # pragma: no cover - library may be missing
    genai = None
    Graph = None


TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправить сообщение при выполнении команды /start."""
    await update.message.reply_text("Hi! Send me text or a file and I'll process it with Gemini.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработать входящий текст, изображения или файлы."""
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
    """Обработать данные с помощью Gemini через LangGraph. Заглушка-реализация."""
    if genai is None:
        return "Gemini libraries not installed."

    genai.configure(api_key=GEMINI_API_KEY)

    prompt = text or ""
    if file_bytes:
        prompt += "\n[File received of size {} bytes]".format(len(file_bytes))

    # Здесь можно собрать конвейер LangGraph для анализа входных данных.
    # Для краткости напрямую отправляем подсказку в модель Gemini.
    model = genai.GenerativeModel("gemini-pro")
    result = model.generate_content(prompt)
    return result.text


async def send_response(update: Update, context: ContextTypes.DEFAULT_TYPE, message: str) -> None:
    """Отправить пользователю текст или файл."""
    # Простая эвристика: если ответ очень длинный, отправить как документ
    if len(message) > 4000:
        bio = BytesIO(message.encode("utf-8"))
        bio.name = "response.tex"
        await update.message.reply_document(InputFile(bio))
    else:
        await update.message.reply_text(message)


def main() -> None:
    """Запустить бота."""
    if not TELEGRAM_TOKEN:
        raise RuntimeError("TELEGRAM_TOKEN environment variable not set")

    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.ALL, handle_message))

    application.run_polling()


if __name__ == "__main__":  # pragma: no cover
    main()
