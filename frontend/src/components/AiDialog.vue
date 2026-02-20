<script setup lang="ts">
import { ref, watch, defineEmits, defineExpose } from 'vue'
import { ssePost } from '../api'
import useI18n from '../i18n'

const props = defineProps<{ chapter_uid?: string }>()
const emit = defineEmits(['insert'])

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

function deleteSession(idx: number) {
  if (!confirm('Delete this AI session?')) return
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
function close() { visible.value = false }

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
  <div v-if="visible" style="position:fixed;right:12px;bottom:12px;width:480px;background:#fff;border:1px solid #ddd;padding:12px;box-shadow:0 6px 20px rgba(0,0,0,0.08)">
    <div style="display:flex;gap:8px;align-items:center;margin-bottom:8px">
      <div style="flex:1">
        <select v-model="selected">
          <option v-for="(s,idx) in sessions" :key="s.id" :value="idx">Session {{ idx + 1 }} - {{ new Date(s.created_at).toLocaleString() }}</option>
        </select>
        <button @click="createSession" style="margin-left:8px">New</button>
        <button @click="deleteSession(selected)" style="margin-left:8px">Delete</button>
      </div>
      <div style="min-width:120px;text-align:right">
        <span v-if="streaming">Streaming...</span>
        <span v-else style="color:#666">Idle</span>
      </div>
    </div>

    <div style="height:260px;overflow:auto;border:1px solid #f0f0f0;padding:8px">
      <div v-if="errorMsg" style="color:crimson;margin-bottom:8px">{{ errorMsg }}</div>
      <div v-for="(m,idx) in sessions[selected]?.messages || []" :key="idx" style="margin-bottom:8px">
        <div v-if="m.role==='user'" style="text-align:right;color:#333">{{ m.content }}</div>
        <div v-else style="color:#111;white-space:pre-wrap">{{ m.content }}</div>
        <div v-if="m.role==='assistant'" style="text-align:right;margin-top:4px">
          <button @click="insertToEditor(m.content)">Insert</button>
          <button @click="copyToClipboard(m.content)" style="margin-left:6px">Copy</button>
        </div>
      </div>
    </div>

    <div style="display:flex;gap:8px;margin-top:8px">
      <textarea v-model="input" @keydown="(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send() } }" style="flex:1;min-height:40px" placeholder="Type message, Enter to send, Shift+Enter newline" />
      <div style="display:flex;flex-direction:column;gap:8px">
        <button @click="send">Send</button>
        <button @click="close">Close</button>
      </div>
    </div>
  </div>
</template>
