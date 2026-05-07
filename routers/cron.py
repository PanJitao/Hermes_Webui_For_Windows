"""Cron / scheduled tasks router - list and view cron jobs"""

import yaml
import json
from pathlib import Path
from datetime import datetime
from fastapi import APIRouter, Request, HTTPException

router = APIRouter()


def _get_hermes_home(request: Request) -> Path:
    return request.app.state.hermes_home


def _parse_cron_file(filepath: Path) -> dict:
    """Parse a cron job YAML file"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        data["_filename"] = filepath.name
        data["_path"] = str(filepath)
        # Add file metadata
        stat = filepath.stat()
        data["_modified"] = datetime.fromtimestamp(stat.st_mtime).isoformat()
        data["_size"] = stat.st_size
        return data
    except Exception as e:
        return {
            "_filename": filepath.name,
            "_path": str(filepath),
            "_error": str(e),
        }


@router.get("/cron")
async def list_cron_jobs(request: Request):
    """List all cron jobs"""
    hermes_home = _get_hermes_home(request)
    cron_dir = hermes_home / "cron"

    if not cron_dir.exists():
        return {"exists": False, "jobs": []}

    jobs = []
    for item in sorted(cron_dir.iterdir()):
        if item.is_file() and item.suffix in (".yaml", ".yml", ".json"):
            jobs.append(_parse_cron_file(item))

    return {"exists": True, "total": len(jobs), "jobs": jobs}


@router.get("/cron/{filename}")
async def get_cron_job(request: Request, filename: str):
    """Get a specific cron job by filename"""
    hermes_home = _get_hermes_home(request)
    cron_dir = hermes_home / "cron"

    # Try exact match first
    filepath = cron_dir / filename
    if not filepath.exists():
        # Try adding .yaml extension
        filepath = cron_dir / f"{filename}.yaml"
    if not filepath.exists():
        # Try adding .yml extension
        filepath = cron_dir / f"{filename}.yml"
    if not filepath.exists():
        raise HTTPException(status_code=404, detail=f"Cron job '{filename}' not found")

    return _parse_cron_file(filepath)
