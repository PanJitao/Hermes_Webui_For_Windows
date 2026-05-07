# Hermes Agent WebUI

Hermes Agent 的现代化 Web 管理面板，提供一站式配置管理、对话管理、技能管理等功能。

⚠️ **Windows 原生环境专用** — 本 WebUI 专为 Windows 环境下的 Hermes Agent 设计

## 功能特性

- **仪表盘** — 实时查看 Hermes Agent 运行状态、模型信息、对话统计
- **配置管理** — 可视化编辑 config.yaml 结构化配置，支持自定义模型提供商管理
- **对话历史** — 浏览搜索历史对话，支持查看完整消息链
- **在线对话** — 与 Hermes Agent 实时聊天，支持 Markdown 渲染、代码高亮、文件上传
- **技能管理** — 查看、搜索、编辑 SKILL.md 技能文件，支持分类筛选
- **定时任务** — 查看和管理 Cron 定时任务
- **日志查看** — 实时查看 Hermes Agent 运行日志
- **服务监控** — 实时检测 Gateway 连接状态，断连自动提醒

## 技术栈

- **后端**: Python + FastAPI
- **前端**: Alpine.js + Tailwind CSS（纯静态，无构建步骤）
- **通信**: REST API + SSE 流式输出

## 快速开始

### 环境要求

- Python 3.10+
- Hermes Agent 已安装（可选，WebUI 可独立运行查看配置）

### 安装

```bash
# 克隆项目
git clone <repo-url>
cd hermes-webui

# 安装依赖
pip install -r requirements.txt
```

### 启动

**Windows:**
```bash
start.bat
```

**macOS / Linux:**
```bash
chmod +x start.sh
./start.sh
```

**或者直接:**
```bash
python app.py
# 或指定端口
WEBUI_PORT=8080 python app.py
```

访问 http://localhost:8686

### 配置

复制 `.env.example` 为 `.env`，按需修改：

```bash
# Hermes 数据目录（自动检测 ~/.hermes，也可手动指定）
HERMES_HOME=/path/to/.hermes

# WebUI 端口（默认 8686）
WEBUI_PORT=8686
```

## 项目结构

```
hermes-webui/
├── app.py              # FastAPI 主入口
├── requirements.txt    # Python 依赖
├── start.bat           # Windows 启动脚本
├── start.sh            # macOS/Linux 启动脚本
├── .env.example        # 环境变量示例
├── routers/            # API 路由模块
│   ├── config.py       # 配置管理
│   ├── conversations.py # 对话历史
│   ├── chat.py         # 在线对话
│   ├── skills.py       # 技能管理
│   ├── cron.py         # 定时任务
│   └── logs.py         # 日志查看
├── static/             # 前端静态文件
│   ├── index.html      # 主页面（单页应用）
│   └── vendor/         # 第三方库（marked.js, highlight.js）
└── workspace/          # 文件上传目录（运行时创建）
```

## 跨平台支持

- **Windows**: 直接运行 `start.bat` 或 `python app.py`
- **macOS / Linux**: 运行 `./start.sh` 或 `python app.py`
- **Hermes 目录**: 自动检测 `~/.hermes`，也可通过 `HERMES_HOME` 环境变量指定

## 许可证

MIT License
