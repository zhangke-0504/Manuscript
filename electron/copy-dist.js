const fs = require('fs')
const path = require('path')

// Simple helper: ensure frontend/dist exists before packaging; no-op otherwise.
const dist = path.join(__dirname, '..', 'frontend', 'dist')
if (!fs.existsSync(dist)) {
  console.warn('frontend/dist not found. Make sure to run `npm run build:frontend` first.')
  process.exit(0)
}
console.log('frontend/dist exists, continuing...')

// Ensure backend/dist exists (backend exe must be built before packaging)
const backendDist = path.join(__dirname, '..', 'backend', 'dist')
if (!fs.existsSync(backendDist)) {
  console.warn('backend/dist not found. Run `npm run build:backend:exe` to produce manuscript-backend.exe before packaging.')
  // do not exit; allow packaging to continue but warn
} else {
  console.log('backend/dist exists, will be included as extraResources')
}
