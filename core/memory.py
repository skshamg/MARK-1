import os
import sqlite3

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "mark1_memory.db"))


def _init_db():
    """Initializes the persistent memory table if it doesn't exist."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS memories (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


# Run DB initialization once on import
_init_db()


def remember(key: str, value: str) -> str:
    """
    Saves or updates a fact, preference, or project detail into long-term memory.
    Example: key='project_goal', value='Building autonomous Mark-1 system agent'
    """
    clean_key = key.strip().lower()
    clean_val = value.strip()

    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(
                """
                INSERT INTO memories (key, value, timestamp)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(key) DO UPDATE SET
                    value = excluded.value,
                    timestamp = CURRENT_TIMESTAMP
                """,
                (clean_key, clean_val),
            )
        return f"Memory stored: '{clean_key}' -> '{clean_val}'."
    except Exception as e:
        return f"Failed to store memory: {e}"


def recall(query: str) -> str:
    """
    Searches persistent memory for facts matching a query or keyword.
    """
    clean_query = f"%{query.strip().lower()}%"
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.execute(
                "SELECT key, value FROM memories WHERE key LIKE ? OR value LIKE ?",
                (clean_query, clean_query),
            )
            rows = cursor.fetchall()

        if not rows:
            return f"No memories found matching '{query}'."

        results = [f"- {r[0]}: {r[1]}" for r in rows]
        return "Retrieved memories:\n" + "\n".join(results)
    except Exception as e:
        return f"Failed to recall memory: {e}"


def get_all_memories() -> str:
    """
    Returns all stored memories as context for Mark-1's system prompt.
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.execute("SELECT key, value FROM memories ORDER BY key ASC")
            rows = cursor.fetchall()

        if not rows:
            return "No persistent memories recorded yet."

        return "\n".join([f"- {r[0]}: {r[1]}" for r in rows])
    except Exception:
        return "No memories available."