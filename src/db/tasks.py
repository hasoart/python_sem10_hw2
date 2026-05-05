import sqlite3

from core.config import settings

DB_PATH = settings.db_path


def init_db() -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                task_id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                result INTEGER,
                error TEXT
            )
            """
        )


def create(task_id: str) -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO tasks (task_id, status) VALUES (?, ?)",
            (task_id, "queued"),
        )


def update(
    task_id: str,
    status: str,
    result: int | None = None,
    error: str | None = None,
) -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            UPDATE tasks
            SET status = ?, result = ?, error = ?
            WHERE task_id = ?
            """,
            (status, result, error, task_id),
        )


def get(task_id: str) -> dict | None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT * FROM tasks WHERE task_id = ?",
            (task_id,),
        ).fetchone()

    if row is None:
        return None

    return dict(row)
