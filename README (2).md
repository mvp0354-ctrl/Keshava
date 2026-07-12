# Keshava Online Compiler (Web IDE)

A browser-based IDE for Keshava: a Monaco code editor on the left,
and a tabbed console (Console / Tokens / AST / Keywords) on the
right, backed by a small Flask API that runs your program through
the real lexer → parser → interpreter pipeline.

```
Browser
   │  Monaco editor (syntax highlighting for Keshava keywords)
   ▼
POST /api/run  { "code": "..." }
   ▼
Flask server
   │
   ├── lexer.py        source → tokens
   ├── parser.py        tokens → AST
   └── interpreter.py   AST → output (stdout captured)
   ▼
JSON { tokens, ast, output, error, stage }
   ▼
Browser renders Console / Tokens / AST tabs
```

## Setup

```bash
cd Keshava/webapp
pip install -r requirements.txt
python app.py
```

Then open **http://127.0.0.1:5000** in your browser.

## Project structure

```
webapp/
├── app.py               # Flask server + /api/run endpoint
├── requirements.txt
├── Keshava/              # your language implementation, untouched
│   ├── tokens.py
│   ├── lexer.py
│   ├── parser.py
│   ├── interpreter.py
│   └── ast_nodes.py
├── templates/
│   └── index.html         # page shell, loads Monaco from a CDN
└── static/
    ├── style.css           # dark theme, marigold accent
    └── script.js            # editor setup, tabs, Run/Reset logic
```

## How it works

- **Editor pane**: a Monaco editor instance with a custom `Keshava`
  Monarch tokenizer, so keywords (`Aarambha`, `Yadi`, `Likha`, ...),
  strings, numbers, and comments are colored distinctly. A matching
  custom theme (`Keshava-dark`) styles the editor to match the rest
  of the page.
- **Run button** (or `Ctrl`/`Cmd`+`Enter`): sends the current editor
  contents as JSON to `POST /api/run`.
- **Backend** (`app.py`):
  1. Runs `lexer.lexer(code)`. A failure here is reported as a
     `"lexer"`-stage error.
  2. Feeds the tokens into `parser.Parser(...).parse()`. A failure
     here is reported as a `"parser"`-stage error, but the token
     list is still returned so you can inspect it in the Tokens tab.
  3. Runs the resulting AST through `interpreter.Interpreter` on a
     worker thread, with `stdout` captured via
     `contextlib.redirect_stdout`. This step has a 5-second timeout
     (`EXECUTION_TIMEOUT_SECONDS` in `app.py`) so an infinite
     `Yaavat` loop can't hang the server — it comes back as a
     `"runtime"`-stage error instead.
- **Console tab**: shows captured program output, or the error
  message with which stage it came from.
- **Tokens tab**: shows the flat token stream as `(kind, value)`
  pairs.
- **AST tab**: shows an indented text dump of the parsed AST
  (built by a small generic `dump_ast()` helper in `app.py` that
  walks each node's `__dict__`, so it stays in sync automatically if
  you add new AST node types).
- **Keywords tab**: a static cheat-sheet of the Keshava keyword
  table.

## Notes & limitations

- The Flask dev server (`app.run(debug=True)`) is fine for local use
  but isn't meant for production — use something like `gunicorn` if
  you ever deploy this publicly.
- The 5-second execution timeout runs the interpreter in a background
  thread and gives up waiting on it — it does **not** forcibly kill a
  truly stuck thread (Python has no safe way to do that). For a
  student/demo project this is an acceptable tradeoff; a stray thread
  from a rare infinite-loop submission will just die with the process.
- `Punah` (for) and `Grahana` (input) are highlighted by the editor as
  keywords but, as in the CLI version, aren't implemented in the
  parser/interpreter yet.
- Monaco is loaded from `unpkg.com` at runtime, so the machine running
  the server needs internet access for the editor to load in-browser
  (the Python backend itself needs no internet access).
