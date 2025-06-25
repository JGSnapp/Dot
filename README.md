# Dot Telegram Bot

This project provides a minimal example of a Telegram bot that connects
Google's Gemini generative model with [LangGraph](https://github.com/langchain-ai/langgraph).
The bot accepts text messages, documents and images and returns a reply
produced by Gemini. When the reply is too large, the bot sends it back as
a LaTeX file, which can later be converted to other formats (Docx or
PDF). This approach ensures formulas are preserved correctly across
formats.

## Features

- **Telegram integration** using `python-telegram-bot`.
- **Gemini API** access via `google-generativeai`.
- **LangGraph** workflow to preprocess the input (placeholder in code).
- Accepts **text, files and images** from the user.
- Sends responses as **text** or **LaTeX documents** (which can be
  converted to Docx or PDF).
- Large files can be generated over multiple requests, allowing the bot
  to write and verify sections before completion.
- Image search and generation hooks can be added to the LangGraph
  pipeline for richer document creation.

## Installation

1. Install dependencies:

   ```bash
   pip install python-telegram-bot google-generativeai langgraph
   ```

2. Set environment variables:

   - `TELEGRAM_TOKEN` – token for your Telegram bot.
   - `GEMINI_API_KEY` – API key for Google Gemini.

3. Run the bot:

   ```bash
   python -m bot.bot
   ```

## How It Works

1. A user sends a text message, document or image to the bot.
2. The bot downloads the file if present and passes all content to the
   Gemini model through a LangGraph pipeline.
3. Gemini returns a text response. If the text is short, the bot sends it
   directly in the chat. For long responses, the bot packages the text
   into a `.tex` file so formulas are preserved. The user may convert
   this file to Docx or PDF.
4. The agent can create large files in multiple steps. Users may request
   additional sections or corrections, and the bot will continue from the
   previous content.

## Converting LaTeX to Other Formats

Any generated `.tex` files can be converted locally using tools like
`pandoc` or `latexmk`:

```bash
pandoc response.tex -o response.pdf
pandoc response.tex -o response.docx
```

This ensures mathematical notation remains accurate in the final
Document.

## Notes

The provided implementation is intentionally minimal. Integrate LangGraph
and add image search or generation nodes as needed for your specific
workflow.
