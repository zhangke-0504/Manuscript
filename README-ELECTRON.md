# Build Desktop App (Electron + FastAPI backend)

Overview
- Frontend: `frontend` (Vite + Vue)
- Backend: `backend` (FastAPI, Python)
- Desktop wrapper: `electron` (Electron main process)

High-level steps (Windows)
1. Install Node and Python on build machine. Ensure `pyinstaller` is available: `pip install pyinstaller`.
2. From project root, build frontend:

```powershell
cd frontend
npm install
npm run build
cd ..
```

3. Build backend standalone executable:

```powershell
cd backend
pip install -r requirements.txt
pyinstaller --onefile --name manuscript-backend main.py
cd ..
```

Output exe will be at `backend/dist/manuscript-backend.exe`.

4. Package Electron app (requires electron-builder):

```powershell
npm install
npm run dist
```

This runs the scripts defined in the root `package.json` which will build frontend, produce backend exe, and run `electron-builder` to create an installer (NSIS on Windows).

Notes
- The Electron `main.js` spawns the backend exe in production and loads the built `frontend/dist/index.html` from the app resources. In development, it will load `http://localhost:5173` and try to run `python backend/main.py` (so run backend separately if needed).
- Make sure to store user data (API keys, DB files) under `app.getPath('userData')` if you change server behavior.
