import { ref } from 'vue'

const visible = ref(false)
const message = ref('')
let _resolver: ((v: boolean) => void) | null = null

export function showConfirm(msg: string) {
  message.value = msg
  visible.value = true
  return new Promise<boolean>((resolve) => {
    _resolver = resolve
  })
}

export function resolveConfirm(v: boolean) {
  if (_resolver) _resolver(v)
  _resolver = null
  visible.value = false
}

export { visible as confirmVisible, message as confirmMessage }
