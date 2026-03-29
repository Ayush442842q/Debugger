# 🤖 AI Code Generator + Debugger

Generate working code AND deeply understand every bug — powered by Groq (Llama 3).

---

## ⚡ Setup

```bash
pip install -r requirements.txt
```

Add your Groq API key to `config.json`:
```json
{ "api_key": "gsk_your_key_here" }
```

Run:
```bash
python main.py
```

---

## 🎮 Commands

| Command | What it does |
|---|---|
| `exit` | Quit |
| `history` | Show past prompts |
| `switch` | Change language |
| `explain` | Explain last generated code |
| `debug` | Deep debug mode — paste code + error |
| `bughistory` | Show past bugs from memory |
| `clearmemory` | Wipe bug memory |
| `config` | Show current settings |
| `settings` | Change API key, theme, timeout, etc. |

---

## 🧠 How Debug Mode Works

Type `debug` → paste your broken code → paste the error → get:

- **Root Cause** — the real reason it broke
- **Line** — exactly where
- **Explanation** — plain English
- **Fix** — exact code change
- **Prevention** — never hit this again

The tool also **remembers every bug** and warns you if it sees a similar one again.

---

## 🏗 Project Structure

```
code-generator/
├── main.py         # CLI — entry point
├── generator.py    # Code generation via Groq
├── executor.py     # Runs Python code safely
├── analyzer.py     # Deep root cause analysis (NEW)
├── memory.py       # Bug memory system (NEW)
├── config.py       # Settings management
├── config.json     # Your settings
├── memory.json     # Auto-created — stores past bugs
├── requirements.txt
└── output/         # Saved code files
```
