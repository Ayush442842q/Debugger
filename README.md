# 🧠 BugMind
### *It doesn't just fix your code — it tells you **why** it broke.*

<p align="center">
  <img src="https://img.shields.io/badge/powered%20by-Groq%20%2F%20Llama%203-orange?style=for-the-badge" />
  <img src="https://img.shields.io/badge/language-Python-blue?style=for-the-badge&logo=python" />
  <img src="https://img.shields.io/badge/CLI-rich%20terminal-green?style=for-the-badge" />
  <img src="https://img.shields.io/badge/license-MIT-lightgrey?style=for-the-badge" />
</p>

---

Most AI tools just **fix the error and move on.**

BugMind goes deeper:
```
🔍 Root Cause  →  The function does not validate inputs to prevent division by zero.
📍 Line        →  3-4
📖 Explanation →  You called divide(10, 0). Python cannot divide by zero.
                  The function has no guard to catch this before it executes.
🔧 Fix         →  if b == 0: raise ValueError("Cannot divide by zero")
🛡 Prevention  →  Always validate numeric inputs before performing arithmetic operations.
```

**Every bug. Every time. In plain English.**

---

## ⚡ Quick Start
```bash
# 1. Clone
git clone https://github.com/Ayush442842q/bugmind
cd bugmind

# 2. Install
pip install -r requirements.txt

# 3. Add your free Groq API key to config.json
# Get one free at: https://console.groq.com

# 4. Run
python main.py
```

---

## 🎮 What It Does

### Generate Code
Type your idea in plain English → get working, runnable code instantly.
```
You: write a web scraper that gets headlines from a news site
✅ Generated python code: [complete, runnable script]
🚀 Running... ▶ Headline 1: ...
```

### Deep Debug Mode
Type `debug` → paste any broken code + error → get a full breakdown.
```
You: debug
> Paste your broken code... END
> Paste the error... END

🧠 Deep Bug Analysis
┌──────────────┬──────────────────────────────────────────────┐
│ 🔍 Root Cause│ Missing null check before dictionary access  │
│ 📍 Line      │ 12                                           │
│ 📖 Explanation│ The API returned None but code assumed dict  │
│ 🔧 Fix       │ if data is None: return {}                   │
│ 🛡 Prevention │ Always validate API responses before use     │
└──────────────┴──────────────────────────────────────────────┘
✅ Bug saved to memory.
```

### Bug Memory
BugMind **remembers every bug you've hit.** Next time it sees a similar error, it warns you instantly — before the AI even runs.
```
⚡ Seen this before!
Root Cause: Missing null check before dictionary access
Fix: if data is None: return {}
```

---

## 🧩 Commands

| Command | What it does |
|---|---|
| `debug` | Deep bug analysis mode |
| `bughistory` | See all bugs BugMind has analyzed |
| `clearmemory` | Wipe bug memory |
| `explain` | Explain last generated code |
| `history` | Show past prompts |
| `switch` | Change programming language |
| `settings` | Change API key, theme, timeout |
| `exit` | Quit |

---

## 🏗 Project Structure
```
bugmind/
├── main.py         # CLI entry point
├── generator.py    # Code generation via Groq API
├── executor.py     # Runs Python code safely with live output
├── analyzer.py     # Root cause analysis engine
├── memory.py       # Bug memory — learns from every error
├── config.py       # Settings management
├── config.json     # Your config (add API key here)
├── memory.json     # Auto-created — stores past bugs
├── requirements.txt
└── output/         # Saved code files go here
```

---

## 🔧 How It Works
```
You type a prompt
        ↓
generator.py → Groq API (Llama 3) → raw code
        ↓
executor.py → runs in temp file → live output stream
        ↓
   [if error]
        ↓
analyzer.py → root cause analysis → structured breakdown
        ↓
memory.py → stores bug pattern for future reference
        ↓
generator.py → auto-fix → retry (up to 3 attempts)
```

---

## 🚀 Languages Supported

| Language | Generate | Debug | Auto-run |
|---|---|---|---|
| Python | ✅ | ✅ | ✅ |
| JavaScript | ✅ | ✅ | ❌ |
| C++ | ✅ | ✅ | ❌ |
| Java | ✅ | ✅ | ❌ |
| Bash | ✅ | ✅ | ❌ |

---

## 🔑 Get a Free Groq API Key

1. Go to [console.groq.com](https://console.groq.com)
2. Sign up → API Keys → Create
3. Paste it in `config.json`

Groq is **free** and insanely fast. No credit card needed.

---

## 📌 Roadmap

- [ ] Multi-file project generation
- [ ] Web UI (Flask)
- [ ] Support more languages
- [ ] Export bug report as PDF
- [ ] VS Code extension

---

## 🤝 Contributing

PRs welcome. Open an issue first for big changes.

---

## 📄 License

MIT — free to use, modify, and distribute.

---

<p align="center">Built solo. No team. No funding. Just code. 🖤</p>
