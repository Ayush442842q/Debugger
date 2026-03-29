"""
memory.py — Stores past bugs and fixes so the AI remembers patterns
Uses a simple JSON file: memory.json
"""

import json
import os
from datetime import datetime

MEMORY_FILE = os.path.join(os.getcwd(), "memory.json")


class BugMemory:
    def __init__(self):
        self.memory = self._load()

    def _load(self) -> list:
        if not os.path.exists(MEMORY_FILE):
            return []
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def _save(self):
        try:
            with open(MEMORY_FILE, "w", encoding="utf-8") as f:
                json.dump(self.memory, f, indent=4)
        except Exception as e:
            print(f"[Memory] Could not save: {e}")

    def store(self, error: str, root_cause: str, fix: str, language: str):
        """Save a bug + fix to memory."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "language": language,
            "error_snippet": error[:200],       # first 200 chars of error
            "root_cause": root_cause,
            "fix": fix
        }
        self.memory.append(entry)
        # Keep only last 100 bugs
        if len(self.memory) > 100:
            self.memory = self.memory[-100:]
        self._save()

    def find_similar(self, error: str) -> dict | None:
        """
        Check if we've seen a similar error before.
        Simple keyword match on error snippet.
        Returns the most recent matching entry or None.
        """
        error_lower = error.lower()
        matches = []

        for entry in self.memory:
            stored = entry.get("error_snippet", "").lower()
            # Check for keyword overlap
            error_words = set(error_lower.split())
            stored_words = set(stored.split())
            overlap = error_words & stored_words
            if len(overlap) >= 3:  # at least 3 words in common
                matches.append((len(overlap), entry))

        if not matches:
            return None

        # Return the one with most overlap
        matches.sort(key=lambda x: x[0], reverse=True)
        return matches[0][1]

    def show_history(self, limit: int = 10) -> list:
        """Return last N bug entries."""
        return self.memory[-limit:]

    def clear(self):
        """Wipe all memory."""
        self.memory = []
        self._save()
