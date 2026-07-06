"""
Quanta -- AI Research Assistant (Flask + Gemini).

A single-page research assistant: ask a question, get a structured Markdown
report back from Gemini, rendered as a formatted answer with a downloadable
PDF and a copy-to-clipboard button.

Run:
    python app.py
Then open http://127.0.0.1:5000
"""

import markdown as md_lib
from dotenv import load_dotenv
from flask import Flask, Response, jsonify, render_template, request

load_dotenv()

from utils.gemini_client import ask_gemini  # noqa: E402  (after load_dotenv)
from utils.pdf_generator import markdown_to_pdf_bytes  # noqa: E402

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/ask", methods=["POST"])
def ask():
    data = request.get_json(silent=True) or {}
    query = (data.get("query") or "").strip()
    if not query:
        return jsonify({"error": "Please enter a question first."}), 400
    if len(query) > 2000:
        return jsonify({"error": "That question is too long. Try to keep it under 2000 characters."}), 400

    try:
        answer_markdown = ask_gemini(query)
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"Something went wrong reaching Gemini: {e}"}), 502

    answer_html = md_lib.markdown(answer_markdown, extensions=["fenced_code", "tables"])
    return jsonify({"markdown": answer_markdown, "html": answer_html, "query": query})


@app.route("/api/pdf", methods=["POST"])
def pdf():
    data = request.get_json(silent=True) or {}
    markdown_text = (data.get("markdown") or "").strip()
    query = (data.get("query") or "Research Report").strip()
    if not markdown_text:
        return jsonify({"error": "No answer to export yet."}), 400

    try:
        pdf_bytes = markdown_to_pdf_bytes(markdown_text, query)
    except Exception as e:
        return jsonify({"error": f"Could not generate PDF: {e}"}), 500

    safe_name = "".join(c for c in query[:40] if c.isalnum() or c in " _-").strip() or "research-report"
    return Response(
        pdf_bytes,
        mimetype="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{safe_name}.pdf"'},
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
