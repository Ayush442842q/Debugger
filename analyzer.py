"""
analyzer.py — Root cause analysis engine
Takes code + error → returns deep structured analysis using Groq API
"""

from groq import Groq


class BugAnalyzer:
    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.3-70b-versatile"

    def analyze(self, code: str, error: str, language: str = "python") -> dict:
        """
        Deep analysis of broken code.
        Returns:
        {
            "root_cause"  : the real reason it broke,
            "line"        : which line caused it,
            "explanation" : plain English explanation,
            "fix"         : exact fix suggestion,
            "prevention"  : how to avoid this in future
        }
        """
        prompt = f"""
You are a senior software engineer and debugging expert.

Analyze this {language} code and its error deeply.

CODE:
{code}

ERROR:
{error}

Respond ONLY in this exact format, no extra text:

ROOT_CAUSE: <one line — the real reason it broke, not just what the error says>
LINE: <line number or range where the problem originates>
EXPLANATION: <2-3 sentences in plain English explaining what went wrong and why>
FIX: <the exact code fix or change needed>
PREVENTION: <one sentence on how to avoid this class of bug in future>
"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an expert debugger. You find root causes, not symptoms. "
                            "Always respond in the exact format requested. No extra text."
                        )
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=1024
            )
            raw = response.choices[0].message.content.strip()
            return self._parse_response(raw)

        except Exception as e:
            return {
                "root_cause": f"Analysis failed: {e}",
                "line": "Unknown",
                "explanation": "Could not connect to AI.",
                "fix": "Check your API key and internet connection.",
                "prevention": "N/A"
            }

    def _parse_response(self, raw: str) -> dict:
        result = {
            "root_cause": "Unknown",
            "line": "Unknown",
            "explanation": "Unknown",
            "fix": "Unknown",
            "prevention": "Unknown"
        }
        field_map = {
            "ROOT_CAUSE": "root_cause",
            "LINE": "line",
            "EXPLANATION": "explanation",
            "FIX": "fix",
            "PREVENTION": "prevention"
        }
        for line in raw.splitlines():
            for label, key in field_map.items():
                if line.startswith(f"{label}:"):
                    value = line[len(label) + 1:].strip()
                    if value:
                        result[key] = value
                    break
        return result
