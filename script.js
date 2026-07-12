// script.js — Keshava online compiler frontend

let editor = null;

const KEYWORD_LIST = [
  "Aarambha", "Samaapti", "Sankhya", "Paatha", "Satyam", "Satya", "Asatya",
  "Likha", "Yadi", "Anyathaa", "Yaavat", "Punah", "Kriyaa", "Pratyaagaccha", "Grahana"
];

// ---------------------------------------------------------------------
// Monaco setup
// ---------------------------------------------------------------------

require.config({ paths: { vs: "https://unpkg.com/monaco-editor@0.47.0/min/vs" } });

require(["vs/editor/editor.main"], function () {
  monaco.languages.register({ id: "Keshava" });

  monaco.languages.setMonarchTokensProvider("Keshava", {
    keywords: KEYWORD_LIST,
    tokenizer: {
      root: [
        [/#.*$/, "comment"],
        [/"[^"]*"/, "string"],
        [/\d+/, "number"],
        [/[A-Za-z_][A-Za-z0-9_]*/, {
          cases: {
            "@keywords": "keyword",
            "@default": "identifier"
          }
        }],
        [/[{}()]/, "@brackets"],
        [/[=!<>]=?|[+\-*/%]/, "operator"],
      ]
    }
  });

  monaco.editor.defineTheme("Keshava-dark", {
    base: "vs-dark",
    inherit: true,
    rules: [
      { token: "keyword", foreground: "e8a33d", fontStyle: "bold" },
      { token: "string", foreground: "6bcf7f" },
      { token: "number", foreground: "9d8df1" },
      { token: "comment", foreground: "6b6879", fontStyle: "italic" },
      { token: "operator", foreground: "e9e7e2" },
    ],
    colors: {
      "editor.background": "#181822",
      "editor.foreground": "#e9e7e2",
      "editorLineNumber.foreground": "#3a3a4a",
      "editorLineNumber.activeForeground": "#9b98a8",
      "editorCursor.foreground": "#e8a33d",
      "editor.lineHighlightBackground": "#1d1d2988",
      "editor.selectionBackground": "#e8a33d33",
    }
  });

  editor = monaco.editor.create(document.getElementById("editor"), {
    value: DEFAULT_CODE,
    language: "Keshava",
    theme: "Keshava-dark",
    fontFamily: "'JetBrains Mono', monospace",
    fontSize: 14,
    minimap: { enabled: false },
    automaticLayout: true,
    scrollBeyondLastLine: false,
    padding: { top: 16 },
    tabSize: 4,
  });

  editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter, runProgram);
});

// ---------------------------------------------------------------------
// Tabs
// ---------------------------------------------------------------------

document.querySelectorAll(".tab-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".tab-btn").forEach((b) => b.classList.remove("active"));
    document.querySelectorAll(".tab-panel").forEach((p) => p.classList.remove("active"));
    btn.classList.add("active");
    document.getElementById(`panel-${btn.dataset.tab}`).classList.add("active");
  });
});

// ---------------------------------------------------------------------
// Status pill
// ---------------------------------------------------------------------

const statusPill = document.getElementById("status-pill");

function setStatus(state, label) {
  statusPill.className = `status-pill status-${state}`;
  statusPill.textContent = label;
}

// ---------------------------------------------------------------------
// Run / Reset
// ---------------------------------------------------------------------

const runBtn = document.getElementById("run-btn");
const resetBtn = document.getElementById("reset-btn");
const outputPanel = document.getElementById("panel-output");
const tokensPanel = document.getElementById("panel-tokens");
const astPanel = document.getElementById("panel-ast");

function escapeHtml(str) {
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

function renderOutput(result) {
  let html = "";

  if (result.output) {
    html += `<span class="line-out">${escapeHtml(result.output)}</span>`;
  }

  if (result.error) {
    const stageLabel = result.stage ? `[${result.stage} error] ` : "[error] ";
    html += `${result.output ? "\n" : ""}<span class="line-error">${escapeHtml(stageLabel + result.error)}</span>`;
  }

  if (!result.output && !result.error) {
    html = `<span class="hint-text">Program ran with no output.</span>`;
  }

  outputPanel.innerHTML = html;
}

function renderTokens(tokens) {
  if (!tokens || tokens.length === 0) {
    tokensPanel.innerHTML = `<span class="hint-text">No tokens produced.</span>`;
    return;
  }
  const lines = tokens.map((t, i) => {
    const idx = String(i).padStart(3, " ");
    return `${idx}  ${t.kind.padEnd(12, " ")} ${t.value}`;
  });
  tokensPanel.textContent = lines.join("\n");
}

function renderAst(astText) {
  if (!astText) {
    astPanel.innerHTML = `<span class="hint-text">No AST produced (parsing failed before completion).</span>`;
    return;
  }
  astPanel.textContent = astText;
}

async function runProgram() {
  if (!editor) return;

  const code = editor.getValue();

  runBtn.disabled = true;
  setStatus("running", "running");

  try {
    const response = await fetch("/api/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code }),
    });

    if (!response.ok) {
      throw new Error(`Server responded with ${response.status}`);
    }

    const result = await response.json();

    renderOutput(result);
    renderTokens(result.tokens);
    renderAst(result.ast);

    if (result.error) {
      setStatus("error", `${result.stage || "error"}`);
    } else {
      setStatus("success", "done");
    }
  } catch (err) {
    outputPanel.innerHTML = `<span class="line-error">[network error] ${escapeHtml(err.message)}</span>`;
    setStatus("error", "network error");
  } finally {
    runBtn.disabled = false;
  }
}

runBtn.addEventListener("click", runProgram);

resetBtn.addEventListener("click", () => {
  if (editor) {
    editor.setValue(DEFAULT_CODE);
  }
  setStatus("idle", "idle");
  outputPanel.innerHTML = `<span class="hint-text">Output will appear here after you run your program.</span>`;
  tokensPanel.innerHTML = `<span class="hint-text">Token stream will appear here after you run your program.</span>`;
  astPanel.innerHTML = `<span class="hint-text">The parsed AST will appear here after you run your program.</span>`;
});

// Also allow Ctrl/Cmd+Enter globally (in case focus is outside Monaco)
document.addEventListener("keydown", (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
    e.preventDefault();
    runProgram();
  }
});
