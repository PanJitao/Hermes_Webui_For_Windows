"""
Hermes Agent WebUI - 管理面板后端
基于 FastAPI，直接读取 Hermes 数据目录

⚠️  Windows 原生环境专用
本 WebUI 专为 Windows 环境下的 Hermes Agent 设计
其他平台可能需要手动适配路径
"""

import os
import sys
import uvicorn
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# ---------------------------------------------------------------------------
# Windows 原生环境检测
# ---------------------------------------------------------------------------
if sys.platform != 'win32':
    print("=" * 60)
    print("⚠️  警告: 当前不是 Windows 环境")
    print("本 WebUI 专为 Windows 原生 Hermes 设计")
    print("继续运行可能导致路径问题，建议检查兼容性")
    print("=" * 60)
    print()


from routers import config as config_router
from routers import conversations as conv_router
from routers import skills as skills_router
from routers import cron as cron_router
from routers import chat as chat_router
from routers import logs as logs_router

# ---------------------------------------------------------------------------
# Hermes home directory detection - 启动时交互式配置
# Priority: HERMES_ENV > user input > known install paths
# ---------------------------------------------------------------------------
def _prompt_hermes_path() -> Path:
    """启动时交互式提示用户指定 Hermes 目录"""
    print("\n" + "=" * 60)
    print("Hermes Agent WebUI - 目录配置")
    print("=" * 60)
    
    # 尝试自动检测
    auto_paths = [
        Path.home() / ".hermes",
        Path(r"D:\Windows_Hermes\hermes-agent-windows\.hermes"),
        Path(r"C:\Windows_Hermes\hermes-agent-windows\.hermes"),
    ]
    
    detected = []
    for p in auto_paths:
        if p.exists() and (p / "config.yaml").exists():
            detected.append(p)
    
    if detected:
        print("\n✓ 检测到以下 Hermes 目录:")
        for i, p in enumerate(detected, 1):
            print(f"  [{i}] {p}")
        print("  [0] 手动输入其他路径")
        
        while True:
            choice = input("\n请选择 [0-{}]: ".format(len(detected))).strip()
            if choice == "0":
                break
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(detected):
                    print(f"✓ 使用目录: {detected[idx]}\n")
                    return detected[idx]
            except:
                pass
            print("无效选择，请重试")
    else:
        print("\n⚠️  未自动检测到 Hermes 目录")
    
    # 手动输入
    while True:
        path_str = input("\n请输入 Hermes 目录路径 (含 config.yaml): ").strip()
        if not path_str:
            print("路径不能为空，请重试")
            continue
        
        path = Path(path_str)
        if not path.exists():
            print(f"⚠️  路径不存在: {path}")
            continue
        if not (path / "config.yaml").exists():
            print(f"⚠️  该目录下未找到 config.yaml")
            cont = input("是否仍要继续? (y/N): ").strip().lower()
            if cont != 'y':
                continue
        
        print(f"✓ 使用目录: {path}\n")
        return path


def _detect_hermes_home() -> Path:
    """检测 Hermes 目录：环境变量 > 自动检测 > 交互式提示"""
    # 1. 环境变量最高优先级
    env = os.environ.get("HERMES_HOME")
    if env:
        path = Path(env)
        if path.exists():
            print(f"✓ 从环境变量 HERMES_HOME 加载: {path}\n")
            return path
        print(f"⚠️  HERMES_HOME 指向的路径不存在: {env}")

    # 2. 自动检测已知路径
    auto_paths = [
        Path.home() / ".hermes",
        Path(r"D:\Windows_Hermes\hermes-agent-windows\.hermes"),
        Path(r"C:\Windows_Hermes\hermes-agent-windows\.hermes"),
    ]
    for p in auto_paths:
        if p.exists() and (p / "config.yaml").exists():
            print(f"✓ 自动检测到 Hermes 目录: {p}\n")
            return p

    # 3. 交互式提示（仅当有终端时）
    try:
        return _prompt_hermes_path()
    except (EOFError, OSError):
        # 非交互式环境（如后台启动），回退到默认路径
        fallback = Path.home() / ".hermes"
        print(f"⚠️  非交互式启动，使用默认路径: {fallback}\n")
        return fallback


HERMES_HOME = _detect_hermes_home()

# 确保目录存在
HERMES_HOME.mkdir(parents=True, exist_ok=True)


app = FastAPI(
    title="Hermes Agent WebUI",
    version="1.0.0",
    description="Hermes Agent 管理面板 - 配置、对话、技能、定时任务一站式管理",
)

# CORS - 允许本地开发
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Inject HERMES_HOME into app state so routers can access it
# ---------------------------------------------------------------------------
app.state.hermes_home = HERMES_HOME

