<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { getModelConfig, updateModelConfig } from '../api'
import useI18n from '../i18n'
import { pushToast } from '../utils/toast'

const { t } = useI18n()

const provider = ref('deepseek')
const apiKey = ref('')

async function load() {
  const res = await getModelConfig(provider.value)
  apiKey.value = res?.data?.config?.api_key || ''
}

onMounted(load)
// reload API key when provider selection changes
watch(provider, () => load())

async function save() {
  await updateModelConfig(provider.value, { api_key: apiKey.value })
  pushToast(t('saved') || 'Saved', 'success')
}
</script>

<template>
  <div>
    <h3>API Key Settings</h3>
    <div class="card" style="max-width:560px; padding:16px; margin-top:12px">
      <div class="form-row">
        <label class="form-label">Provider</label>
        <select v-model="provider" class="form-input">
          <option value="deepseek">deepseek</option>
          <option value="openai">openai</option>
        </select>
      </div>

      <div class="form-row" style="margin-top:12px">
        <label class="form-label">API Key</label>
        <input v-model="apiKey" class="form-input" />
        <div class="hint" style="margin-top:8px">Keep your API key secret. Stored locally for this provider.</div>
      </div>

      <div style="margin-top:16px;display:flex;gap:8px;align-items:center">
        <button class="btn-primary" @click="save">Save</button>
        <button class="btn-ghost" @click="() => provider = provider">Cancel</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.form-row{ display:flex; flex-direction:column }
.form-label{ font-size:0.95rem; color:var(--muted); margin-bottom:6px }
.form-input{ padding:8px 10px; border-radius:6px; border:1px solid rgba(255,255,255,0.03); background:transparent; color:var(--text); font-size:1rem }
.form-input option{ color:var(--muted); background:var(--panel) }
.form-input[type="text"], .form-input[type="password"] { width:100% }
.hint{ color:var(--muted); font-size:0.9rem }
</style>
