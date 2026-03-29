import re
from groq import Groq

LANG_KEYWORDS = {
    "python": ["python", "py", "django", "flask", "pandas", "numpy"],
    "javascript": ["javascript", "js", "node", "react", "vue", "typescript"],
    "c++": ["c++", "cpp", "c plus plus"],
    "java": ["java", "spring", "maven"],
    "bash": ["bash", "shell", "script", "terminal", "linux command"],
}


class CodeGenerator:
    def __init__(self, api_key: str, language: str = None):
        self.client = Groq(api_key=api_key)
        self.language = language
        self.model = "llama-3.3-70b-versatile"

    def set_language(self, language: str):
        self.language = language

    def _detect_language(self, prompt: str) -> str:
        prompt_lower = prompt.lower()
        for lang, keywords in LANG_KEYWORDS.items():
            if any(kw in prompt_lower for kw in keywords):
                return lang
        return "python"

    def _build_system_prompt(self, language: str) -> str:
        return f"""You are an expert {language} code generator.

STRICT RULES:
1. Output ONLY raw {language} code — no explanations, no markdown, no backticks
2. No preamble like "Here is the code:" — just the code itself
3. Code must be complete, runnable, and well-commented
4. Always add error handling where appropriate
5. Use best practices for {language}
6. If the request is unclear, make reasonable assumptions
7. NEVER use input(), raw_input(), or any interactive user input
8. NEVER require user interaction at runtime
9. If input is needed, use hardcoded example values
10. Always include a main execution block or example usage
"""

    def _call_api(self, messages: list, temperature: float = 0.2, max_tokens: int = 2048):
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise RuntimeError(f"API call failed: {e}")

    def generate(self, prompt: str):
        lang = self.language or self._detect_language(prompt)
        try:
            messages = [
                {"role": "system", "content": self._build_system_prompt(lang)},
                {"role": "user", "content": f"Write {lang} code that: {prompt}. Must run without user input."}
            ]
            code = self._call_api(messages, temperature=0.2)
            code = self._clean_code(code)
            if not code or not code.strip():
                return None, lang
            return code, lang
        except Exception as e:
            print(f"Generation error: {e}")
            return None, lang

    def fix(self, broken_code: str, error: str, language: str = None):
        lang = language or self.language or "python"
        try:
            messages = [
                {"role": "system", "content": self._build_system_prompt(lang)},
                {"role": "user", "content": (
                    f"Fix this {lang} code.\n\nBROKEN CODE:\n{broken_code}\n\nERROR:\n{error}\n\n"
                    f"Output ONLY the fixed code. No explanations."
                )}
            ]
            code = self._call_api(messages, temperature=0.1)
            code = self._clean_code(code)
            if not code or not code.strip():
                return None, lang
            return code, lang
        except Exception as e:
            print(f"Fix error: {e}")
            return None, lang

    def explain(self, code: str, language: str):
        try:
            messages = [
                {"role": "system", "content": "You are a helpful coding tutor. Explain code clearly and concisely."},
                {"role": "user", "content": f"Explain what this {language} code does:\n\n{code}"}
            ]
            return self._call_api(messages, temperature=0.3, max_tokens=1024)
        except Exception as e:
            return f"Could not generate explanation: {e}"

    def _clean_code(self, code: str) -> str:
        code = re.sub(r"^```[\w]*\n?", "", code, flags=re.MULTILINE)
        code = re.sub(r"```$", "", code, flags=re.MULTILINE)
        return code.strip()
