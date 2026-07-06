"""
Turns a Markdown-ish answer (the shape Gemini is prompted to produce) into a
nicely formatted PDF using ReportLab, so the user can download their research
result as a standalone document.
"""

import io
import re
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    ListFlowable,
    ListItem,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)

VIOLET = colors.HexColor("#6C5CE7")
INK = colors.HexColor("#1A1F2B")
MUTED = colors.HexColor("#6B6F76")


def _inline_bold(text: str) -> str:
    """Convert **bold** markdown into ReportLab-friendly <b> tags."""
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)


def _build_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="QTitle", fontName="Helvetica-Bold", fontSize=20,
        textColor=VIOLET, spaceAfter=14,
    ))
    styles.add(ParagraphStyle(
        name="QHeading", fontName="Helvetica-Bold", fontSize=13,
        textColor=INK, spaceBefore=14, spaceAfter=6,
    ))
    styles.add(ParagraphStyle(
        name="QBody", fontName="Helvetica", fontSize=10.5,
        textColor=INK, leading=15,
    ))
    styles.add(ParagraphStyle(
        name="QMeta", fontName="Helvetica-Oblique", fontSize=8.5,
        textColor=MUTED, spaceAfter=18,
    ))
    return styles


def markdown_to_pdf_bytes(markdown_text: str, query: str) -> bytes:
    """Render the Markdown answer text to a PDF and return its raw bytes."""
    styles = _build_styles()
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=LETTER,
        topMargin=0.85 * inch, bottomMargin=0.85 * inch,
        leftMargin=0.9 * inch, rightMargin=0.9 * inch,
    )

    story = []
    story.append(Paragraph(
        f"Generated {datetime.now().strftime('%B %d, %Y at %I:%M %p')} &middot; "
        f"Query: \"{query}\"",
        styles["QMeta"],
    ))

    bullet_buffer = []

    def flush_bullets():
        if bullet_buffer:
            items = [ListItem(Paragraph(_inline_bold(b), styles["QBody"]), leftIndent=6)
                     for b in bullet_buffer]
            story.append(ListFlowable(items, bulletType="bullet", start="circle", leftIndent=14))
            story.append(Spacer(1, 8))
            bullet_buffer.clear()

    for raw_line in markdown_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("# "):
            flush_bullets()
            story.append(Paragraph(_inline_bold(line[2:]), styles["QTitle"]))
        elif line.startswith("## "):
            flush_bullets()
            story.append(Paragraph(_inline_bold(line[3:]), styles["QHeading"]))
        elif line.startswith(("- ", "* ")):
            bullet_buffer.append(line[2:])
        elif re.match(r"^\d+\.\s", line):
            bullet_buffer.append(re.sub(r"^\d+\.\s", "", line))
        else:
            flush_bullets()
            story.append(Paragraph(_inline_bold(line), styles["QBody"]))
            story.append(Spacer(1, 4))

    flush_bullets()
    doc.build(story)
    return buffer.getvalue()
