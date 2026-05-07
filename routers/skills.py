"""Skills management router - list, view, edit, import, enable/disable skills

Actual structure: skills/{category}/{skill-name}/SKILL.md
e.g. skills/software-development/hermes-development/SKILL.md
"""

import os
import re
import shutil
import yaml
from pathlib import Path
from fastapi import APIRouter, Request, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


def _get_hermes_home(request: Request) -> Path:
    return request.app.state.hermes_home


def _get_disabled_skills(hermes_home: Path) -> list:
    """Read disabled skills list from config.yaml"""
    config_path = hermes_home / "config.yaml"
    if not config_path.exists():
        return []
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}
        return config.get("skills", {}).get("disabled", [])
    except Exception:
        return []


def _save_disabled_skills(hermes_home: Path, disabled: list):
    """Save disabled skills list to config.yaml"""
    config_path = hermes_home / "config.yaml"
    config = {}
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}
    if "skills" not in config:
        config["skills"] = {}
    config["skills"]["disabled"] = disabled
    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)


def _parse_skill(skill_dir: Path, category: str = "") -> dict:
    """Parse a skill directory into a structured dict"""
    skill_md = skill_dir / "SKILL.md"
    info = {
        "name": skill_dir.name,
        "category": category,
        "path": str(skill_dir),
        "has_skill_md": skill_md.exists(),
        "files": [f.name for f in skill_dir.iterdir() if f.is_file()],
        "dirs": [d.name for d in skill_dir.iterdir() if d.is_dir()],
    }

    if skill_md.exists():
        content = skill_md.read_text(encoding="utf-8")
        info["content"] = content

        # Parse frontmatter if present
        fm_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if fm_match:
            try:
                frontmatter = yaml.safe_load(fm_match.group(1))
                if isinstance(frontmatter, dict):
                    info["frontmatter"] = frontmatter
                    info["title"] = frontmatter.get("title", frontmatter.get("name", skill_dir.name))
                    info["summary"] = frontmatter.get("summary", "")
                    info["description"] = frontmatter.get("description", "")
                    info["agent_created"] = frontmatter.get("agent_created", False)
                    info["triggers"] = frontmatter.get("triggers", [])
                    info["read_when"] = frontmatter.get("read_when", [])
            except Exception:
                pass

        # Extract title from first heading if no frontmatter title
        if "title" not in info:
            heading_match = re.search(r'^#\s+(.+)', content, re.MULTILINE)
            if heading_match:
                info["title"] = heading_match.group(1).strip()
            else:
                info["title"] = skill_dir.name

    return info


# ---------------------------------------------------------------------------
# List / Get
# ---------------------------------------------------------------------------

@router.get("/skills")
async def list_skills(request: Request):
    """List all installed skills (nested: skills/{category}/{skill-name}/)"""
    hermes_home = _get_hermes_home(request)
    skills_dir = hermes_home / "skills"

    if not skills_dir.exists():
        return {"exists": False, "skills": [], "categories": []}

    skills = []
    categories = []

    for category_dir in sorted(skills_dir.iterdir()):
        if not category_dir.is_dir():
            continue
        categories.append(category_dir.name)

        subdirs = [d for d in category_dir.iterdir() if d.is_dir()]
        skill_md = category_dir / "SKILL.md"

        if subdirs:
            for skill_dir in sorted(subdirs):
                skill_info = _parse_skill(skill_dir, category=category_dir.name)
                skills.append(skill_info)
        elif skill_md.exists():
            skill_info = _parse_skill(skill_dir)
            skill_info["category"] = category_dir.name
            skills.append(skill_info)

    # Read disabled skills
    disabled = _get_disabled_skills(hermes_home)
    for skill in skills:
        skill["enabled"] = skill["name"] not in disabled

    return {"exists": True, "total": len(skills), "categories": categories, "skills": skills}


