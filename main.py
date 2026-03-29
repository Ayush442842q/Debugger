import os
import sys
import re
from config import load_config, get_api_key, show_config, save_config
from generator import CodeGenerator
from executor import CodeExecutor
from analyzer import BugAnalyzer
from memory import BugMemory
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.syntax import Syntax
from rich.table import Table

console = Console()

LANGUAGES = {
    "1": "python",
    "2": "javascript",
    "3": "c++",
    "4": "java",
    "5": "bash"
}


def show_banner():
    console.print(Panel.fit(
        "[bold cyan]🤖 AI Code Generator + Debugger[/bold cyan]\n"
        "[dim]Powered by Groq (Llama 3)[/dim]\n"
        "[yellow]Generate code · Debug deeply · Learn from every bug[/yellow]",
        border_style="cyan"
    ))


def choose_language(current: str = None) -> str:
    console.print("\n[bold]Choose a language:[/bold]")
    for key, lang in LANGUAGES.items():
        marker = " [green]← current[/green]" if lang == current else ""
        console.print(f"  [cyan]{key}[/cyan]. {lang}{marker}")
    console.print("  [cyan]6[/cyan]. auto-detect from prompt\n")
    choice = Prompt.ask("Enter choice", default="1")
    if choice == "6":
        return None
    return LANGUAGES.get(choice, "python")


def show_analysis(analysis: dict, theme: str = "monokai"):
    """Display a beautiful bug analysis panel."""
    table = Table(border_style="red", show_header=False, padding=(0, 1))
    table.add_column("Field", style="bold red", width=14)
    table.add_column("Detail", style="white")

    table.add_row("🔍 Root Cause", analysis["root_cause"])
    table.add_row("📍 Line",       analysis["line"])
    table.add_row("📖 Explanation", analysis["explanation"])
    table.add_row("🔧 Fix",        analysis["fix"])
    table.add_row("🛡 Prevention", analysis["prevention"])

    console.print(Panel(table, title="[bold red]🧠 Deep Bug Analysis[/bold red]", border_style="red"))


def run_debug_mode(api_key: str, theme: str):
    """
    Standalone debug mode — paste any code + error,
    get deep root cause analysis.
    """
    console.print(Panel(
        "[bold]Paste your broken code below.[/bold]\n"
        "[dim]Type END on a new line when done.[/dim]",
        border_style="yellow"
    ))

    lines = []
    while True:
        line = input()
        if line.strip() == "END":
            break
        lines.append(line)

    code = "\n".join(lines)
    if not code.strip():
        console.print("[red]No code entered.[/red]")
        return

    console.print("\n[bold]Now paste the error message.[/bold] [dim]Type END when done.[/dim]")
    error_lines = []
    while True:
        line = input()
        if line.strip() == "END":
            break
        error_lines.append(line)

    error = "\n".join(error_lines)
    if not error.strip():
        console.print("[red]No error entered.[/red]")
        return

    lang = Prompt.ask("Language", default="python")

    # Check memory for similar past bug
    memory = BugMemory()
    similar = memory.find_similar(error)
    if similar:
        console.print(Panel(
            f"[yellow]⚡ Similar bug found in memory![/yellow]\n\n"
            f"[dim]Language:[/dim] {similar['language']}\n"
            f"[dim]Root Cause:[/dim] {similar['root_cause']}\n"
            f"[dim]Fix:[/dim] {similar['fix']}\n"
            f"[dim]When:[/dim] {similar['timestamp']}",
            title="[yellow]🧠 Memory Match[/yellow]",
            border_style="yellow"
        ))

    # Deep analysis
    with console.status("[bold red]🔬 Analyzing root cause...[/bold red]"):
        analyzer = BugAnalyzer(api_key)
        analysis = analyzer.analyze(code, error, lang)

    show_analysis(analysis, theme)

    # Save to memory
    memory.store(error, analysis["root_cause"], analysis["fix"], lang)
    console.print("[dim]✅ Bug saved to memory.[/dim]\n")


