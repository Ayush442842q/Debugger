import os
import sys
import tempfile
import subprocess
import threading
from rich.console import Console

console = Console()


class CodeExecutor:
    def __init__(self, timeout: int = 15):
        self.timeout = timeout

    def _is_interactive(self, code: str) -> bool:
        patterns = ["input(", "input (", "raw_input(", "getpass(", "sys.stdin"]
        return any(p in code for p in patterns)

    def execute(self, code: str, language: str = "python"):
        if language.lower() not in ("python", "py"):
            return False, "", f"⚠ Auto-run not supported for {language}."

        if self._is_interactive(code):
            return False, "", (
                "⚠ This code uses input() — save and run it manually:\n"
                "  python output\\<filename>.py"
            )

        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as tmp:
                tmp.write(code)
                tmp_path = tmp.name

            process = subprocess.Popen(
                [sys.executable, tmp_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8"
            )

            stdout_lines = []
            stderr_lines = []

            def stream_stdout():
                for line in process.stdout:
                    stripped = line.rstrip()
                    stdout_lines.append(stripped)
                    console.print(f"[green]▶[/green] {stripped}")

            def stream_stderr():
                for line in process.stderr:
                    stripped = line.rstrip()
                    stderr_lines.append(stripped)
                    console.print(f"[red]✗[/red] {stripped}")

            t_out = threading.Thread(target=stream_stdout)
            t_err = threading.Thread(target=stream_stderr)
            t_out.start()
            t_err.start()

            try:
                process.wait(timeout=self.timeout)
            except subprocess.TimeoutExpired:
                process.kill()
                try:
                    process.stdout.close()
                    process.stderr.close()
                except:
                    pass
                try:
                    process.wait(timeout=1)
                except:
                    pass
                t_out.join(timeout=1)
                t_err.join(timeout=1)
                return False, "", f"❌ Timed out after {self.timeout}s. Possible infinite loop."

            t_out.join()
            t_err.join()

            output = "\n".join(stdout_lines)
            error = "\n".join(stderr_lines)

            if process.returncode == 0:
                return True, output or "(No output)", ""
            else:
                return False, "", error or "Unknown error."

        except Exception as e:
            return False, "", f"❌ Execution failed: {e}"
        finally:
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except OSError:
                    pass
