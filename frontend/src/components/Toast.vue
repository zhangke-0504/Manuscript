<template>
  <div class="toast-container" v-if="toasts.length">
    <div v-for="t in toasts" :key="t.id" class="toast" :class="t.type">
      <div class="toast-body">{{ t.message }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue'
import { onPush } from '../utils/toast'

interface ToastItem { id: number; message: string; type?: 'info'|'success'|'error' }
const state = reactive({ toasts: [] as ToastItem[] })

// subscribe to global push events
onPush((m)=>{
  const id = Date.now()+Math.random()
  state.toasts.push({ id, message: m.message, type: (m.type as any) || 'info' })
  setTimeout(()=>{ const i = state.toasts.findIndex(t=>t.id===id); if(i>=0) state.toasts.splice(i,1) }, 3500)
})

const toasts = state.toasts
</script>

<style scoped>
.toast-container { position: fixed; right: 16px; bottom: 16px; display:flex;flex-direction:column;gap:8px; z-index:1000 }
.toast { min-width:180px;padding:10px 12px;border-radius:8px;color:white;box-shadow:0 6px 18px rgba(2,6,23,0.6); }
.toast.info { background: rgba(20,20,30,0.8) }
.toast.success { background: linear-gradient(90deg,#3ddc84,#1fa57a) }
.toast.error { background: linear-gradient(90deg,#ff6b6b,#ff3b3b) }
.toast-body{ font-weight:600 }
</style>