def main():
    config = load_config()
    api_key = get_api_key(config)

    show_banner()

    language = config.get("default_language", "python")
    if language not in LANGUAGES.values():
        language = None

    console.print(f"[green]✅ Language: {language or 'auto-detect'}[/green] [dim](config.json)[/dim]")
    console.print(
        "[dim]Commands: 'exit' | 'history' | 'switch' | 'explain' | "
        "'debug' | 'bughistory' | 'clearmemory' | 'config' | 'settings'[/dim]\n"
    )

    generator = CodeGenerator(api_key, language)
    executor = CodeExecutor(timeout=config.get("timeout_seconds", 15))
    memory = BugMemory()
    history = []
    last_code = None
    last_lang = None

    while True:
        try:
            prompt = Prompt.ask("[bold yellow]You[/bold yellow]")

            if not prompt.strip():
                continue

            cmd = prompt.strip().lower()

            # ── EXIT ──────────────────────────────────────────────
            if cmd == "exit":
                console.print("[cyan]Bye! Happy coding! 🚀[/cyan]")
                break

            # ── HISTORY ───────────────────────────────────────────
            elif cmd == "history":
                if not history:
                    console.print("[dim]No history yet.[/dim]")
                else:
                    for i, h in enumerate(history, 1):
                        console.print(f"[cyan]{i}.[/cyan] {h}")
                continue

            # ── SWITCH LANGUAGE ───────────────────────────────────
            elif cmd == "switch":
                language = choose_language(current=language)
                generator.set_language(language)
                console.print(f"[green]✅ Switched to: {language or 'auto-detect'}[/green]")
                continue

            # ── EXPLAIN LAST CODE ─────────────────────────────────
            elif cmd == "explain":
                if not last_code:
                    console.print("[yellow]No code generated yet.[/yellow]")
                    continue
                with console.status("[bold cyan]🧠 Explaining...[/bold cyan]"):
                    explanation = generator.explain(last_code, last_lang)
                console.print(Panel(explanation, title="[cyan]📖 Explanation[/cyan]", border_style="cyan"))
                continue

            # ── DEBUG MODE (new) ──────────────────────────────────
            elif cmd == "debug":
                run_debug_mode(api_key, config.get("theme", "monokai"))
                continue

            # ── BUG HISTORY (new) ─────────────────────────────────
            elif cmd == "bughistory":
                bugs = memory.show_history()
                if not bugs:
                    console.print("[dim]No bugs in memory yet.[/dim]")
                else:
                    for i, b in enumerate(bugs, 1):
                        console.print(
                            f"[cyan]{i}.[/cyan] [{b['language']}] "
                            f"[red]{b['root_cause']}[/red] → [green]{b['fix']}[/green]"
                        )
                continue

            # ── CLEAR MEMORY (new) ────────────────────────────────
            elif cmd == "clearmemory":
                if Confirm.ask("Clear all bug memory?", default=False):
                    memory.clear()
                    console.print("[green]✅ Memory cleared.[/green]")
                continue

            # ── CONFIG ────────────────────────────────────────────
            elif cmd == "config":
                show_config(config)
                continue

            # ── SETTINGS ──────────────────────────────────────────
            elif cmd == "settings":
                console.print("\n[bold]Settings:[/bold]")
                console.print("  [cyan]1[/cyan]. Change API key")
                console.print("  [cyan]2[/cyan]. Change default language")
                console.print("  [cyan]3[/cyan]. Toggle auto-run")
                console.print("  [cyan]4[/cyan]. Change theme")
                console.print("  [cyan]5[/cyan]. Change timeout")
                console.print("  [cyan]6[/cyan]. Toggle save-all\n")
                s = Prompt.ask("Choice", default="1")

                if s == "1":
                    new_key = Prompt.ask("New Groq API key", password=True)
                    if new_key.strip().startswith("gsk_"):
                        config["api_key"] = new_key.strip()
                        save_config(config)
                        console.print("[green]✅ API key updated.[/green]")
                    else:
                        console.print("[red]❌ Invalid key (must start with gsk_)[/red]")

                elif s == "2":
                    new_lang = choose_language(current=config.get("default_language"))
                    config["default_language"] = new_lang or "python"
                    save_config(config)
                    generator.set_language(new_lang)
                    console.print(f"[green]✅ Language: {new_lang or 'auto-detect'}[/green]")

                elif s == "3":
                    config["auto_run"] = not config.get("auto_run", True)
                    save_config(config)
                    console.print(f"[green]✅ Auto-run: {'ON' if config['auto_run'] else 'OFF'}[/green]")

                elif s == "4":
                    console.print("Themes: monokai, dracula, github-dark, solarized-dark, vim")
                    new_theme = Prompt.ask("Theme", default=config.get("theme", "monokai"))
                    config["theme"] = new_theme
                    save_config(config)
                    console.print(f"[green]✅ Theme: {new_theme}[/green]")

                elif s == "5":
                    new_timeout = Prompt.ask("Timeout (seconds)", default=str(config.get("timeout_seconds", 15)))
                    try:
                        config["timeout_seconds"] = max(5, min(int(new_timeout), 120))
                        executor.timeout = config["timeout_seconds"]
                        save_config(config)
                        console.print(f"[green]✅ Timeout: {config['timeout_seconds']}s[/green]")
                    except ValueError:
                        console.print("[red]❌ Invalid number.[/red]")

                elif s == "6":
                    config["save_all"] = not config.get("save_all", False)
                    save_config(config)
                    console.print(f"[green]✅ Save-all: {'ON' if config['save_all'] else 'OFF'}[/green]")

                continue

            # ── GENERATE CODE ─────────────────────────────────────
            history.append(prompt)

            with console.status("[bold cyan]🧠 Generating code...[/bold cyan]"):
                code, detected_lang = generator.generate(prompt)

            if not code:
                console.print("[red]❌ Failed to generate. Try rephrasing.[/red]")
                continue

            last_code = code
            last_lang = detected_lang
            theme = config.get("theme", "monokai")

            console.print(f"\n[bold green]✅ Generated {detected_lang} code:[/bold green]")
            console.print(Panel(Syntax(code, detected_lang, theme=theme, line_numbers=True), border_style="green"))

            # ── RUN PYTHON CODE ───────────────────────────────────
            if detected_lang == "python":
                should_run = config.get("auto_run", True)
                if not should_run:
                    should_run = Confirm.ask("\n[yellow]▶ Run this code?[/yellow]", default=True)

                if should_run:
                    console.print("\n[bold cyan]🚀 Running...[/bold cyan]\n")
                    success, output, error = executor.execute(code, detected_lang)

                    if success:
                        console.print(Panel(output or "[dim](No output)[/dim]", title="[green]Output[/green]", border_style="green"))
                    else:
                        console.print(Panel(error, title="[red]Error[/red]", border_style="red"))

                        # ── DEEP ANALYSIS (new) ───────────────────
                        if Confirm.ask("\n[red]🔬 Run deep bug analysis?[/red]", default=True):
                            # Check memory first
                            similar = memory.find_similar(error)
                            if similar:
                                console.print(Panel(
                                    f"[yellow]⚡ Seen this before![/yellow]\n"
                                    f"Root Cause: {similar['root_cause']}\n"
                                    f"Fix: {similar['fix']}",
                                    title="[yellow]Memory Match[/yellow]",
                                    border_style="yellow"
                                ))

                            with console.status("[bold red]🔬 Analyzing root cause...[/bold red]"):
                                analyzer = BugAnalyzer(api_key)
                                analysis = analyzer.analyze(code, error, detected_lang)

                            show_analysis(analysis)
                            memory.store(error, analysis["root_cause"], analysis["fix"], detected_lang)

                        # ── AUTO FIX ──────────────────────────────
                        if Confirm.ask("\n[yellow]🔧 Auto-fix this error?[/yellow]", default=True):
                            max_attempts = config.get("max_fix_attempts", 3)
                            for attempt in range(1, max_attempts + 1):
                                console.print(f"\n[cyan]🔄 Fix attempt {attempt}/{max_attempts}...[/cyan]")
                                with console.status("[bold cyan]🧠 Fixing...[/bold cyan]"):
                                    fixed_code, _ = generator.fix(code, error, detected_lang)

                                if not fixed_code:
                                    console.print("[red]Couldn't generate a fix.[/red]")
                                    break

                                console.print(Panel(
                                    Syntax(fixed_code, detected_lang, theme=theme, line_numbers=True),
                                    title="[yellow]Fixed Code[/yellow]", border_style="yellow"
                                ))

                                success, output, error = executor.execute(fixed_code, detected_lang)
                                if success:
                                    console.print(Panel(
                                        output or "[dim](No output)[/dim]",
                                        title="[green]✅ Fixed & Working![/green]", border_style="green"
                                    ))
                                    last_code = fixed_code
                                    break
                                else:
                                    console.print(f"[red]Still failing: {error}[/red]")
                            else:
                                console.print(f"[red]❌ Couldn't fix after {max_attempts} attempts.[/red]")

            # ── SAVE ──────────────────────────────────────────────
            save_all = config.get("save_all", False)
            if save_all or Confirm.ask("\n[yellow]💾 Save to file?[/yellow]", default=False):
                ext = {"python": "py", "javascript": "js", "c++": "cpp", "java": "java", "bash": "sh"}.get(detected_lang, "txt")
                if save_all:
                    auto_name = "_".join(prompt.split()[:4])
                    filename = re.sub(r"[^\w\-]", "_", auto_name).strip("_") or "generated_code"
                else:
                    filename = Prompt.ask("Filename (no extension)", default="generated_code")
                    filename = re.sub(r"[^\w\-]", "_", filename).strip("_") or "generated_code"

                try:
                    os.makedirs("output", exist_ok=True)
                    filepath = os.path.join("output", f"{filename}.{ext}")
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(last_code)
                    console.print(f"[green]✅ Saved to {filepath}[/green]")
                except OSError as e:
                    console.print(f"[red]❌ Could not save: {e}[/red]")

            console.print()

        except KeyboardInterrupt:
            console.print("\n[cyan]Bye! Happy coding! 🚀[/cyan]")
            break


if __name__ == "__main__":
    main()
