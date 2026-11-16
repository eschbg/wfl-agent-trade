import sqlite3
from pathlib import Path


class AuditRepository:
    def __init__(self, path: str = "trading_mvp.db"):
        self.connection = sqlite3.connect(Path(path))
        self.connection.execute("CREATE TABLE IF NOT EXISTS audit (id INTEGER PRIMARY KEY, action TEXT, detail TEXT)")
        self.connection.commit()

    def record(self, action: str, detail: str):
        self.connection.execute("INSERT INTO audit(action, detail) VALUES (?, ?)", (action, detail))
        self.connection.commit()
