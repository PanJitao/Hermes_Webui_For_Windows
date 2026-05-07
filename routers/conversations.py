"""Conversations router - reads session history from state.db (SQLite)

Actual schema (hermes-agent-windows):
  sessions: id, source, user_id, model, title, started_at, ended_at, message_count,
            tool_call_count, input_tokens, output_tokens, estimated_cost_usd, ...
  messages: id, session_id, role, content, tool_call_id, tool_calls, tool_name,
            timestamp, token_count, reasoning, ...
"""

import json
import time
import aiosqlite
from pathlib import Path
from fastapi import APIRouter, Request, HTTPException
from typing import Optional
from pydantic import BaseModel

router = APIRouter()


def _get_hermes_home(request: Request) -> Path:
    return request.app.state.hermes_home


async def _get_db(hermes_home: Path):
    db_path = hermes_home / "state.db"
    if not db_path.exists():
        return None
    return await aiosqlite.connect(str(db_path))


async def _discover_tables(db):
    cursor = await db.execute("SELECT name FROM sqlite_master WHERE type='table'")
    return [row[0] async for row in cursor]


@router.get("/conversations")
async def list_conversations(
    request: Request,
    limit: int = 50,
    offset: int = 0,
    search: Optional[str] = None,
):
    """List all sessions with summary info"""
    hermes_home = _get_hermes_home(request)
    db = await _get_db(hermes_home)
    if db is None:
        return {"exists": False, "conversations": []}

    try:
        tables = await _discover_tables(db)

        if "sessions" in tables:
            # Full query with message preview
            query = """
                SELECT s.*,
                       (SELECT content FROM messages m
                        WHERE m.session_id = s.id AND m.role = 'user'
                        ORDER BY m.timestamp ASC LIMIT 1) as first_user_msg
                FROM sessions s
            """
            params = []
            if search:
                query += " WHERE s.title LIKE ? OR s.model LIKE ? OR first_user_msg LIKE ?"
                like = f"%{search}%"
                params = [like, like, like]

            query += " ORDER BY COALESCE(s.started_at, 0) DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])

            cursor = await db.execute(query, params)
            cols = [d[0] for d in cursor.description]
            rows = [dict(zip(cols, row)) async for row in cursor]

            # Count total
            count_query = "SELECT COUNT(*) FROM sessions s"
            count_params = []
            if search:
                count_query += " WHERE s.title LIKE ? OR s.model LIKE ?"
                like = f"%{search}%"
                count_params = [like, like]
            cursor = await db.execute(count_query, count_params)
            total = (await cursor.fetchone())[0]

            return {"exists": True, "table": "sessions", "total": total, "conversations": rows}

        else:
            return {
                "exists": True,
                "tables": tables,
                "conversations": [],
                "hint": "No sessions table found. Tables: " + ", ".join(tables),
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    finally:
        await db.close()


@router.get("/conversations/{session_id}")
async def get_conversation(request: Request, session_id: str, limit: int = 500):
    """Get session detail + messages"""
    hermes_home = _get_hermes_home(request)
    db = await _get_db(hermes_home)
    if db is None:
        raise HTTPException(status_code=404, detail="state.db not found")

    try:
        # Get session info
        cursor = await db.execute(
            "SELECT * FROM sessions WHERE id = ?", (session_id,)
        )
        cols = [d[0] for d in cursor.description]
        row = await cursor.fetchone()
        session = dict(zip(cols, row)) if row else None

        # Get messages
        cursor = await db.execute(
            """SELECT id, session_id, role, content, tool_call_id, tool_calls,
                      tool_name, timestamp, token_count, finish_reason, reasoning
               FROM messages WHERE session_id = ?
               ORDER BY timestamp ASC, id ASC LIMIT ?""",
            (session_id, limit)
        )
        msg_cols = [d[0] for d in cursor.description]
        messages = [dict(zip(msg_cols, r)) async for r in cursor]

        # Count total messages for this session
        cursor = await db.execute(
            "SELECT COUNT(*) FROM messages WHERE session_id = ?", (session_id,)
        )
        total_msgs = (await cursor.fetchone())[0]

        return {
            "session": session,
            "messages": messages,
            "total_messages": total_msgs,
            "returned_messages": len(messages),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    finally:
        await db.close()


@router.get("/conversations/db/schema")
async def get_db_schema(request: Request):
    """Inspect the database schema"""
    hermes_home = _get_hermes_home(request)
    db = await _get_db(hermes_home)
    if db is None:
        return {"exists": False}

    try:
        tables = await _discover_tables(db)
        schema = {}
        for table in tables:
            if table.startswith("messages_fts") or table == "sqlite_sequence":
                continue  # skip FTS internal tables
            cursor = await db.execute(f"PRAGMA table_info({table})")
            cols = [{"name": row[1], "type": row[2], "notnull": row[3], "pk": row[5]}
                    async for row in cursor]
            cursor = await db.execute(f"SELECT COUNT(*) FROM {table}")
            count = (await cursor.fetchone())[0]
            schema[table] = {"columns": cols, "row_count": count}
        return {"exists": True, "tables": schema}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Schema error: {e}")
    finally:
        await db.close()


class RenameRequest(BaseModel):
    title: str


@router.put("/conversations/{session_id}/rename")
async def rename_conversation(request: Request, session_id: str, body: RenameRequest):
    """Rename a conversation session"""
    hermes_home = _get_hermes_home(request)
    db = await _get_db(hermes_home)
    if db is None:
        raise HTTPException(status_code=404, detail="state.db not found")

    try:
        await db.execute("UPDATE sessions SET title = ? WHERE id = ?", (body.title, session_id))
        await db.commit()
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Rename error: {e}")
    finally:
        await db.close()
