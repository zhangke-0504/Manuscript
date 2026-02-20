# Manuscript — Quick Start

简体中文 / English (双语)

## 快速开始（普通用户）

1. 将 `backend/dist` 整个文件夹与本仓库根目录下的 `start.bat` 一并放到某台 Windows 电脑上。
2. 双击 `start.bat`：它会启动后端服务并自动在默认浏览器打开项目首页。
3. 打开页面后，进入 "API Key Settings"，选择供应商（`deepseek` 或 `openai`），粘贴你的 API Key，然后点击 Save。
   - DeepSeek 配置会保存到：`backend/config/deepseek/config.yaml`
   - OpenAI 配置会保存到：`backend/config/openai/config.yaml`
4. 保存成功后你会在页面右下角看到成功提示。随后在任意小说页面点击“生成角色”等功能即可使用该供应商服务。

说明：如果你偏好手动配置，可以直接编辑对应的 YAML 文件（路径见上），格式示例：

```yaml
# DeepSeek 示例
api_key: sk-xxxxx
model: deepseek-chat
base_url: https://api.deepseek.com
```

```yaml
# OpenAI 示例
api_key: sk-xxxxx
model: gpt-4.1-mini
```

## Quick Start (English)

1. Put the `backend/dist` folder and the `start.bat` (in this repo root) on a Windows machine.
2. Double-click `start.bat` — it will start the backend and open the app in your default browser.
3. In the app open "API Key Settings", choose a provider (`deepseek` or `openai`), paste your API key and click Save.
   - DeepSeek config is saved to: `backend/config/deepseek/config.yaml`
   - OpenAI config is saved to: `backend/config/openai/config.yaml`
4. After save you will see a toast confirming success. Then use the generation features on any novel page.

Manual config example (YAML):

```yaml
# DeepSeek example
api_key: sk-xxxxx
model: deepseek-chat
base_url: https://api.deepseek.com
```

```yaml
# OpenAI example
api_key: sk-xxxxx
model: gpt-4.1-mini
```

## Notes
- This distribution includes a packaged backend executable (`server.exe`) that serves the frontend static files — users do not need to install Python or other runtimes.
- If you prefer a custom deployment or need an installer, contact the maintainer.
# Manuscript

中文：
Manuscript 是一款专注于小说创作的长篇写作编辑器，帮助作者组织章节、场景与人物，支持实时预览与导出。该项目由前端（Vue 3 + TypeScript + Vite）和后端（Python）组成，适合用于构建长篇故事写作工作流。

特点：
- 专注长篇小说结构：章节与场景管理
- 富文本编辑与实时预览
- 导出与备份功能支持

English:
Manuscript is a novel-focused writing editor for long-form storytelling. It helps authors organize chapters, scenes, and characters, while offering real-time preview and export capabilities. The project consists of a frontend (Vue 3 + TypeScript + Vite) and a backend (Python), aimed at supporting a complete long-form writing workflow.

Highlights:
- Structure-focused: chapters and scene management
- Rich-text editing and live preview
- Export and backup support

Quick start (frontend):

```bash
cd frontend
npm install
npm run dev
```

Backend development instructions are available under `backend/README.md`.
