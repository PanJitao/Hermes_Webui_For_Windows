"""Chat router - proxy to Hermes Agent's OpenAI-compatible API Server

Hermes exposes a streaming OpenAI-compatible endpoint at:
  POST http://127.0.0.1:8642/v1/chat/completions (with stream=true)

This router acts as a CORS-free proxy, forwarding SSE events to the frontend.
"""

import json
import os
import time
import uuid
import shutil
import httpx
import aiosqlite
from pathlib import Path
from fastapi import APIRouter, Request, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel

router = APIRouter()

HERMES_API_BASE = "http://127.0.0.1:8642"
WORKSPACE_DIR = Path(__file__).resolve().parent.parent / "workspace"


def _ensure_workspace() -> Path:
    WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)
    return WORKSPACE_DIR


def _get_hermes_home(request: Request) -> Path:
    return request.app.state.hermes_home


def _get_api_key(request: Request) -> str:
    """Read API_SERVER_KEY from .env or use a default"""
    env_path = _get_hermes_home(request) / ".env"
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("API_SERVER_KEY="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    return os.environ.get("API_SERVER_KEY", "")


class ChatMessage(BaseModel):
    message: str
    model: str | None = None
    session_id: str | None = None
    history: list[dict] | None = None


@router.get("/chat/status")
async def chat_status(request: Request):
    """Check if Hermes API Server is running"""
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(f"{HERMES_API_BASE}/health")
            if resp.status_code == 200:
                return {"running": True, "url": HERMES_API_BASE}
    except Exception:
        pass
    return {
        "running": False,
        "url": HERMES_API_BASE,
        "hint": "请先启动 Hermes Gateway: 运行 hermes gateway 或双击 03启动gateway.bat",
    }


@router.post("/chat")
async def send_chat(request: Request, body: ChatMessage):
    """Send a message via Hermes API Server with SSE streaming"""
    api_key = _get_api_key(request)
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    messages = []
    if body.history:
        for msg in body.history:
            messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})
    messages.append({"role": "user", "content": body.message})

    payload = {
        "model": body.model or "hermes-agent",
        "messages": messages,
        "stream": True,
    }

    async def event_stream():
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(300.0, connect=5.0)) as client:
                async with client.stream("POST", f"{HERMES_API_BASE}/v1/chat/completions", json=payload, headers=headers) as resp:
                    if resp.status_code != 200:
                        error_body = ""
                        async for chunk in resp.aiter_text():
                            error_body += chunk
                        yield f"data: {json.dumps({'type': 'error', 'message': f'API returned {resp.status_code}: {error_body[:500]}'})}\n\n"
                        return
                    buffer = ""
                    async for chunk in resp.aiter_text():
                        buffer += chunk
                        while "\n" in buffer:
                            line, buffer = buffer.split("\n", 1)
                            line = line.strip()
                            if not line:
                                continue
                            if line.startswith("data: "):
                                data_str = line[6:]
                                if data_str == "[DONE]":
                                    yield f"data: {json.dumps({'type': 'done'})}\n\n"
                                    return
                                try:
                                    data = json.loads(data_str)
                                    choices = data.get("choices", [])
                                    if choices:
                                        delta = choices[0].get("delta", {})
                                        content = delta.get("content", "")
                                        if content:
                                            yield f"data: {json.dumps({'type': 'delta', 'content': content})}\n\n"
                                        tool_calls = delta.get("tool_calls")
                                        if tool_calls:
                                            for tc in tool_calls:
                                                yield f"data: {json.dumps({'type': 'tool_call', 'data': tc})}\n\n"
                                        finish = choices[0].get("finish_reason")
                                        if finish:
                                            yield f"data: {json.dumps({'type': 'finish', 'reason': finish})}\n\n"
                                    if "hermes" in data:
                                        yield f"data: {json.dumps({'type': 'progress', 'data': data['hermes']})}\n\n"
                                except json.JSONDecodeError:
                                    yield f"data: {json.dumps({'type': 'raw', 'text': data_str})}\n\n"
        except httpx.ConnectError:
            yield f"data: {json.dumps({'type': 'error', 'message': '无法连接到 Hermes API Server (localhost:8642)。请先启动 Hermes Gateway。'})}\n\n"
        except httpx.ReadTimeout:
            yield f"data: {json.dumps({'type': 'error', 'message': '请求超时，Hermes 可能正在处理中...'})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"},
    )


