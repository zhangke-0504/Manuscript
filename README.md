# Manuscript — 桌面版使用说明 / Usage

本说明使用中英双语，简洁说明如何在 Windows 上启动已打包的桌面应用。

---

中文（简体）

1. 启动应用（非开发者，推荐）
   - 在项目根目录双击 `start-app.bat`，或右键选择“以 PowerShell 运行”执行 `start-app.ps1`。
   - 脚本会自动查找并运行已生成的 unpacked 可执行程序（优先 `build_dist\\win-unpacked\\manuscript-desktop.exe`，其次 `dist\\win-unpacked\\manuscript-desktop.exe`），如果未找到会提示你先运行 `npm run dist` 进行打包。

2. 已安装版（使用安装程序）
   - 双击 `build_dist\\manuscript-desktop Setup 1.0.0.exe` 或 `dist\\manuscript-desktop Setup 1.0.0.exe` 进行安装。
   - 安装后程序会写入用户数据（数据库文件位于 Electron 的 userData 目录），卸载通过控制面板执行。

3. 简要排错
   - 出现空白界面：请使用 unpacked 的可执行（`...\\win-unpacked\\manuscript-desktop.exe`）运行以查看调试控制台，或检查是否已正确打包前端（`frontend/dist`）。
   - 找不到可执行：在项目根运行 `npm run dist` 重新打包。

---

English

1. Start the app (for non-developers)
   - Double-click `start-app.bat` in the project root, or run `start-app.ps1` with PowerShell.
   - The launcher searches for the unpacked app executable (prefers `build_dist\\win-unpacked\\manuscript-desktop.exe`, then `dist\\win-unpacked\\manuscript-desktop.exe`). If not found it instructs to run `npm run dist`.

2. Installed version
   - Run the installer `build_dist\\manuscript-desktop Setup 1.0.0.exe` (or `dist\\manuscript-desktop Setup 1.0.0.exe`) to install.
   - The app stores runtime data in the Electron userData folder (e.g., AppData\\Roaming). Uninstall via Control Panel.

3. Quick troubleshooting
   - Blank window: run the unpacked executable to open DevTools for errors and confirm frontend assets exist (`frontend/dist`).
   - Missing executable: run `npm run dist` in project root to rebuild.

---

   **Packaging / 打包**

   - **中文（简体）:**
      - 前置条件：已安装 Node.js 与 npm、Python 3、以及 `pyinstaller`（用于打包后端）。如果使用全局 `electron-builder`，也请确保其可用；项目 devDependencies 中也包含 `electron-builder`。
      - 打包命令（在项目根目录运行）：

         ```bash
         npm install            # 安装前端与构建所需依赖（若尚未安装）
         npm run dist           # 构建 frontend/dist、后端可执行，并运行 electron-builder
         ```

      - `npm run dist` 会执行：前端构建（`frontend`）、后端使用 `pyinstaller` 打包为可执行文件、复制 Electron 运行所需资产，最后由 `electron-builder` 生成 `build_dist`/安装包。
      - 注意：打包需要一定时间且依赖本机环境（Python、编译工具链等）。如果 `start-app.bat` 未找到可运行的 exe，它会尝试自动运行 `npm run dist`；失败时请根据控制台提示修复依赖后重试。

   - **English:**
      - Prerequisites: Node.js + npm, Python 3 and `pyinstaller` (for backend packaging). `electron-builder` is used by the project (installed as a devDependency or globally).
      - Packaging commands (run in project root):

         ```bash
         npm install
         npm run dist
         ```

      - What `npm run dist` does: builds the frontend into `frontend/dist`, packages the backend into a single executable with `pyinstaller`, copies Electron assets, and runs `electron-builder` to produce `build_dist` / installer artifacts.
      - Building is environment-dependent and can take several minutes. `start-app.bat` will attempt to run `npm run dist` automatically if no packaged executable is found; if the automated build fails, run the commands above and inspect console output.


如果需要，我可以：
- 把 `start-app.bat` 添加到安装程序创建的桌面快捷方式；
- 生成一个 GitHub Actions workflow 用于 CI 构建并签名发行版。

If you want, I can:
- Add a desktop shortcut creation step to the installer that points to `start-app.bat`/the installed exe;
- Provide a GitHub Actions workflow that builds and signs releases in CI.
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
