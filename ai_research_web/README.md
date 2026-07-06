# Quanta — AI Research Assistant

A single-page research assistant built with Flask + Google Gemini. Ask a
research question, get back a structured report (Definition, Key Points,
Examples, Why It Matters), copy it, or download it as a PDF — with a
working light/dark theme toggle.

This uses Google's **current** official SDK (`google-genai`), a single
lightweight package — no heavyweight ML libraries, no local model downloads,
so setup is quick.

## Setup

### 1. Get a free Gemini API key
Go to **https://aistudio.google.com/app/apikey**, sign in with a Google
account, and click "Create API key." It's free (with rate limits — see
Limitations below).

### 2. Install and configure

```bash
cd ai_research_web
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
```
Open `.env` in a text editor and paste your key in place of `your_api_key_here`:
```
GEMINI_API_KEY=AIzaSy...
```

### 3. Run it

```bash
python app.py
```

Open **http://127.0.0.1:5000** in your browser.

## Project layout

```
ai_research_web/
  app.py                    Flask routes: /, /api/ask, /api/pdf
  utils/
    gemini_client.py        Prompt + Gemini API call
    pdf_generator.py        Markdown -> PDF (ReportLab)
  templates/index.html      Page structure
  static/css/style.css      Theme tokens (dark + light) and layout
  static/js/script.js       Chat logic, theme toggle, copy, PDF download
  requirements.txt
  .env.example
```

## How it works

1. You type a question (or tap a topic chip to pre-fill one).
2. The browser POSTs it to `/api/ask`.
3. Flask sends it to Gemini with a system prompt that asks for a structured
   Markdown report (Definition / Key Points / Examples / Why It Matters).
4. The Markdown is converted to HTML on the server and sent back for display,
   and kept as raw Markdown too (for the Copy and PDF buttons).
5. "Download PDF" posts that same Markdown to `/api/pdf`, which renders it
   into a formatted PDF with ReportLab and streams it back as a file.

## Limitations to know about

- **Free tier rate limits**: as of writing, Gemini 2.5 Flash's free tier is
  limited (roughly 10 requests/minute, 250/day). If you hit a quota error,
  wait a bit, or switch `GEMINI_MODEL` in `.env` to `gemini-2.5-flash-lite`
  for a higher free allowance.
- **Single shared history**: this version doesn't save conversation history
  or support follow-up questions — each question is independent. Good next
  step if you want to extend it (see below).
- **No auth**: anyone with the URL can use it and burn your API quota. Fine
  for local/personal use; add a login before deploying it publicly.

## Ideas to extend

- Add conversation memory so follow-up questions ("explain more about point 2")
  work, by keeping the last few Q&As in a `chat = client.chats.create(...)`
  session instead of one-shot `generate_content` calls.
- Add a history sidebar (store past Q&As in a small SQLite database).
- Stream the answer token-by-token instead of waiting for the full response
  (Gemini supports streaming; pair it with Server-Sent Events in Flask).
- Add source citations by combining this with a live search tool (e.g. the
  arXiv-search version we discussed earlier) so answers link to real papers.