@router.get("/chat/hermes-path")
async def get_hermes_path():
    """Check hermes executable"""
    path = shutil.which("hermes")
    return {"found": path is not None, "path": path}


# ---------------------------------------------------------------------------
# Save conversation to state.db
# ---------------------------------------------------------------------------
@router.post("/chat/save-conversation")
async def save_conversation(request: Request, body: dict):
    """Save current WebUI conversation to state.db so it appears in history"""
    msgs = body.get("messages", [])
    if not msgs:
        return {"success": False, "reason": "no messages"}

    hermes_home = _get_hermes_home(request)
    db_path = hermes_home / "state.db"
    if not db_path.exists():
        return {"success": False, "reason": "state.db not found"}

    session_id = body.get("session_id") or f"webui-{uuid.uuid4().hex[:12]}"
    now = int(time.time())
    title = (body.get("title") or "").strip() or (msgs[0].get("content", "")[:60] if msgs else "WebUI对话")

    try:
        db = await aiosqlite.connect(str(db_path))
        cursor = await db.execute("SELECT id FROM sessions WHERE id = ?", (session_id,))
        existing = await cursor.fetchone()

        if not existing:
            await db.execute(
                "INSERT INTO sessions (id, source, user_id, model, title, started_at, ended_at, message_count) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (session_id, "webui", "webui", body.get("model", "hermes-agent"), title, now, now, len(msgs))
            )

        for i, m in enumerate(msgs):
            role = m.get("role", "user")
            content = m.get("text", m.get("content", ""))
            if not content:
                continue
            await db.execute(
                "INSERT INTO messages (session_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
                (session_id, role, content, now + i)
            )

        await db.execute("UPDATE sessions SET message_count = ?, ended_at = ? WHERE id = ?", (len(msgs), now, session_id))
        await db.commit()
        await db.close()
        return {"success": True, "session_id": session_id, "title": title}
    except Exception as e:
        return {"success": False, "reason": str(e)}


# ---------------------------------------------------------------------------
# File upload & workspace endpoints
# ---------------------------------------------------------------------------
@router.post("/chat/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload a file to the workspace directory for Hermes to access"""
    ws = _ensure_workspace()
    ts = int(time.time())
    dest = ws / f"{ts}_{file.filename or 'uploaded_file'}"
    content = await file.read()
    dest.write_bytes(content)
    return {
        "success": True,
        "filename": file.filename or "uploaded_file",
        "saved_path": str(dest),
        "size": len(content),
    }


@router.get("/chat/workspace")
async def list_workspace():
    ws = _ensure_workspace()
    files = []
    for f in sorted(ws.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True):
        if f.is_file():
            st = f.stat()
            files.append({
                "name": f.name, "path": str(f), "size": st.st_size,
                "size_human": _format_size(st.st_size),
                "modified": time.strftime("%m-%d %H:%M", time.localtime(st.st_mtime)),
                "is_new": (time.time() - st.st_mtime) < 300,
            })
    return {"workspace": str(ws), "files": files, "count": len(files)}


@router.get("/chat/workspace/{filename:path}")
async def get_workspace_file(filename: str):
    ws = _ensure_workspace()
    file_path = ws / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    try:
        file_path.resolve().relative_to(ws.resolve())
    except ValueError:
        raise HTTPException(status_code=403, detail="Access denied")
    return FileResponse(file_path, filename=file_path.name)


@router.delete("/chat/workspace/{filename:path}")
async def delete_workspace_file(filename: str):
    ws = _ensure_workspace()
    file_path = ws / filename
    try:
        file_path.resolve().relative_to(ws.resolve())
    except ValueError:
        raise HTTPException(status_code=403, detail="Access denied")
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    file_path.unlink()
    return {"success": True}


def _format_size(size: int) -> str:
    if size < 1024:
        return f"{size} B"
    elif size < 1048576:
        return f"{size / 1024:.1f} KB"
    return f"{size / 1048576:.1f} MB"