# ---------------------------------------------------------------------------
# Register routers
# ---------------------------------------------------------------------------
app.include_router(config_router.router, prefix="/api", tags=["config"])
app.include_router(conv_router.router, prefix="/api", tags=["conversations"])
app.include_router(skills_router.router, prefix="/api", tags=["skills"])
app.include_router(cron_router.router, prefix="/api", tags=["cron"])
app.include_router(chat_router.router, prefix="/api", tags=["chat"])
app.include_router(logs_router.router, prefix="/api", tags=["logs"])

# ---------------------------------------------------------------------------
# Serve static frontend
# ---------------------------------------------------------------------------
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/")
async def root():
    """Serve the single-page frontend"""
    index_path = static_dir / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return {"message": "Hermes Agent WebUI is running. Place index.html in static/"}


@app.get("/api/status")
async def get_status():
    """System status overview for the dashboard"""
    hermes_home = app.state.hermes_home
    hermes_repo = hermes_home / "hermes-agent"

    status = {
        "hermes_home": str(hermes_home),
        "hermes_home_exists": hermes_home.exists(),
        "hermes_repo_exists": hermes_repo.exists(),
        "config_yaml_exists": (hermes_home / "config.yaml").exists(),
        "env_exists": (hermes_home / ".env").exists(),
        "state_db_exists": (hermes_home / "state.db").exists(),
        "skills_dir_exists": (hermes_home / "skills").exists(),
        "cron_dir_exists": (hermes_home / "cron").exists(),
        "logs_dir_exists": (hermes_home / "logs").exists(),
        "soul_md_exists": (hermes_home / "SOUL.md").exists(),
    }

    # Read current model from config.yaml
    config_path = hermes_home / "config.yaml"
    if config_path.exists():
        try:
            import yaml
            with open(config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f) or {}
            model_cfg = config.get("model", {})
            status["current_model"] = model_cfg.get("default", "not set")
            status["context_length"] = model_cfg.get("context_length", None)
        except Exception as e:
            status["config_error"] = str(e)

    # Count skills (nested: skills/{category}/{skill-name}/SKILL.md)
    skills_dir = hermes_home / "skills"
    if skills_dir.exists():
        count = 0
        for category_dir in skills_dir.iterdir():
            if not category_dir.is_dir():
                continue
            # Check if this is a category with sub-skills
            subdirs = [d for d in category_dir.iterdir() if d.is_dir()]
            if subdirs:
                count += len([d for d in subdirs if (d / "SKILL.md").exists()])
            elif (category_dir / "SKILL.md").exists():
                count += 1
        status["skill_count"] = count

    # Count cron jobs
    cron_dir = hermes_home / "cron"
    if cron_dir.exists():
        status["cron_count"] = len(list(cron_dir.glob("*.yaml")))

    # Count conversations (sessions in state.db)
    state_db = hermes_home / "state.db"
    if state_db.exists():
        try:
            import aiosqlite
            async with aiosqlite.connect(str(state_db)) as db:
                # Try common table names for sessions
                cursor = await db.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                )
                tables = [row[0] async for row in cursor]
                status["db_tables"] = tables

                if "sessions" in tables:
                    cursor = await db.execute("SELECT COUNT(*) FROM sessions")
                    row = await cursor.fetchone()
                    status["session_count"] = row[0] if row else 0
                elif "conversations" in tables:
                    cursor = await db.execute("SELECT COUNT(*) FROM conversations")
                    row = await cursor.fetchone()
                    status["session_count"] = row[0] if row else 0
        except Exception as e:
            status["db_error"] = str(e)

    return status


# ---------------------------------------------------------------------------
# Health monitor endpoint - checks WebUI + Hermes API Server
# ---------------------------------------------------------------------------
@app.get("/api/health/monitor")
async def health_monitor():
    import time, httpx
    result = {
        "webui": "ok",
        "gateway": "unknown",
        "gateway_url": "http://127.0.0.1:8642",
        "timestamp": time.time(),
    }
    try:
        async with httpx.AsyncClient(timeout=4.0) as client:
            resp = await client.get("http://127.0.0.1:8642/health")
            if resp.status_code == 200:
                result["gateway"] = "connected"
            else:
                result["gateway"] = f"error_{resp.status_code}"
    except httpx.ConnectError:
        result["gateway"] = "disconnected"
    except httpx.ReadTimeout:
        result["gateway"] = "timeout"
    except Exception as e:
        result["gateway"] = f"error:{str(e)[:60]}"
    return result


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("WEBUI_PORT", 8686))
    print(f"\n  Hermes Agent WebUI")
    print(f"  http://localhost:{port}\n")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
