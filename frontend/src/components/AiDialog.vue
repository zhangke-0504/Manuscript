<script setup lang="ts">
import { ref, watch } from 'vue'
import { ssePost } from '../api'
import useI18n from '../i18n'

const props = defineProps<{ chapter_uid?: string }>()
const emit = defineEmits(['insert','open','close'])

const visible = ref(false)
const sessions = ref<Array<any>>([])
const selected = ref(0)
const { t } = useI18n()
const input = ref('')
const streaming = ref(false)
const errorMsg = ref('')

const storageKey = () => `ai_sessions:${props.chapter_uid || 'global'}`

function loadSessions() {
  try {
    const raw = localStorage.getItem(storageKey())
    sessions.value = raw ? JSON.parse(raw) : []
  } catch {
    sessions.value = []
  }
  if (!sessions.value.length) createSession()
  if (selected.value >= sessions.value.length) selected.value = sessions.value.length - 1
}

function saveSessions() {
  try { localStorage.setItem(storageKey(), JSON.stringify(sessions.value)) } catch {}
}

function createSession() {
  const s = { id: Date.now().toString(), created_at: Date.now(), messages: [] as any[] }
  sessions.value.push(s)
  selected.value = sessions.value.length - 1
  saveSessions()
}

import { showConfirm } from '../utils/confirm'

async function deleteSession(idx: number) {
  const ok = await showConfirm('Delete this AI session?')
  if (!ok) return
  sessions.value.splice(idx, 1)
  if (!sessions.value.length) createSession()
  if (selected.value >= sessions.value.length) selected.value = sessions.value.length - 1
  saveSessions()
}

function open() {
  loadSessions()
  // set default prompt when opening if empty
  if (!input.value) input.value = t('aiDefaultPrompt')
  visible.value = true
}
function close() { visible.value = false; emit('close') }

// notify parent when opened/closed
watch(visible, (v)=>{ if(v) emit('open') })

watch(sessions, saveSessions, { deep: true })

async function send() {
  const prompt = input.value.trim()
  if (!prompt) return
  const sess = sessions.value[selected.value]
  sess.messages.push({ role: 'user', content: prompt })
  input.value = ''
  errorMsg.value = ''
  streaming.value = true

  // ensure an assistant placeholder exists
  sess.messages.push({ role: 'assistant', content: '' })
  const assistantIndex = sess.messages.length - 1

  await ssePost('/working_flow/create_chapter_content', { chapter_uid: props.chapter_uid, provider: 'deepseek', conversation_messages: sess.messages }, (data) => {
    if (!data) return
    if (data.type === 'error') {
      errorMsg.value = data.message || 'Stream error'
      streaming.value = false
      return
    }
    if (data.type === 'token') {
      const token = data.token || ''
      const last = sess.messages[assistantIndex]
      if (!last || last.role !== 'assistant') sess.messages.push({ role: 'assistant', content: token })
      else last.content += token
    } else if (data.type === 'assistant' && data.content) {
      sess.messages[assistantIndex].content += data.content
    } else if (typeof data === 'string') {
      sess.messages[assistantIndex].content += data
    }
  }, () => {
    streaming.value = false
    saveSessions()
  }, { retries: 2, retryDelay: 1000 })
}

function insertToEditor(content: string) {
  emit('insert', content)
}

function copyToClipboard(text: string) {
  try { navigator.clipboard.writeText(text) } catch {}
}

defineExpose({ open, close })
</script>

<template>
  <div v-if="visible" class="ai-dialog">
    <div class="ai-header">
      <div class="ai-sessions">
        <select v-model="selected" class="ai-select">
          <option v-for="(s,idx) in sessions" :key="s.id" :value="idx">Session {{ idx + 1 }} - {{ new Date(s.created_at).toLocaleString() }}</option>
        </select>
        <button class="btn-ghost" @click="createSession">New</button>
        <button class="btn-ghost" @click="deleteSession(selected)">Delete</button>
      </div>
      <div class="ai-status">
        <span v-if="streaming" class="muted">Streaming...</span>
      </div>
    </div>

    <div class="ai-messages">
      <div v-if="errorMsg" class="error">{{ errorMsg }}</div>
      <div v-for="(m,idx) in sessions[selected]?.messages || []" :key="idx" :class="['ai-message', m.role]">
        <div class="ai-bubble" :title="m.role==='assistant' ? 'Click to insert, double-click to copy' : ''" @click="m.role==='assistant' && insertToEditor(m.content)" @dblclick.prevent="m.role==='assistant' && copyToClipboard(m.content)">{{ m.content }}</div>
        <div v-if="m.role==='assistant'" class="ai-actions">
          <button class="btn-ghost" @click="insertToEditor(m.content)">Insert</button>
          <button class="btn-ghost" @click="copyToClipboard(m.content)">Copy</button>
        </div>
      </div>
    </div>

    <div class="ai-input">
      <textarea v-model="input" @keydown="(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send() } }" placeholder="Type message, Enter to send, Shift+Enter newline"></textarea>
      <div class="ai-controls">
        <button class="btn-primary" @click="send">Send</button>
        <button class="btn-ghost" @click="close">Close</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.ai-dialog{ /* inline panel, parent controls placement */ width:100%; display:flex; flex-direction:column; padding:12px; box-shadow: -6px 0 30px rgba(0,0,0,0.5); z-index:1200; height:100%; background: var(--panel); border-left:1px solid rgba(255,255,255,0.02); color:var(--text) }
.ai-header{ display:flex; justify-content:space-between; align-items:center; gap:8px }
.ai-sessions{ display:flex; gap:8px; align-items:center }
.ai-select{ min-width:220px; background:transparent; color:var(--text); border:1px solid rgba(255,255,255,0.03); padding:6px 8px; border-radius:6px }
.ai-select option{ color: var(--muted); background: var(--panel) }
.ai-status{ min-width:120px; text-align:right }
.ai-messages{ flex:1; overflow:auto; border:1px solid rgba(255,255,255,0.02); padding:8px; margin-top:8px; background: rgba(0,0,0,0.05) }
.ai-message{ margin-bottom:12px; display:flex; flex-direction:column }
.ai-message.user{ align-items:flex-end }
.ai-message.assistant{ align-items:flex-start }
.ai-bubble{ max-width:86%; padding:10px 12px; border-radius:10px; background: rgba(255,255,255,0.04); color:var(--text); box-shadow:0 2px 6px rgba(0,0,0,0.08); white-space:pre-wrap; cursor: pointer }
.ai-message.user .ai-bubble{ background:linear-gradient(90deg,var(--accent),var(--accent-2)); color:white }
.ai-actions{ margin-top:6px }
.ai-input{ display:flex; gap:8px; margin-top:8px; align-items:flex-end }
.ai-input textarea{ flex:1; min-height:80px; padding:8px; border:1px solid rgba(255,255,255,0.03); border-radius:6px; resize:vertical; background:transparent; color:var(--text) }
.ai-controls{ display:flex; flex-direction:column; gap:8px }
.ai-controls .btn-ghost, .ai-actions .btn-ghost{ background: rgba(255,255,255,0.02); color: var(--text); border:1px solid rgba(255,255,255,0.03) }
.muted{ color:var(--muted) }
.error{ color:crimson; margin-bottom:8px }
</style>