@router.get("/skills/{category}/{name}")
async def get_skill(request: Request, category: str, name: str):
    """Get detailed info about a specific skill"""
    hermes_home = _get_hermes_home(request)
    skill_dir = hermes_home / "skills" / category / name

    if not skill_dir.exists():
        raise HTTPException(status_code=404, detail=f"Skill '{category}/{name}' not found")

    skill = _parse_skill(skill_dir, category=category)
    disabled = _get_disabled_skills(hermes_home)
    skill["enabled"] = skill["name"] not in disabled

    # List all files with sizes
    all_files = []
    for f in skill_dir.rglob("*"):
        if f.is_file():
            rel = f.relative_to(skill_dir)
            all_files.append({
                "path": str(rel),
                "size": f.stat().st_size,
            })
    skill["all_files"] = all_files

    return skill


# ---------------------------------------------------------------------------
# Edit SKILL.md content
# ---------------------------------------------------------------------------

class SkillContentUpdate(BaseModel):
    content: str


@router.put("/skills/{category}/{name}/content")
async def update_skill_content(request: Request, category: str, name: str, body: SkillContentUpdate):
    """Update the SKILL.md content"""
    hermes_home = _get_hermes_home(request)
    skill_dir = hermes_home / "skills" / category / name
    skill_md = skill_dir / "SKILL.md"

    if not skill_dir.exists():
        raise HTTPException(status_code=404, detail=f"Skill '{category}/{name}' not found")

    try:
        skill_md.write_text(body.content, encoding="utf-8")
        return {"success": True, "message": f"SKILL.md 已更新"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to write: {e}")


# ---------------------------------------------------------------------------
# Enable / Disable
# ---------------------------------------------------------------------------

class SkillToggle(BaseModel):
    enabled: bool


@router.put("/skills/{category}/{name}/toggle")
async def toggle_skill(request: Request, category: str, name: str, body: SkillToggle):
    """Enable or disable a skill by updating config.yaml"""
    hermes_home = _get_hermes_home(request)
    disabled = _get_disabled_skills(hermes_home)

    if body.enabled:
        disabled = [d for d in disabled if d != name]
    else:
        if name not in disabled:
            disabled.append(name)

    try:
        _save_disabled_skills(hermes_home, disabled)
        return {"success": True, "name": name, "enabled": body.enabled}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update config: {e}")


# ---------------------------------------------------------------------------
# Create / Import skill
# ---------------------------------------------------------------------------

class SkillCreate(BaseModel):
    category: str
    name: str
    content: str = ""
    title: str = ""


@router.post("/skills")
async def create_skill(request: Request, body: SkillCreate):
    """Create a new skill directory with SKILL.md"""
    hermes_home = _get_hermes_home(request)
    skill_dir = hermes_home / "skills" / body.category / body.name

    if skill_dir.exists():
        raise HTTPException(status_code=409, detail=f"Skill '{body.category}/{body.name}' already exists")

    try:
        skill_dir.mkdir(parents=True, exist_ok=True)

        content = body.content
        if not content:
            title = body.title or body.name
            content = f"""---
title: "{title}"
summary: ""
description: ""
agent_created: false
---

# {title}

> 在此编写技能描述和使用说明

## 使用场景

## 步骤

## 注意事项
"""
        (skill_dir / "SKILL.md").write_text(content, encoding="utf-8")

        return {
            "success": True,
            "skill": _parse_skill(skill_dir, category=body.category),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create skill: {e}")


# ---------------------------------------------------------------------------
# Import skill from ZIP / folder upload
# ---------------------------------------------------------------------------

@router.post("/skills/import")
async def import_skill(
    request: Request,
    category: str = Form(...),
    name: str = Form(...),
    file: UploadFile = File(...),
):
    """Import a skill from a ZIP file"""
    hermes_home = _get_hermes_home(request)
    skill_dir = hermes_home / "skills" / category / name

    if skill_dir.exists():
        raise HTTPException(status_code=409, detail=f"Skill '{category}/{name}' already exists")

    import zipfile
    import io
    import tempfile

    try:
        skill_dir.mkdir(parents=True, exist_ok=True)

        # Read uploaded file
        content = await file.read()

        # Try to extract as ZIP
        if zipfile.is_zipfile(io.BytesIO(content)):
            with zipfile.ZipFile(io.BytesIO(content)) as zf:
                for member in zf.namelist():
                    # Skip __MACOSX and hidden files
                    if member.startswith("__MACOSX") or "/." in member:
                        continue
                    # Extract to skill dir
                    target = skill_dir / member
                    if member.endswith("/"):
                        target.mkdir(parents=True, exist_ok=True)
                    else:
                        target.parent.mkdir(parents=True, exist_ok=True)
                        with open(target, "wb") as f:
                            f.write(zf.read(member))
        else:
            # Assume it's a raw SKILL.md file
            (skill_dir / "SKILL.md").write_bytes(content)

        return {
            "success": True,
            "message": f"已导入到 {category}/{name}",
            "skill": _parse_skill(skill_dir, category=category),
        }
    except HTTPException:
        raise
    except Exception as e:
        # Cleanup on failure
        if skill_dir.exists():
            shutil.rmtree(skill_dir, ignore_errors=True)
        raise HTTPException(status_code=500, detail=f"Import failed: {e}")


# ---------------------------------------------------------------------------
# Delete skill
# ---------------------------------------------------------------------------

@router.delete("/skills/{category}/{name}")
async def delete_skill(request: Request, category: str, name: str):
    """Delete a skill directory"""
    hermes_home = _get_hermes_home(request)
    skill_dir = hermes_home / "skills" / category / name

    if not skill_dir.exists():
        raise HTTPException(status_code=404, detail=f"Skill '{category}/{name}' not found")

    try:
        shutil.rmtree(skill_dir)
        # Also remove from disabled list
        disabled = _get_disabled_skills(hermes_home)
        disabled = [d for d in disabled if d != name]
        _save_disabled_skills(hermes_home, disabled)
        return {"success": True, "message": f"已删除 {category}/{name}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete: {e}")


# ---------------------------------------------------------------------------
# List files in a skill (for editing)
# ---------------------------------------------------------------------------

@router.get("/skills/{category}/{name}/files/{filepath:path}")
async def get_skill_file(request: Request, category: str, name: str, filepath: str):
    """Read a specific file in a skill directory"""
    hermes_home = _get_hermes_home(request)
    file_path = hermes_home / "skills" / category / name / filepath

    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"File not found: {filepath}")
    if not file_path.is_file():
        raise HTTPException(status_code=400, detail="Not a file")

    # Security: prevent path traversal
    try:
        file_path.resolve().relative_to((hermes_home / "skills" / category / name).resolve())
    except ValueError:
        raise HTTPException(status_code=403, detail="Path traversal not allowed")

    try:
        content = file_path.read_text(encoding="utf-8")
        return {"path": filepath, "content": content, "size": file_path.stat().st_size}
    except UnicodeDecodeError:
        return {"path": filepath, "content": "[Binary file]", "size": file_path.stat().st_size, "binary": True}


class FileUpdate(BaseModel):
    content: str


@router.put("/skills/{category}/{name}/files/{filepath:path}")
async def update_skill_file(request: Request, category: str, name: str, filepath: str, body: FileUpdate):
    """Update a specific file in a skill directory"""
    hermes_home = _get_hermes_home(request)
    file_path = hermes_home / "skills" / category / name / filepath

    # Security check
    skill_root = hermes_home / "skills" / category / name
    try:
        file_path.resolve().relative_to(skill_root.resolve())
    except ValueError:
        raise HTTPException(status_code=403, detail="Path traversal not allowed")

    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(body.content, encoding="utf-8")
        return {"success": True, "message": f"已更新 {filepath}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to write: {e}")
