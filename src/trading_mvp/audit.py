import sqlite3
from pathlib import Path


class AuditRepository:
    def __init__(self, path: str = "trading_mvp.db"):
        self.connection = sqlite3.connect(Path(path), check_same_thread=False)
        self.connection.execute("CREATE TABLE IF NOT EXISTS audit (id INTEGER PRIMARY KEY, action TEXT, detail TEXT)")
        self.connection.commit()

    def record(self, action: str, detail: str):
        self.connection.execute("INSERT INTO audit(action, detail) VALUES (?, ?)", (action, detail))
        self.connection.commit()

    def list_recent(self, limit: int = 50) -> list[dict]:
        rows = self.connection.execute("SELECT action, detail FROM audit ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        return [{"action": action, "detail": detail} for action, detail in rows]
