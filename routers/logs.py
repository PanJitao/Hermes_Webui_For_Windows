"""Logs router - read log files from ~/.hermes/logs/"""

import os
from pathlib import Path
from datetime import datetime
from fastapi import APIRouter, Request, HTTPException

router = APIRouter()


def _get_hermes_home(request: Request) -> Path:
    return request.app.state.hermes_home


@router.get("/logs")
async def list_logs(request: Request):
    """List available log files"""
    hermes_home = _get_hermes_home(request)
    logs_dir = hermes_home / "logs"

    if not logs_dir.exists():
        return {"exists": False, "logs": []}

    logs = []
    for item in sorted(logs_dir.iterdir(), reverse=True):
        if item.is_file():
            stat = item.stat()
            logs.append({
                "name": item.name,
                "path": str(item),
                "size": stat.st_size,
                "size_human": _human_size(stat.st_size),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            })

    return {"exists": True, "total": len(logs), "logs": logs}


@router.get("/logs/{filename}")
async def get_log(request: Request, filename: str, tail: int = 500):
    """Read a log file (last N lines by default)"""
    hermes_home = _get_hermes_home(request)
    log_path = hermes_home / "logs" / filename

    # Security: prevent path traversal
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")

    if not log_path.exists():
        raise HTTPException(status_code=404, detail=f"Log file '{filename}' not found")

    try:
        with open(log_path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()

        total_lines = len(lines)
        # Return last N lines
        if tail > 0 and len(lines) > tail:
            lines = lines[-tail:]

        return {
            "filename": filename,
            "total_lines": total_lines,
            "returned_lines": len(lines),
            "truncated": total_lines > tail,
            "content": "".join(lines),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read log: {e}")


def _human_size(size: int) -> str:
    """Convert bytes to human-readable format"""
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"
