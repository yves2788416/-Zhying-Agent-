# Zhying Agent

A fully **local-first** AI agent built with [Ollama](https://ollama.com) + [LangChain](https://www.langchain.com) + [LangGraph](https://www.langchain.com/langgraph) + [Streamlit](https://streamlit.io). It features **long-term memory, self-reflection, private knowledge base (RAG), web search, and file operations** — with no cloud API calls and all data staying on your machine.

> No API key required. Both the models and your data run locally, for maximum privacy and control.

---

## Features

- 🤖 **ReAct agent** — powered by LangGraph's `create_react_agent`, it autonomously picks tools to complete tasks instead of following a fixed flow.
- 🔀 **Dual-path retrieval (dual routing)** — two information channels: local private knowledge + live web search, routed on demand. Falls back to the web when local lookup misses, balancing privacy and freshness.
- 🧠 **Long-term memory** — persistent vector memory (ChromaDB) that remembers you across sessions.
- 📚 **Private knowledge base (RAG)** — upload `.docx` files; they are chunked, embedded, and retrieved on demand.
- 🔁 **Self-reflection** — every answer is self-reviewed and refined before being returned.
- 🌐 **Web search / scraping** — DuckDuckGo search plus web-page text extraction.
- 📝 **File operations** — read/write files, list directories, and execute Python code (sandboxed) inside the project directory.
- 🛡️ **Hardened** — path-traversal guard, high-risk commands blocked, file ops confined to the project root.
- 🎨 **Dual entry points + dark web UI** — `app.py` (full-featured Streamlit web app) and `agent.py` (lightweight CLI).

---

## Tech Stack

| Layer | Technology |
|---|---|
| Web UI | Streamlit |
| LLM | Ollama (local inference) |
| Agent framework | LangGraph (ReAct Agent + SQLite checkpointer) |
| Orchestration | LangChain (ollama / chroma / community / text-splitters) |
| Vector database | ChromaDB |
| Document parsing | docx2txt |
| Search / scraping | DuckDuckGo (ddgs), requests, BeautifulSoup |

---

## Requirements

- **OS**: Windows / macOS / Linux.
- **Python**: 3.11+ (developed on 3.12).
- **RAM**: 8GB+ recommended (a 7B model needs roughly 4–6GB; an NVIDIA GPU speeds things up but is not required).
- **Disk**: ~5–8GB for the models (`qwen2.5:7b` ≈ 4.7GB + coder + embedding model).

---

## Installation

### Step 1 — Install Ollama (the local model server)

1. Download the installer for your OS from <https://ollama.com/download>.
2. After installation, Ollama runs as a background service on port `11434`.

Verify:

```bash
ollama --version
```

### Step 2 — Download the models

```bash
# Main brain: general chat
ollama pull qwen2.5:7b

# Coding model (used for code tasks in app.py)
ollama pull qwen2.5-coder:7b

# Embedding model (required for knowledge base & memory)
ollama pull nomic-embed-text
```

Check installed models:

```bash
ollama list
```

### Step 3 — Install Python dependencies

From the project root (the directory containing this README):

```bash
# Create a virtual environment (recommended)
python -m venv .venv

# Activate it
# Windows:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## Running the Project

### Option A — Web UI (recommended, full features)

```bash
streamlit run app.py
```

Your browser opens at <http://localhost:8501>. Chat on the left, upload `.docx` documents to the knowledge base on the right.

### Option B — CLI (lightweight)

```bash
python agent.py
```

Interactive loop; type `exit` to quit. Provides local file reading, web search, and web scraping.

---

## Configuration

| Environment variable | Purpose | Default |
|---|---|---|
| `ZHIYING_ROOT` | Working directory the agent operates in (file read/write and code execution) | `project/` next to the script (auto-created) |
| `OLLAMA_MAX_LOADED_MODELS` | Memory optimization: max models Ollama keeps resident | `1` |

> Normally no configuration is needed — it works out of the box. All paths are resolved relative to the script location, so you can move the project folder freely.

---

## Project Structure

```
my-agent-safe/
├── app.py              # Main app: Streamlit web UI (full agent)
├── agent.py            # CLI entry point (lightweight agent)
├── requirements.txt    # Python dependencies
├── .gitignore          # Git ignore rules
├── README.md           # Chinese documentation
├── README_EN.md        # This English documentation
└── LICENSE             # MIT license

Generated at runtime (git-ignored; do not upload):
├── project/            # Agent working directory (ZHIYING_ROOT)
├── chroma_db/          # Private knowledge-base vectors
├── zhying_memory/      # Long-term memory vectors
├── zhying_session.db   # Session checkpoints (SQLite)
└── zhying_runtime.log  # Runtime log
```

---

## How It Works

### Core components

| Component | Purpose |
|---|---|
| `qwen2.5:7b` | Main brain: general chat, reasoning, decision-making |
| `qwen2.5-coder:7b` | Coding model for code-related tasks |
| `nomic-embed-text` | Embedding model: turns text into vectors for retrieval |
| `zhying_memory/` | Long-term memory store (ChromaDB) |
| `chroma_db/` | Private knowledge base (ChromaDB) |
| `zhying_session.db` | Session checkpoints (SQLite, used by LangGraph) |

### Dual-path retrieval (dual routing)

The agent has two ways to get information, chosen on demand by the ReAct decision core:

- **Local route** — search long-term memory + the private knowledge base, for private, offline, or proprietary material.
- **Web route** — DuckDuckGo search + web scraping, for live, public information.

```
Data flow:
  user input
     │
     ▼
 LangGraph ReAct decision core (the brain)
     │
     ├─ local route ─► long-term memory + knowledge base (RAG)
     ├─ web route   ─► DuckDuckGo search + web scraping
     └─ tool calls  ─► file read/write / list dir / Python sandbox
     │
     ▼
 Ollama local models (qwen2.5:7b / qwen2.5-coder:7b)
     │
     ▼
 self-reflection → final answer → written to long-term memory
```

### A single answer, step by step

1. **Input** — the user types a prompt in the UI.
2. **Retrieve** — the agent searches long-term memory and the private knowledge base for relevant context.
3. **Decide** — the LangGraph ReAct agent chooses which tool to call (file ops / search / scraping / memory / code execution).
4. **Generate** — the local Ollama model produces a first answer.
5. **Reflect** — the agent self-reviews the answer and returns a refined final version.
6. **Remember** — the conversation is compressed and written into long-term memory.

---

## Security Notes

The code enforces these constraints:

- ✅ All file operations are **confined to `ZHIYING_ROOT`**; anything outside is blocked.
- ✅ Prompt-level bans on high-risk commands such as `rm` / `del` / `format`.
- ✅ Self-iteration is restricted to `sandbox_test/` or temporary scripts.
- ⚠️ `safe_python_execute` is currently **weakly isolated** (it executes Python directly). Run it only in a **trusted, personal** environment; do not expose it to the public internet.

---

## FAQ

**Q: `ModuleNotFoundError` on startup?**
Make sure the virtual environment is activated and you ran `pip install -r requirements.txt`.

**Q: `ConnectionError` or can't reach Ollama?**
The Ollama service isn't running. Start "Ollama" from your Start menu, or run `ollama serve`.

**Q: Model not found?**
Run `ollama pull qwen2.5:7b` (and the other models) as shown in the installation section.

**Q: Uploaded a `.docx` but the knowledge base didn't update?**
Make sure the `nomic-embed-text` embedding model is pulled, and check `zhying_runtime.log`.

**Q: Slow on a low-end machine?**
CPU inference is slower than GPU. You can switch to a smaller model, e.g. change `qwen2.5:7b` to `qwen2.5:3b` in `app.py`.

---

## License

[MIT](LICENSE) — see the LICENSE file for details. Please also respect the licenses of Ollama, the open-source models, and the bundled dependencies.
