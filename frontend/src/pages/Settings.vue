<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { getModelConfig, updateModelConfig } from '../api'
import useI18n from '../i18n'

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
  alert(t('saved') || 'Saved')
}
</script>

<template>
  <div>
    <h3>API Key Settings</h3>
    <div style="max-width:480px">
      <label>Provider</label>
      <select v-model="provider">
        <option value="deepseek">deepseek</option>
        <option value="openai">openai</option>
      </select>

      <div style="margin-top:8px">
        <label>API Key</label>
        <input v-model="apiKey" style="width:100%" />
      </div>
      <div style="margin-top:8px">
        <button @click="save">Save</button>
      </div>
    </div>
  </div>
</template>
