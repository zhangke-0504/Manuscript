const { app, BrowserWindow } = require('electron')
const path = require('path')
const fs = require('fs')
const { spawn } = require('child_process')
const http = require('http')

let mainWindow = null
let backendProc = null

function startBackend() {
  if (app.isPackaged) {
    // packaged: exe located in resources
    const exePath = path.join(process.resourcesPath, 'backend', 'dist', process.platform === 'win32' ? 'manuscript-backend.exe' : 'manuscript-backend')
    // Ensure backend uses Electron userData for writable storage
    const userDataDir = app.getPath('userData')
    const env = Object.assign({}, process.env, { BACKEND_DATA_DIR: userDataDir })
    backendProc = spawn(exePath, ['-p', '8890'], { stdio: 'inherit', env })
  } else {
    // development: try to run python backend/main.py
    const py = process.platform === 'win32' ? 'python' : 'python3'
    const script = path.join(__dirname, '..', 'backend', 'main.py')
    backendProc = spawn(py, [script, '-p', '8890'], { stdio: 'inherit' })
  }
  backendProc.on('exit', (code) => {
    console.log('backend exited', code)
  })
}

function waitForBackend(url, timeout = 10000) {
  const start = Date.now()
  return new Promise((resolve, reject) => {
    (function poll() {
      const req = http.request(url, { method: 'POST', timeout: 2000 }, (res) => {
        // any response means backend up
        resolve()
      })
      req.on('error', () => {
        if (Date.now() - start > timeout) return reject(new Error('timeout'))
        setTimeout(poll, 300)
      })
      req.end()
    })()
  })
}

async function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false
    }
  })

  if (process.env.NODE_ENV === 'development') {
    await mainWindow.loadURL('http://localhost:5173')
    mainWindow.webContents.openDevTools()
    return
  }

  // production: start backend and load local index.html
  startBackend()
  try {
    await waitForBackend('http://127.0.0.1:8890/api/health/test', 15000)
  } catch (e) {
    console.warn('backend did not respond in time, proceeding to load frontend')
  }

  // Resolve index.html from several possible locations (resources root, app.asar, or relative __dirname)
  const candidates = [
    path.join(process.resourcesPath, 'frontend', 'dist', 'index.html'),
    path.join(process.resourcesPath, 'app.asar', 'frontend', 'dist', 'index.html'),
    path.join(__dirname, '..', 'frontend', 'dist', 'index.html')
  ]
  let indexPath = null
  for (const c of candidates) {
    if (fs.existsSync(c)) { indexPath = c; break }
  }
  if (!indexPath) {
    // fallback to original location (will throw) so error is visible
    indexPath = path.join(process.resourcesPath, 'frontend', 'dist', 'index.html')
  }

  console.log('Loading frontend index:', indexPath, 'exists=', fs.existsSync(indexPath))
  await mainWindow.loadFile(indexPath)

  // Open DevTools when packaged for debugging blank window issues (remove for production)
  try {
    if (process.env.ELECTRON_DEBUG === '1' || process.env.NODE_ENV === 'development' || app.isPackaged) {
      mainWindow.webContents.openDevTools({ mode: 'right' })
    }
  } catch (e) {
    console.warn('Could not open DevTools', e)
  }
}

app.whenReady().then(createWindow)

app.on('window-all-closed', () => {
  if (backendProc) {
    try { backendProc.kill() } catch (e) { }
  }
  if (process.platform !== 'darwin') app.quit()
})
