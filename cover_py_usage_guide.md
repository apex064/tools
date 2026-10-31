# `cover.py` — Usage Guide

`cover.py` generates a cover letter PDF. It runs **interactively** (prompts for each field) or **non-interactively** (JSON file, JSON string, or stdin) so AI agents and scripts can drive it.

Styling and layout are identical to the original Nomba SRE cover letter.

---

## 1. Requirements

- Python 3.10+
- `reportlab`

```bash
pip install --user reportlab
```

> Do not run with `sudo`. Sudo uses root's Python and won't see packages installed under your user account.

## 2. Quick start

```bash
python cover.py                     # interactive, blank
python cover.py --defaults          # interactive, pre-filled with sample values
python cover.py --json letter.json  # non-interactive (AI / script)
```

Example output:

```text
Created: /home/apex064/jobs/Chima_Chidiebere_Sunday_Nomba_SRE_Cover_Letter.pdf size: 12345 bytes
```

## 3. Command-line options

| Flag | Purpose |
|---|---|
| (none) | Interactive prompts, blank by default |
| `--defaults` | Interactive prompts, pre-filled with sample values |
| `--json SPEC` | Load fields from a JSON file, a JSON string, or `-` for stdin |
| `--json-str JSON` | Load fields from an inline JSON string |
| `--out PATH` | Override the output PDF path |
| `--print-schema` | Print the JSON schema + example and exit |
| `-h`, `--help` | Show help |

### Exit codes

| Code | Meaning |
|---:|---|
| `0` | Success |
| `1` | Unexpected runtime error |
| `2` | Bad input (missing fields, unknown keys, permission denied, invalid path) |

## 4. Interactive mode

```bash
python cover.py --defaults
```

Single-line fields: press Enter to accept the default shown in `[...]`.

Multiline fields: type your text; a blank line ends the field. `\n` inside a line becomes a real newline.

Paths: relative paths resolve against the current working directory. `~` expands to your home directory.

### Example session (abridged)

```text
[name] Full name (header) [CHIMA CHIDIEBERE SUNDAY]: Ada Lovelace
[tagline] Tagline / role line [Full-Stack Software Engineer | ...]: Platform Engineer
[recipient] Recipient block (use \n for newlines)
  (default: 'Hiring Team\nNomba')
  (end with a blank line; \n becomes newline)
Engineering Hiring
Stripe

[subject] Subject line [Application for Site Reliability Engineer]: Application for Platform Engineer
[p1] Paragraph 1
  (end with a blank line; \n becomes newline)
I am applying for the Platform Engineer role...

[path] Output PDF path [Chima_Chidiebere_Sunday_Nomba_SRE_Cover_Letter.pdf]: ada_stripe_cover_letter.pdf
```

## 5. Non-interactive mode (AI / scripts)

### 5.1 From a JSON file

```bash
python cover.py --json letter.json
```

`letter.json` — send only the fields you want to change. Everything else falls back to built-in defaults.

```json
{
  "name": "Ada Lovelace",
  "tagline": "Platform Engineer",
  "recipient": "Engineering Hiring\nStripe",
  "subject": "Application for Platform Engineer",
  "salutation": "Dear Engineering Team,",
  "p1": "I am applying for the Platform Engineer role...",
  "p2": "At Example Co, I ...",
  "thanks": "Thank you for your consideration.",
  "signature": "Ada Lovelace",
  "path": "ada_stripe_cover_letter.pdf"
}
```

### 5.2 From an inline JSON string

```bash
python cover.py --json-str '{"recipient":"Hiring Team\nNomba","p1":"Short intro.","path":"out.pdf"}'
```

### 5.3 From stdin

```bash
echo '{"path":"out.pdf","p1":"Hi."}' | python cover.py --json -
cat letter.json | python cover.py --json -
```

### 5.4 Override output path

`--out` always wins over whatever is in `path`:

```bash
python cover.py --json letter.json --out /tmp/ada.pdf
```

## 6. Field reference

All fields are strings. Use `\n` for newlines inside a single-line field; `recipient` splits on newlines into separate lines.

