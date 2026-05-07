"""Configuration management router - reads/writes config.yaml and .env"""

import os
import re
import yaml
from pathlib import Path
from typing import Any, Optional
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel

router = APIRouter()


# ---------------------------------------------------------------------------
# .env endpoints
# ---------------------------------------------------------------------------


def _get_hermes_home(request: Request) -> Path:
    return request.app.state.hermes_home


def _mask_value(key: str, value: str) -> str:
    """Mask sensitive values like API keys"""
    sensitive_patterns = [
        "KEY", "SECRET", "TOKEN", "PASSWORD", "PASSWD",
        "CREDENTIAL", "AUTH", "PRIVATE"
    ]
    key_upper = key.upper()
    if any(p in key_upper for p in sensitive_patterns):
        if len(value) <= 8:
            return "****"
        return value[:4] + "*" * (len(value) - 8) + value[-4:]
    return value


# ---------------------------------------------------------------------------
# config.yaml endpoints
# ---------------------------------------------------------------------------

@router.get("/config")
async def get_config(request: Request):
    """Read config.yaml"""
    config_path = _get_hermes_home(request) / "config.yaml"
    if not config_path.exists():
        return {"exists": False, "config": {}}
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            content = f.read()
        config = yaml.safe_load(content) or {}
        return {"exists": True, "config": config, "raw": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read config: {e}")


class ConfigUpdate(BaseModel):
    config: dict[str, Any]


@router.put("/config")
async def update_config(request: Request, body: ConfigUpdate):
    """Update config.yaml (merges with existing)"""
    config_path = _get_hermes_home(request) / "config.yaml"

    # Read existing
    existing = {}
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            existing = yaml.safe_load(f) or {}

    # Merge (shallow + nested)
    def deep_merge(base: dict, override: dict) -> dict:
        result = base.copy()
        for k, v in override.items():
            if k in result and isinstance(result[k], dict) and isinstance(v, dict):
                result[k] = deep_merge(result[k], v)
            else:
                result[k] = v
        return result

    merged = deep_merge(existing, body.config)

    try:
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(merged, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        return {"success": True, "config": merged}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to write config: {e}")


# Structured config section definitions
CONFIG_SECTIONS = [
    {
        "id": "model",
        "title": "模型配置",
        "icon": "🤖",
        "path": ["model"],
        "fields": [
            {"key": "default", "label": "默认模型", "type": "text"},
            {"key": "provider", "label": "提供商", "type": "select", "options": ["custom", "openrouter", "openai", "anthropic", "nous"]},
            {"key": "base_url", "label": "API Base URL", "type": "text"},
        ],
    },
    {
        "id": "custom_providers",
        "title": "自定义模型提供商",
        "icon": "🔌",
        "path": ["custom_providers"],
        "type": "list",
        "item_fields": [
            {"key": "name", "label": "名称"},
            {"key": "model", "label": "模型"},
            {"key": "base_url", "label": "API URL"},
        ],
    },
    {
        "id": "agent",
        "title": "Agent 行为",
        "icon": "⚙️",
        "path": ["agent"],
        "fields": [
            {"key": "max_turns", "label": "最大轮次", "type": "number"},
            {"key": "gateway_timeout", "label": "Gateway 超时(秒)", "type": "number"},
            {"key": "tool_use_enforcement", "label": "工具使用策略", "type": "select", "options": ["auto", "strict", "off"]},
        ],
    },
    {
        "id": "terminal",
        "title": "终端配置",
        "icon": "💻",
        "path": ["terminal"],
        "fields": [
            {"key": "backend", "label": "后端", "type": "select", "options": ["local", "docker", "ssh", "modal", "daytona"]},
            {"key": "timeout", "label": "超时(秒)", "type": "number"},
            {"key": "persistent_shell", "label": "持久 Shell", "type": "boolean"},
            {"key": "docker_image", "label": "Docker 镜像", "type": "text"},
        ],
    },
    {
        "id": "display",
        "title": "显示设置",
        "icon": "🎨",
        "path": ["display"],
        "fields": [
            {"key": "personality", "label": "个性", "type": "text"},
            {"key": "show_reasoning", "label": "显示推理过程", "type": "boolean"},
            {"key": "streaming", "label": "流式输出", "type": "boolean"},
            {"key": "show_cost", "label": "显示费用", "type": "boolean"},
            {"key": "skin", "label": "皮肤", "type": "text"},
            {"key": "tool_progress", "label": "工具进度", "type": "select", "options": ["off", "new", "all", "verbose"]},
            {"key": "compact", "label": "紧凑模式", "type": "boolean"},
            {"key": "inline_diffs", "label": "内联差异", "type": "boolean"},
        ],
    },
    {
        "id": "memory",
        "title": "记忆设置",
        "icon": "🧠",
        "path": ["memory"],
        "fields": [
            {"key": "memory_enabled", "label": "启用记忆", "type": "boolean"},
            {"key": "user_profile_enabled", "label": "启用用户画像", "type": "boolean"},
            {"key": "memory_char_limit", "label": "记忆字符限制", "type": "number"},
            {"key": "user_char_limit", "label": "用户画像字符限制", "type": "number"},
        ],
    },
    {
        "id": "browser",
        "title": "浏览器设置",
        "icon": "🌐",
        "path": ["browser"],
        "fields": [
            {"key": "inactivity_timeout", "label": "不活动超时(秒)", "type": "number"},
            {"key": "command_timeout", "label": "命令超时(秒)", "type": "number"},
            {"key": "record_sessions", "label": "录制会话", "type": "boolean"},
            {"key": "allow_private_urls", "label": "允许私有URL", "type": "boolean"},
        ],
    },
    {
        "id": "security",
        "title": "安全设置",
        "icon": "🔒",
        "path": ["security"],
        "fields": [
            {"key": "redact_secrets", "label": "脱敏密钥", "type": "boolean"},
            {"key": "tirith_enabled", "label": "启用 Tirith", "type": "boolean"},
            {"key": "tirith_fail_open", "label": "Tirith 失败放行", "type": "boolean"},
        ],
    },
    {
        "id": "checkpoints",
        "title": "检查点",
        "icon": "📸",
        "path": ["checkpoints"],
        "fields": [
            {"key": "enabled", "label": "启用", "type": "boolean"},
            {"key": "max_snapshots", "label": "最大快照数", "type": "number"},
        ],
    },
    {
        "id": "compression",
        "title": "压缩设置",
        "icon": "📦",
        "path": ["compression"],
        "fields": [
            {"key": "enabled", "label": "启用", "type": "boolean"},
            {"key": "threshold", "label": "触发阈值", "type": "number"},
            {"key": "target_ratio", "label": "目标压缩比", "type": "number"},
            {"key": "protect_last_n", "label": "保护最后N条", "type": "number"},
        ],
    },
    {
        "id": "tts",
        "title": "语音合成 (TTS)",
        "icon": "🔊",
        "path": ["tts"],
        "fields": [
            {"key": "provider", "label": "TTS 提供商", "type": "select", "options": ["edge", "elevenlabs", "openai", "mistral"]},
        ],
    },
    {
        "id": "privacy",
        "title": "隐私设置",
        "icon": "🛡️",
        "path": ["privacy"],
        "fields": [
            {"key": "redact_pii", "label": "脱敏个人信息", "type": "boolean"},
        ],
    },
    {
        "id": "session",
        "title": "会话重置",
        "icon": "🔄",
        "path": ["session_reset"],
        "fields": [
            {"key": "mode", "label": "重置模式", "type": "select", "options": ["off", "idle", "scheduled", "both"]},
            {"key": "at_hour", "label": "重置时间(小时)", "type": "number"},
            {"key": "idle_minutes", "label": "空闲重置(分钟)", "type": "number"},
        ],
    },
]


@router.get("/config/structured")
async def get_structured_config(request: Request):
    """Read config.yaml and return structured sections"""
    config_path = _get_hermes_home(request) / "config.yaml"
    if not config_path.exists():
        return {"exists": False, "sections": []}

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read config: {e}")

    sections = []
    for sec_def in CONFIG_SECTIONS:
        # Navigate to the nested value
        value = config
        for key in sec_def["path"]:
            if isinstance(value, dict):
                value = value.get(key, {})
            else:
                value = {}
                break

        sections.append({
            "id": sec_def["id"],
            "title": sec_def["title"],
            "icon": sec_def["icon"],
            "fields": sec_def.get("fields", []),
            "type": sec_def.get("type", "object"),
            "item_fields": sec_def.get("item_fields", []),
            "value": value if value else {},
            "path": sec_def["path"],
        })

    # Also include top-level "other" keys not covered by any section
    covered_keys = set()
    for sec_def in CONFIG_SECTIONS:
        covered_keys.add(sec_def["path"][0])
    other = {k: v for k, v in config.items() if k not in covered_keys}
    sections.append({
        "id": "other",
        "title": "其他配置",
        "icon": "📄",
        "fields": [],
        "type": "raw",
        "value": other,
        "path": [],
    })

    return {"exists": True, "sections": sections}


class SectionUpdate(BaseModel):
    section_id: str
    path: list[str]
    value: Any


@router.put("/config/section")
async def update_config_section(request: Request, body: SectionUpdate):
    """Update a specific config section"""
    config_path = _get_hermes_home(request) / "config.yaml"

    existing = {}
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            existing = yaml.safe_load(f) or {}

    # Navigate to the parent and set the value
    if body.path:
        target = existing
        for key in body.path[:-1]:
            if key not in target or not isinstance(target[key], dict):
                target[key] = {}
            target = target[key]
        target[body.path[-1]] = body.value
    else:
        # Top-level merge
        existing.update(body.value)

    try:
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(existing, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to write config: {e}")


# ---------------------------------------------------------------------------
# .env endpoints
# ---------------------------------------------------------------------------

@router.get("/config/env")
async def get_env(request: Request):
    """Read .env file with sensitive values masked"""
    env_path = _get_hermes_home(request) / ".env"
    if not env_path.exists():
        return {"exists": False, "variables": []}

    variables = []
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                variables.append({
                    "key": key,
                    "value": _mask_value(key, value),
                    "is_sensitive": _mask_value(key, value) != value,
                })

    return {"exists": True, "variables": variables}


class EnvUpdate(BaseModel):
    variables: dict[str, str]


@router.put("/config/env")
async def update_env(request: Request, body: EnvUpdate):
    """Update .env file (merges with existing)"""
    env_path = _get_hermes_home(request) / ".env"

    # Read existing
    existing: dict[str, str] = {}
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, _, value = line.partition("=")
                    existing[key.strip()] = value.strip().strip('"').strip("'")

    # Merge
    existing.update(body.variables)

    try:
        with open(env_path, "w", encoding="utf-8") as f:
            for key, value in existing.items():
                f.write(f"{key}={value}\n")
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to write .env: {e}")


# ---------------------------------------------------------------------------
# Model management endpoints
# ---------------------------------------------------------------------------

@router.get("/models")
async def list_models(request: Request):
    """List all available models from config.yaml (current + custom providers)"""
    config_path = _get_hermes_home(request) / "config.yaml"
    if not config_path.exists():
        return {"current": None, "providers": []}

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}

        model_cfg = config.get("model", {})
        current = model_cfg.get("default", None)

        # Collect custom providers
        providers = []
        for cp in config.get("custom_providers", []):
            providers.append({
                "name": cp.get("name", ""),
                "model": cp.get("model", ""),
                "base_url": cp.get("base_url", ""),
                "provider": "custom",
                "has_key": bool(cp.get("api_key")),
            })

        # Built-in provider info
        built_in = model_cfg.get("provider", "")
        built_in_model = model_cfg.get("default", "")

        return {
            "current": current,
            "provider": built_in,
            "base_url": model_cfg.get("base_url", ""),
            "providers": providers,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read models: {e}")


class ModelSwitch(BaseModel):
    model: str
    provider: str = "custom"
    base_url: str = ""
    api_key: str = ""


@router.put("/models/switch")
async def switch_model(request: Request, body: ModelSwitch):
    """Switch the active model in config.yaml"""
    config_path = _get_hermes_home(request) / "config.yaml"
    if not config_path.exists():
        raise HTTPException(status_code=404, detail="config.yaml not found")

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            content = f.read()
        config = yaml.safe_load(content) or {}

        # Update model section
        if "model" not in config:
            config["model"] = {}
        config["model"]["default"] = body.model
        config["model"]["provider"] = body.provider
        if body.base_url:
            config["model"]["base_url"] = body.base_url
        if body.api_key:
            config["model"]["api_key"] = body.api_key

        # Write back preserving raw format (use YAML dump)
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

        return {"success": True, "current_model": body.model, "provider": body.provider}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to switch model: {e}")


class ProviderAdd(BaseModel):
    name: str
    model: str
    base_url: str
    api_key: str = ""


@router.post("/models/providers")
async def add_provider(request: Request, body: ProviderAdd):
    """Add a new custom provider"""
    config_path = _get_hermes_home(request) / "config.yaml"
    if not config_path.exists():
        raise HTTPException(status_code=404, detail="config.yaml not found")

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f.read()) or {}

        if "custom_providers" not in config:
            config["custom_providers"] = []

        # Check for duplicate
        for cp in config["custom_providers"]:
            if cp.get("base_url") == body.base_url and cp.get("model") == body.model:
                raise HTTPException(status_code=409, detail="Provider already exists")

        new_provider = {
            "name": body.name,
            "base_url": body.base_url,
            "model": body.model,
        }
        if body.api_key:
            new_provider["api_key"] = body.api_key

        config["custom_providers"].append(new_provider)

        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

        return {"success": True, "providers": config["custom_providers"]}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add provider: {e}")
