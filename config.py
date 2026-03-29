import json
import os
import sys

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.json")

PLACEHOLDER = "YOUR_API_KEY"

DEFAULTS = {
    "api_key": PLACEHOLDER,
    "default_language": "python",
    "theme": "monokai",
    "auto_run": True,
    "max_fix_attempts": 3,
    "timeout_seconds": 15,
    "save_all": False
}

VALID_THEMES = ["monokai", "dracula", "github-dark", "solarized-dark", "vim"]
VALID_LANGUAGES = ["python", "javascript", "c++", "java", "bash", None]


def load_config() -> dict:
    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULTS.copy())
        print(f"[!] config.json not found — created at:\n    {CONFIG_FILE}")
        print("[!] Add your Groq API key to config.json and restart.\n")

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            user_config = json.load(f)
    except json.JSONDecodeError as e:
        print(f"[!] config.json is corrupted: {e}")
        sys.exit(1)
    except OSError as e:
        print(f"[!] Could not read config.json: {e}")
        sys.exit(1)

    config = {**DEFAULTS, **user_config}

    if config["theme"] not in VALID_THEMES:
        config["theme"] = "monokai"

    try:
        config["max_fix_attempts"] = max(1, min(int(config["max_fix_attempts"]), 10))
    except (ValueError, TypeError):
        config["max_fix_attempts"] = 3

    try:
        config["timeout_seconds"] = max(5, min(int(config["timeout_seconds"]), 120))
    except (ValueError, TypeError):
        config["timeout_seconds"] = 15

    return config


def save_config(config: dict):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)
    except OSError as e:
        print(f"[!] Could not save config.json: {e}")


def get_api_key(config: dict) -> str:
    from rich.console import Console
    from rich.prompt import Prompt
    console = Console()

    key = config.get("api_key", "").strip()
    if key and key != PLACEHOLDER and key.startswith("gsk_"):
        return key

    key = os.environ.get("GROQ_API_KEY", "").strip()
    if key and key.startswith("gsk_"):
        return key

    console.print("\n[yellow]⚠ No API key found.[/yellow]")
    key = Prompt.ask("Enter your Groq API key", password=True)

    if not key or not key.strip():
        console.print("[red]❌ No API key provided. Exiting.[/red]")
        sys.exit(1)

    if not key.startswith("gsk_"):
        console.print("[red]❌ Invalid key. Groq keys start with 'gsk_'.[/red]")
        sys.exit(1)

    save = Prompt.ask("Save to config.json? (y/n)", default="y")
    if save.lower() == "y":
        config["api_key"] = key
        save_config(config)
        console.print("[green]✅ Key saved.[/green]")

    return key.strip()


def show_config(config: dict):
    from rich.console import Console
    from rich.table import Table
    console = Console()

    table = Table(title="⚙ Current Config", border_style="cyan")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="yellow")

    for key, value in config.items():
        if key == "api_key":
            display = "✅ Set" if (value and value != PLACEHOLDER) else "❌ Not set"
        else:
            display = str(value)
        table.add_row(key, display)

    console.print(table)
