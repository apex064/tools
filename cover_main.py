#!/usr/bin/env python3
"""
cover.py — Cover letter PDF generator (interactive OR AI/JSON driven).

Usage:
  python cover.py                     # interactive prompts
  python cover.py --defaults          # interactive, pre-filled with sample values
  python cover.py --json data.json    # non-interactive from JSON file
  python cover.py --json-str '{...}'  # non-interactive from JSON string
  cat data.json | python cover.py --json -   # non-interactive from stdin
  python cover.py --json data.json --out /tmp/letter.pdf
  python cover.py --print-schema      # show the JSON schema / example

Exit codes:
  0 success, 2 bad input / missing fields, 1 runtime error.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Callable

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    HRFlowable,
)


# ---------------------------------------------------------------------------
# Field schema — single source of truth for prompts, JSON, and defaults.
# Each field: (key, prompt, default, kind)
#   kind: "str" | "multiline" | "path"
# ---------------------------------------------------------------------------
FIELDS: list[tuple[str, str, str, str]] = [
    ("name",        "Full name (header)",                         "CHIMA CHIDIEBERE SUNDAY", "str"),
    ("tagline",     "Tagline / role line",                        "Full-Stack Software Engineer | Backend & Systems Development", "str"),
    ("contact",     "Contact line (use  •  as separator)",        "Nigeria  •  github.com/apex064  •  apex064.earncentive.com", "str"),
    ("date",        "Date",                                       "31 October 2026", "str"),
    ("recipient",   "Recipient block (use \\n for newlines)",      "Hiring Team\nNomba", "multiline"),
    ("subject",     "Subject line",                               "Application for Site Reliability Engineer", "str"),
    ("salutation",  "Salutation",                                 "Dear Hiring Team,", "str"),
    ("p1",          "Paragraph 1",                                "", "multiline"),
    ("p2",          "Paragraph 2",                                "", "multiline"),
    ("p3",          "Paragraph 3",                                "", "multiline"),
    ("p4",          "Paragraph 4",                                "", "multiline"),
    ("p5",          "Paragraph 5",                                "", "multiline"),
    ("thanks",      "Closing line",                               "Thank you for your time and consideration.", "multiline"),
    ("signoff",     "Sign-off (Yours sincerely,)",                "Yours sincerely,", "str"),
    ("signature",   "Signature name",                             "Chima Chidiebere Sunday", "str"),
    ("footer_left", "Footer left text",                           "APPLICATION — SITE RELIABILITY ENGINEER", "str"),
    ("pdf_title",   "PDF title metadata",                         "Cover Letter - Chima Chidiebere Sunday - Nomba SRE", "str"),
    ("pdf_author",  "PDF author metadata",                        "Chima Chidiebere Sunday", "str"),
    ("path",        "Output PDF path",                            "Chima_Chidiebere_Sunday_Nomba_SRE_Cover_Letter.pdf", "path"),
]

DEFAULTS: dict[str, str] = {
    "name": "CHIMA CHIDIEBERE SUNDAY",
    "tagline": "Full-Stack Software Engineer | Backend & Systems Development",
    "contact": "Nigeria  •  github.com/apex064  •  apex064.earncentive.com",
    "date": "31 October 2026",
    "recipient": "Hiring Team\nNomba",
    "subject": "Application for Site Reliability Engineer",
    "salutation": "Dear Hiring Team,",
    "p1": (
        "I am writing to apply for the Site Reliability Engineer role at Nomba. I am a software engineer "
        "with more than five years of experience building and supporting web, backend, and mobile products. "
        "My work has involved developing production applications, designing APIs and data systems, "
        "troubleshooting service issues, and improving the reliability of the systems behind user-facing "
        "products. I am interested in bringing that practical engineering experience to a fintech platform "
        "operating at Nomba’s scale."
    ),
    "p2": (
        "In my role at Earncentive, I develop and maintain applications across frontend and backend services, "
        "integrate external platforms such as payment gateways, and work through testing, debugging, and "
        "performance issues. I have also worked with Python, Django, Flask, Node.js, PostgreSQL, MySQL, "
        "Redis, and Linux. This combination has given me a useful understanding of how application code, "
        "data stores, integrations, and the underlying runtime environment affect the reliability of a "
        "complete service."
    ),
    "p3": (
        "I have also taken responsibility for building and operating products beyond feature development. "
        "Through my work on FLINK and other applications, I have dealt with backend services, asynchronous "
        "workers, WebSocket-based functionality, deployment processes, server logs, and production "
        "troubleshooting in Linux environments. At Mattys Inc., I led development of a web application "
        "serving more than 100,000 users, built REST APIs with Django REST Framework, improved database "
        "query performance by 40%, and implemented a GitHub Actions CI/CD pipeline. These experiences "
        "have strengthened my ability to investigate failures, identify bottlenecks, and make changes "
        "that improve system behaviour."
    ),
    "p4": (
        "What attracts me to Nomba is the engineering challenge behind dependable financial infrastructure. "
        "When businesses and individuals rely on a platform for payments and everyday financial operations, "
        "availability, security, observability, and disciplined incident response are essential. I would "
        "welcome the opportunity to work closely with your engineering teams to improve operational "
        "visibility, automate repeatable tasks, strengthen deployment practices, and build systems that "
        "remain dependable as usage grows."
    ),
    "p5": (
        "I bring a strong foundation in Python and Linux-based systems, practical experience with databases "
        "and production application support, and a product-minded approach to engineering. I am also "
        "committed to deepening my expertise in formal SRE practices and infrastructure automation. "
        "I would appreciate the opportunity to discuss how my background could contribute to Nomba’s "
        "reliability and infrastructure goals."
    ),
    "thanks": "Thank you for your time and consideration.",
    "signoff": "Yours sincerely,",
    "signature": "Chima Chidiebere Sunday",
    "footer_left": "APPLICATION — SITE RELIABILITY ENGINEER",
    "pdf_title": "Cover Letter - Chima Chidiebere Sunday - Nomba SRE",
    "pdf_author": "Chima Chidiebere Sunday",
    "path": "Chima_Chidiebere_Sunday_Nomba_SRE_Cover_Letter.pdf",
}

# Which paragraph fields are optional (empty -> skipped)
OPTIONAL_PARAGRAPHS = ("p1", "p2", "p3", "p4", "p5")


# ---------------------------------------------------------------------------
# Styling — identical to your original.
# ---------------------------------------------------------------------------
def build_styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    name = ParagraphStyle(
        "Name", parent=base["Normal"],
        fontName="Helvetica-Bold", fontSize=17, leading=20, spaceAfter=2,
    )
    meta = ParagraphStyle(
        "Meta", parent=base["Normal"],
        fontName="Helvetica", fontSize=8.5, leading=12,
        textColor=colors.HexColor("#444444"), spaceAfter=2,
    )
    date = ParagraphStyle("Date", parent=meta, spaceBefore=13, spaceAfter=13)
    subject = ParagraphStyle(
        "Subject", parent=base["Normal"],
        fontName="Helvetica-Bold", fontSize=10, leading=13,
        spaceBefore=3, spaceAfter=11,
    )
    body = ParagraphStyle(
        "Body", parent=base["Normal"],
        fontName="Helvetica", fontSize=9.5, leading=14.2,
        textColor=colors.HexColor("#222222"), spaceAfter=9,
    )
    closing = ParagraphStyle("Closing", parent=body, spaceBefore=2, spaceAfter=2)
    return {
        "name": name, "meta": meta, "date": date, "subject": subject,
        "body": body, "closing": closing,
    }


# ---------------------------------------------------------------------------
# Story builder — takes the field dict, returns platypus flowables.
# ---------------------------------------------------------------------------
def build_story(data: dict[str, str], styles: dict[str, ParagraphStyle]) -> list[Any]:
    # Escape helper: keep user text safe in reportlab's mini-markup.
    def esc(text: str) -> str:
        return (
            text.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
        )

    def inline(text: str) -> str:
        # Turn • separators into non-breaking spaced bullets for the contact line.
        return esc(text).replace("•", "&nbsp;•&nbsp;")

    recipient_html = "<br/>".join(esc(line) for line in data["recipient"].splitlines() if line.strip())

    story: list[Any] = [
        Paragraph(inline(data["name"]), styles["name"]),
        Paragraph(inline(data["tagline"]), styles["meta"]),
        Paragraph(inline(data["contact"]), styles["meta"]),
        Spacer(1, 5),
        HRFlowable(width="100%", thickness=0.8, color=colors.black, spaceBefore=4, spaceAfter=7),
        Paragraph(esc(data["date"]), styles["date"]),
        Paragraph(recipient_html, styles["meta"]),
        Spacer(1, 8),
        Paragraph(esc(data["subject"]), styles["subject"]),
        Paragraph(esc(data["salutation"]), styles["body"]),
    ]

    for key in OPTIONAL_PARAGRAPHS:
        text = (data.get(key) or "").strip()
        if text:
            story.append(Paragraph(esc(text), styles["body"]))

    if data.get("thanks", "").strip():
        story.append(Paragraph(esc(data["thanks"]), styles["body"]))

    story.append(Paragraph(esc(data["signoff"]), styles["closing"]))
    story.append(Spacer(1, 16))
    story.append(Paragraph(f"<b>{esc(data['signature'])}</b>", styles["closing"]))
    return story


# ---------------------------------------------------------------------------
# Footer factory — same visual, driven by config.
# ---------------------------------------------------------------------------
def make_footer(footer_left: str) -> Callable[[Any, Any], None]:
    def footer(canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#BBBBBB"))
        canvas.setLineWidth(0.4)
        canvas.line(22 * mm, 15 * mm, A4[0] - 22 * mm, 15 * mm)
        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(colors.HexColor("#666666"))
        canvas.drawString(22 * mm, 10 * mm, footer_left)
        canvas.drawRightString(A4[0] - 22 * mm, 10 * mm, str(doc.page))
        canvas.restoreState()
    return footer


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------
def resolve_output_path(path: str, cwd: str | None = None) -> str:
    """Expand ~ and make relative to cwd; validate parent dir is writable."""
    cwd = cwd or os.getcwd()
    if path.startswith("~"):
        path = os.path.expanduser(path)
    if not os.path.isabs(path):
        path = os.path.join(cwd, path)
    parent = os.path.dirname(path) or cwd
    if not os.path.isdir(parent):
        raise ValueError(f"Output directory does not exist: {parent!r}")
    if not os.access(parent, os.W_OK):
        raise PermissionError(f"Cannot write to {parent!r}")
    if os.path.isdir(path):
        raise ValueError(f"Output path is a directory: {path!r}")
    return path


def render_pdf(data: dict[str, str], out_override: str | None = None) -> str:
    styles = build_styles()
    story = build_story(data, styles)
    footer = make_footer(data["footer_left"])

    path = resolve_output_path(out_override or data["path"])
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)

    pdf = SimpleDocTemplate(
        path, pagesize=A4,
        rightMargin=22 * mm, leftMargin=22 * mm,
        topMargin=18 * mm, bottomMargin=22 * mm,
        title=data["pdf_title"], author=data["pdf_author"],
    )
    pdf.build(story, onFirstPage=footer, onLaterPages=footer)
    return path


# ---------------------------------------------------------------------------
# Input: interactive prompts
# ---------------------------------------------------------------------------
def _read_multiline() -> str:
    """Read until a blank line. '\\n' escapes are expanded to real newlines."""
    lines: list[str] = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line == "":
            break
        lines.append(line.replace("\\n", "\n"))
    return "\n".join(lines)


def prompt_fields(use_defaults: bool) -> dict[str, str]:
    data: dict[str, str] = {}
    print("Cover Letter Generator — press Enter to accept defaults.\n", file=sys.stderr)
    for key, prompt, default, kind in FIELDS:
        shown_default = (DEFAULTS.get(key, "") if use_defaults else "")
        if kind == "multiline":
            print(f"[{key}] {prompt}")
            if shown_default:
                print(f"  (default: {shown_default!r})")
            print("  (end with a blank line; \\n becomes newline)")
            value = _read_multiline().strip()
            data[key] = value or shown_default
        else:
            hint = f" [{shown_default}]" if shown_default else ""
            try:
                value = input(f"[{key}] {prompt}{hint}: ").strip()
            except EOFError:
                value = ""
            data[key] = value or shown_default
    return data


# ---------------------------------------------------------------------------
# Input: JSON (file / string / stdin)
# ---------------------------------------------------------------------------
def load_json_source(spec: str) -> dict[str, Any]:
    if spec == "-":
        return json.load(sys.stdin)
    if spec.lstrip().startswith("{"):
        return json.loads(spec)
    with open(spec, "r", encoding="utf-8") as f:
        return json.load(f)


def collect_from_json(spec: str) -> dict[str, str]:
    raw = load_json_source(spec)
    if not isinstance(raw, dict):
        raise ValueError("Top-level JSON must be an object.")
    # Merge over DEFAULTS so AI callers can send only what changes.
    data: dict[str, str] = {k: str(v) for k, v in DEFAULTS.items()}
    for k, v in raw.items():
        if k not in DEFAULTS:
            raise ValueError(f"Unknown field in JSON: {k!r}")
        if v is None:
            data[k] = ""
        else:
            data[k] = str(v)
    validate(data)
    return data


def validate(data: dict[str, str]) -> None:
    missing = [
        k for k, *_ in FIELDS
        if k not in OPTIONAL_PARAGRAPHS and k != "path" and not (data.get(k) or "").strip()
    ]
    if not (data.get("path") or "").strip():
        missing.append("path")
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")


# ---------------------------------------------------------------------------
# Schema printer (useful for AI callers)
# ---------------------------------------------------------------------------
def print_schema() -> None:
    schema = {
        "_comment": "Send any subset of these fields via --json. Unknown keys are rejected.",
        "fields": [
            {"key": k, "kind": kind, "required": not (k in OPTIONAL_PARAGRAPHS or k == "path"),
             "default": DEFAULTS.get(k, "")}
            for k, _prompt, _d, kind in FIELDS
        ],
        "example": {k: DEFAULTS[k] for k, *_ in FIELDS},
    }
    json.dump(schema, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate a cover letter PDF.")
    parser.add_argument("--json", metavar="SPEC",
                        help="JSON file path, a JSON object string, or '-' for stdin.")
    parser.add_argument("--json-str", dest="json_str", metavar="JSON",
                        help="Inline JSON object string.")
    parser.add_argument("--out", metavar="PATH", help="Override output PDF path.")
    parser.add_argument("--defaults", action="store_true",
                        help="Interactive mode: pre-fill with sample Nomba values.")
    parser.add_argument("--print-schema", action="store_true",
                        help="Print JSON schema / example and exit.")
    args = parser.parse_args(argv)

    if args.print_schema:
        print_schema()
        return 0

    try:
        if args.json_str:
            data = collect_from_json(args.json_str)
        elif args.json:
            data = collect_from_json(args.json)
        else:
            data = prompt_fields(use_defaults=args.defaults)
            validate(data)

        path = render_pdf(data, out_override=args.out)
        size = os.path.getsize(path)
        print(f"Created: {path} size: {size} bytes")
        return 0
    except (ValueError, PermissionError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2
    except Exception as e:  # pragma: no cover
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
