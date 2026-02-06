"""SQLite database storage for conversations and messages."""

import sqlite3
import uuid
from datetime import datetime
from typing import Optional
from oaichat.config import get_db_path
from oaichat.core.models import Conversation, Message


def get_connection() -> sqlite3.Connection:
    """Get a database connection with proper settings."""
    db_path = get_db_path()
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    
    # Check if tables exist by querying sqlite_master
    # We only check for 'conversations' table since _create_tables() is idempotent
    # and creates all tables together using CREATE TABLE IF NOT EXISTS
    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='conversations'"
    )
    if not cursor.fetchone():
        _create_tables(conn)
    
    return conn


def _create_tables(conn: sqlite3.Connection) -> None:
    """Create database tables if they don't exist."""
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            profile TEXT NOT NULL,
            model TEXT NOT NULL,
            title TEXT,
            system_prompt TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            token_usage_prompt INTEGER,
            token_usage_completion INTEGER,
            created_at TEXT NOT NULL,
            FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_messages_conversation
            ON messages(conversation_id);

        CREATE INDEX IF NOT EXISTS idx_conversations_updated
            ON conversations(updated_at DESC);

        CREATE INDEX IF NOT EXISTS idx_conversations_profile
            ON conversations(profile);
    """)


def create_conversation(profile: str, model: str, system_prompt: Optional[str] = None) -> Conversation:
    """Create a new conversation."""
    conversation_id = str(uuid.uuid4())
    now = datetime.now()

    with get_connection() as conn:
        conn.execute(
            "INSERT INTO conversations (id, profile, model, title, system_prompt, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (conversation_id, profile, model, None, system_prompt, now.isoformat(), now.isoformat()),
        )

    return Conversation(
        id=conversation_id,
        profile=profile,
        model=model,
        system_prompt=system_prompt,
        created_at=now,
        updated_at=now,
    )


def add_message(
    conversation_id: str,
    role: str,
    content: str,
    token_usage_prompt: Optional[int] = None,
    token_usage_completion: Optional[int] = None,
) -> Message:
    """Add a message to a conversation."""
    now = datetime.now()

    with get_connection() as conn:
        conn.execute(
            "INSERT INTO messages (conversation_id, role, content, token_usage_prompt, "
            "token_usage_completion, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (conversation_id, role, content, token_usage_prompt, token_usage_completion, now.isoformat()),
        )
        conn.execute(
            "UPDATE conversations SET updated_at = ? WHERE id = ?",
            (now.isoformat(), conversation_id),
        )

    return Message(
        role=role,
        content=content,
        token_usage_prompt=token_usage_prompt,
        token_usage_completion=token_usage_completion,
        created_at=now,
    )


def get_conversation(conversation_id: str) -> Optional[Conversation]:
    """Get a conversation by ID with all its messages."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM conversations WHERE id = ?", (conversation_id,)
        ).fetchone()

        if not row:
            return None

        message_rows = conn.execute(
            "SELECT * FROM messages WHERE conversation_id = ? ORDER BY created_at ASC",
            (conversation_id,),
        ).fetchall()

    messages = [
        Message(
            role=msg["role"],
            content=msg["content"],
            token_usage_prompt=msg["token_usage_prompt"],
            token_usage_completion=msg["token_usage_completion"],
            created_at=datetime.fromisoformat(msg["created_at"]),
        )
        for msg in message_rows
    ]

    return Conversation(
        id=row["id"],
        profile=row["profile"],
        model=row["model"],
        title=row["title"],
        system_prompt=row["system_prompt"],
        messages=messages,
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
    )


def list_conversations(
    profile: Optional[str] = None,
    limit: int = 20,
    search: Optional[str] = None,
) -> list[Conversation]:
    """List conversations, optionally filtered by profile and/or search term."""
    with get_connection() as conn:
        query = """
            SELECT c.*, COUNT(m.id) as message_count
            FROM conversations c
            LEFT JOIN messages m ON c.id = m.conversation_id
        """
        conditions: list[str] = []
        params: list = []

        if profile:
            conditions.append("c.profile = ?")
            params.append(profile)

        if search:
            conditions.append("(c.title LIKE ? OR c.id LIKE ?)")
            params.extend([f"%{search}%", f"%{search}%"])

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " GROUP BY c.id ORDER BY c.updated_at DESC LIMIT ?"
        params.append(limit)

        rows = conn.execute(query, params).fetchall()

    conversations = []
    for row in rows:
        conv = Conversation(
            id=row["id"],
            profile=row["profile"],
            model=row["model"],
            title=row["title"],
            system_prompt=row["system_prompt"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )
        conversations.append(conv)

    return conversations


def delete_conversation(conversation_id: str) -> bool:
    """Delete a conversation and all its messages (via CASCADE)."""
    with get_connection() as conn:
        cursor = conn.execute(
            "DELETE FROM conversations WHERE id = ?", (conversation_id,)
        )
        return cursor.rowcount > 0


def delete_messages(conversation_id: str) -> int:
    """Delete all messages in a conversation. Returns count deleted."""
    with get_connection() as conn:
        cursor = conn.execute(
            "DELETE FROM messages WHERE conversation_id = ?", (conversation_id,)
        )
        return cursor.rowcount


def update_title(conversation_id: str, title: str) -> bool:
    """Update the title of a conversation."""
    with get_connection() as conn:
        cursor = conn.execute(
            "UPDATE conversations SET title = ? WHERE id = ?",
            (title, conversation_id),
        )
        return cursor.rowcount > 0


def update_conversation_model(conversation_id: str, model: str) -> bool:
    """Update the model of a conversation."""
    with get_connection() as conn:
        cursor = conn.execute(
            "UPDATE conversations SET model = ? WHERE id = ?",
            (model, conversation_id),
        )
        return cursor.rowcount > 0


def update_conversation_system_prompt(conversation_id: str, system_prompt: Optional[str]) -> bool:
    """Update the system prompt of a conversation."""
    with get_connection() as conn:
        cursor = conn.execute(
            "UPDATE conversations SET system_prompt = ? WHERE id = ?",
            (system_prompt, conversation_id),
        )
        return cursor.rowcount > 0


def get_message_count(conversation_id: str) -> int:
    """Get the number of messages in a conversation."""
    with get_connection() as conn:
        result = conn.execute(
            "SELECT COUNT(*) as count FROM messages WHERE conversation_id = ?",
            (conversation_id,),
        ).fetchone()
    return result["count"] if result else 0


def find_conversation_by_prefix(prefix: str) -> Optional[Conversation]:
    """Find a conversation by ID prefix using efficient SQL LIKE."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id FROM conversations WHERE id LIKE ? ORDER BY updated_at DESC LIMIT 1",
            (prefix + "%",),
        ).fetchone()

    if not row:
        return None
    return get_conversation(row["id"])


def get_total_conversation_count(profile: Optional[str] = None) -> int:
    """Get total number of conversations."""
    with get_connection() as conn:
        if profile:
            row = conn.execute(
                "SELECT COUNT(*) as cnt FROM conversations WHERE profile = ?", (profile,)
            ).fetchone()
        else:
            row = conn.execute("SELECT COUNT(*) as cnt FROM conversations").fetchone()
    return row["cnt"] if row else 0