| Key | Required | Purpose | Default |
|---|:---:|---|---|
| `name` | ✅ | Name in header (bold, 17pt) | `CHIMA CHIDIEBERE SUNDAY` |
| `tagline` | ✅ | Role line under the name | `Full-Stack Software Engineer \| Backend & Systems Development` |
| `contact` | ✅ | Contact line, `•` separators | `Nigeria • github.com/apex064 • apex064.earncentive.com` |
| `date` | ✅ | Date block | `31 October 2026` |
| `recipient` | ✅ | Recipient block (multi-line via `\n`) | `Hiring Team\nNomba` |
| `subject` | ✅ | Subject line (bold) | `Application for Site Reliability Engineer` |
| `salutation` | ✅ | Greeting | `Dear Hiring Team,` |
| `p1` … `p5` | ⬜ | Body paragraphs (empty ones are skipped) | (sample text) |
| `thanks` | ⬜ | Closing thank-you line | `Thank you for your time and consideration.` |
| `signoff` | ✅ | Sign-off | `Yours sincerely,` |
| `signature` | ✅ | Signature name (bold) | `Chima Chidiebere Sunday` |
| `footer_left` | ✅ | Footer left text | `APPLICATION — SITE RELIABILITY ENGINEER` |
| `pdf_title` | ✅ | PDF metadata title | `Cover Letter - Chima Chidiebere Sunday - Nomba SRE` |
| `pdf_author` | ✅ | PDF metadata author | `Chima Chidiebere Sunday` |
| `path` | ⬜ | Output PDF path (relative to CWD) | `Chima_Chidiebere_Sunday_Nomba_SRE_Cover_Letter.pdf` |

### Rules enforced by the tool

- Unknown keys are rejected — typos or unsupported fields fail loudly.
- Required fields cannot be empty (except body paragraphs and `path`).
- The parent directory for `path` must exist and be writable; this is checked before layout work.
- `&`, `<`, and `>` in your text are HTML-escaped automatically. Pass raw text (including LLM output).

Print the schema:

```bash
python cover.py --print-schema
```

## 7. How AI agents should call it

### Recommended pattern

1. Write a JSON file containing only the fields the letter needs.
2. Invoke the tool with `--json` and a path inside a temporary or working directory.
3. Check the exit code:
   - `0`: success
   - `2`: fixable input error
   - `1`: runtime error
4. Read stdout to get the final absolute PDF path (`Created: /abs/path size: N bytes`).

### Minimal workflow

```bash
cat > /tmp/letter.json <<'JSON'
{
  "recipient": "Hiring Team\nNomba",
  "subject": "Application for Site Reliability Engineer",
  "p1": "I am a software engineer with five years ...",
  "p2": "At Earncentive I ...",
  "path": "/tmp/out/nomba_sre.pdf"
}
JSON

python cover.py --json /tmp/letter.json
```

### Tips

- Prefer `--json` over `--json-str` for long text — no shell-quoting headaches.
- Always pass a path you control (e.g. under `/tmp/`).
- Use `--out` to keep the JSON body stable but change the filename per run.
- Retry on exit code `2` — the error message names the offending field(s).
- No TTY required in JSON mode — works from `subprocess.run`, Lambda, cron, etc.
- Never invoke with `sudo`.

## 8. Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `ModuleNotFoundError: No module named 'reportlab'` | Package installed for a different Python (e.g. under `sudo`) | Run `pip install --user reportlab` as your user |
| `PermissionError: Cannot write to '...'` | Output directory is not writable | Pick a writable path (e.g. `~/…` or `./…`) |
| `ValueError: Missing required fields: ...` | A required field is empty | Provide the named field(s) |
| `ValueError: Unknown field in JSON: '...'` | Typo or unsupported key | Use keys from §6 or run `--print-schema` |
| `ValueError: Output path is a directory` | `path` points at a folder | Use a full filename |
| PDF has stray `&amp;` / `&lt;` | Text was already HTML-escaped | Pass raw text — escaping is automatic |
