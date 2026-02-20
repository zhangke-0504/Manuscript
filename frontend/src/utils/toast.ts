import { ref } from 'vue'

const listeners: Array<(m: { message: string; type?: string }) => void> = []
export function onPush(fn: (m: { message: string; type?: string }) => void) { listeners.push(fn) }
export function pushToast(message: string, type: 'info'|'success'|'error'='info') {
  listeners.forEach(l => l({ message, type }))
}
