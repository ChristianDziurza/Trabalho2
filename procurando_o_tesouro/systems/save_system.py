from __future__ import annotations
import json
import os
from datetime import datetime
from config.settings import settings

class SaveSystem:
    def __init__(self, path=None):
        self.path = path or settings.RECORDS_FILE
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        self.records = self._load()

    def _load(self):
        if not os.path.exists(self.path): return []
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, list) else []
        except Exception:
            return []

    def _save(self):
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self.records, f, indent=2, ensure_ascii=False)
        except OSError:
            pass

    def add_result(self, name, score, num_players):
        self.records.append({
            "name": name, "score": score,
            "date": datetime.now().isoformat(timespec="seconds"),
            "players": num_players,
        })
        self.records.sort(key=lambda r: r.get("score", 0), reverse=True)
        self.records = self.records[:50]
        self._save()

    def top(self, n=10):
        return self.records[:n]
