import axios from 'axios'

// Base URL for backend API. Can be overridden via Vite env `VITE_API_BASE`.
const API_BASE = (import.meta.env.VITE_API_BASE as string) || 'http://127.0.0.1:8890/api'

const api = axios.create({ baseURL: API_BASE, timeout: 60000 })

export async function getModelConfig(provider: string) {
  const res = await api.post('/model_providers/get', { provider })
  return res.data
}

export async function updateModelConfig(provider: string, values: any) {
  const res = await api.post('/model_providers/update', { provider, values })
  return res.data
}

export async function listNovels(page = 1, size = 50) {
  const res = await api.post('/novel/list', { page, size })
  return res.data
}

export async function createNovel(payload: any) {
  const res = await api.post('/novel/create', payload)
  return res.data
}

export async function updateNovel(payload: any) {
  const res = await api.post('/novel/update', payload)
  return res.data
}

export async function deleteNovels(uids: string[]) {
  const res = await api.post('/novel/delete', { uids })
  return res.data
}

export async function listChapters(novel_uid: string, page = 1, size = 200) {
  const res = await api.post('/chapter/list', { novel_uid, page, size })
  return res.data
}

export async function getChapter(uid: string) {
  const res = await api.post('/chapter/get', { uid })
  return res.data
}

export async function listCharacters(novel_uid: string, page = 1, size = 200) {
  const res = await api.post('/character/list', { novel_uid, page, size })
  return res.data
}

export async function createChapter(payload: any) {
  const res = await api.post('/chapter/create', payload)
  return res.data
}

export async function createCharacter(payload: any) {
  const res = await api.post('/character/create', payload)
  return res.data
}

export async function updateChapter(payload: any) {
  const res = await api.post('/chapter/update', payload)
  return res.data
}

export async function deleteChapters(uids: string[]) {
  const res = await api.post('/chapter/delete', { uids })
  return res.data
}

export async function updateCharacter(payload: any) {
  const res = await api.post('/character/update', payload)
  return res.data
}

export async function getCharacter(uid: string) {
  const res = await api.post('/character/get', { uid })
  return res.data
}

export async function deleteCharacters(uids: string[]) {
  const res = await api.post('/character/delete', { uids })
  return res.data
}

// SSE-like streaming POST reader. Calls onMessage with parsed JSON chunks as they arrive.
export async function ssePost(path: string, body: any, onMessage: (data: any) => void, onDone?: () => void, options?: { retries?: number, retryDelay?: number }) {
  const retries = options?.retries ?? 2
  const retryDelay = options?.retryDelay ?? 1000

  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      // Use same base as axios
      const url = API_BASE.replace(/\/$/, '') + path
      const res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })

      if (!res.ok) {
        const text = await res.text().catch(() => '')
        throw new Error(`HTTP ${res.status} ${text}`)
      }

      if (!res.body) {
        onDone && onDone()
        return
      }

      const reader = res.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      // We'll parse SSE-style events: blocks separated by double newline
      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })

        let idx
        while ((idx = buffer.indexOf('\n\n')) !== -1) {
          const event = buffer.slice(0, idx)
          buffer = buffer.slice(idx + 2)

          // collect lines starting with 'data:'
          const lines = event.split(/\r?\n/)
          const dataLines: string[] = []
          for (const l of lines) {
            const trimmed = l.trim()
            if (!trimmed) continue
            if (trimmed.startsWith('data:')) {
              dataLines.push(trimmed.replace(/^data:\s?/, ''))
            } else {
              // also accept raw JSON line
              dataLines.push(trimmed)
            }
          }

          const payload = dataLines.join('\n')
          if (!payload) continue
          // Try parse JSON, or deliver raw
          try {
            const parsed = JSON.parse(payload)
            onMessage(parsed)
          } catch (e) {
            onMessage(payload)
          }
        }
      }

      // leftover
      if (buffer.trim()) {
        // try to parse any remaining data lines
        const lines = buffer.split(/\r?\n/).map(l => l.replace(/^data:\s?/, '').trim()).filter(Boolean)
        if (lines.length) {
          const payload = lines.join('\n')
          try { onMessage(JSON.parse(payload)) } catch { onMessage(payload) }
        }
      }

      onDone && onDone()
      return
    } catch (err: any) {
      const message = err?.message || String(err)
      console.warn('ssePost error:', message, 'attempt', attempt)
      onMessage({ type: 'error', message })
      if (attempt < retries) {
        // exponential backoff
        const wait = retryDelay * Math.pow(2, attempt)
        await new Promise((r) => setTimeout(r, wait))
        continue
      } else {
        onDone && onDone()
        return
      }
    }
  }
}

export default api
