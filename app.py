# app.py
#
# Flask backend for the Keshava online compiler.
#
#   Browser (Monaco editor)
#        │  POST /api/run  { "code": "..." }
#        ▼
#   Flask server  ──►  Lexer ──► Parser ──► Interpreter
#        │
#        ▼
#   JSON { tokens, ast, output, error, stage }
#
# Run with:
#   pip install -r requirements.txt
#   python app.py

import os
import sys
import io
import contextlib
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError

from flask import Flask, render_template, request, jsonify

# Make the Keshava/ package (lexer.py, parser.py, interpreter.py, ...)
# importable as top-level modules, exactly as they were written.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "Keshava"))

from lexer import lexer                                   # noqa: E402
from parser import Parser, ParserError                     # noqa: E402
from interpreter import Interpreter, msmRuntimeError        # noqa: E402

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, template_folder=PROJECT_ROOT, static_folder=PROJECT_ROOT)

EXECUTION_TIMEOUT_SECONDS = 5
executor = ThreadPoolExecutor(max_workers=4)

DEFAULT_CODE = """Aarambha

Sankhya age = 20

Paatha name = "Vivek"

Likha(name)

Yadi(age >= 18){
    Likha("Adult")
}
Anyathaa{
    Likha("Minor")
}

Samaapti
"""


def dump_ast(node, indent=0):
    """Render an AST node (or list of nodes) as an indented text tree."""
    pad = "  " * indent

    if isinstance(node, list):
        return "\n".join(dump_ast(item, indent) for item in node)

    if hasattr(node, "__dict__"):
        cls_name = type(node).__name__
        attrs = vars(node)
        if not attrs:
            return f"{pad}{cls_name}"

        lines = [f"{pad}{cls_name}"]
        for key, value in attrs.items():
            if isinstance(value, list) and value and hasattr(value[0], "__dict__"):
                lines.append(f"{pad}  {key}:")
                lines.append(dump_ast(value, indent + 2))
            elif hasattr(value, "__dict__"):
                lines.append(f"{pad}  {key}:")
                lines.append(dump_ast(value, indent + 2))
            else:
                lines.append(f"{pad}  {key}: {value!r}")
        return "\n".join(lines)

    return f"{pad}{node!r}"


def run_program(ast):
    """Executed on a worker thread so a runaway loop can time out."""
    buf = io.StringIO()
    interpreter = Interpreter()
    with contextlib.redirect_stdout(buf):
        interpreter.run(ast)
    return buf.getvalue()


@app.route("/")
def index():
    return render_template("index.html", default_code=DEFAULT_CODE)


@app.route("/api/run", methods=["POST"])
def api_run():
    data = request.get_json(force=True, silent=True) or {}
    code = data.get("code", "")

    result = {"tokens": None, "ast": None, "output": "", "error": None, "stage": None}

    # ---- Lexer -------------------------------------------------------
    try:
        tokens = lexer(code)
    except RuntimeError as e:
        result["error"] = str(e)
        result["stage"] = "lexer"
        return jsonify(result)

    result["tokens"] = [{"kind": kind, "value": value} for kind, value in tokens]

    # ---- Parser --------------------------------------------------------
    try:
        ast = Parser(tokens).parse()
    except ParserError as e:
        result["error"] = str(e)
        result["stage"] = "parser"
        return jsonify(result)
    except RecursionError:
        result["error"] = "Program is too deeply nested to parse."
        result["stage"] = "parser"
        return jsonify(result)

    result["ast"] = dump_ast(ast)

    # ---- Interpreter (with a wall-clock timeout) ----------------------
    future = executor.submit(run_program, ast)
    try:
        result["output"] = future.result(timeout=EXECUTION_TIMEOUT_SECONDS)
    except msmRuntimeError as e:
        result["error"] = str(e)
        result["stage"] = "runtime"
    except FutureTimeoutError:
        result["error"] = (
            f"Execution timed out after {EXECUTION_TIMEOUT_SECONDS}s "
            "(possible infinite loop)."
        )
        result["stage"] = "runtime"
    except RecursionError:
        result["error"] = "Maximum recursion depth exceeded (possible infinite recursion)."
        result["stage"] = "runtime"
    except Exception as e:  # noqa: BLE001 - surface any other runtime failure safely
        result["error"] = f"{type(e).__name__}: {e}"
        result["stage"] = "runtime"

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
