<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { listNovels, deleteNovels, createNovel } from '../api'
import { useRouter } from 'vue-router'
import useI18n from '../i18n'

const { t } = useI18n()

const novels = ref<any[]>([])
const loading = ref(false)
const deleting = ref(false)
const router = useRouter()

async function load() {
  loading.value = true
  const res = await listNovels(1, 100)
  novels.value = res?.data?.items || []
  loading.value = false
}

onMounted(load)

async function onCreate() {
  const title = prompt('Novel title')
  if (!title) return
  const res = await createNovel({ title, genre: '未知', description: '' })
  const uid = res?.data?.uid
  if (uid) router.push({ name: 'novel-editor', params: { uid } })
}

async function onDeleteSelected() {
  const checked = document.querySelectorAll('input[data-uid]:checked')
  const uids = Array.from(checked).map((c: any) => c.getAttribute('data-uid'))
  if (!uids.length) return alert(t('selectAtLeastOne') || 'Select at least one')
  if (!confirm(t('deleteConfirm') || 'Delete selected?')) return
  deleting.value = true
  try {
    await deleteNovels(uids)
    await load()
  } finally {
    deleting.value = false
  }
}

function openNovel(uid: string) {
  router.push({ name: 'novel-editor', params: { uid } })
}
</script>

<template>
  <div>
    <div style="display:flex;gap:8px;margin-bottom:12px">
      <button @click="onDeleteSelected" :disabled="loading || deleting">{{ t('deleteSelected') }}</button>
      <span v-if="loading">{{ t('loading') }}</span>
      <span v-if="deleting" style="color:crimson">{{ t('deleting') }}</span>
    </div>

    <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:12px">
      <div @click="onCreate" style="border:1px dashed #ccc;padding:16px;cursor:pointer">+ {{ t('createPlaceholder') }}</div>
      <div v-for="n in novels" :key="n.uid" style="border:1px solid #ddd;padding:12px">
        <div style="display:flex;justify-content:space-between">
          <div>
            <input type="checkbox" :data-uid="n.uid" />
          </div>
          <div style="flex:1;margin-left:8px;cursor:pointer" @click="openNovel(n.uid)">
            <div style="font-weight:600">{{ n.title }}</div>
            <div style="color:#666;font-size:12px">{{ n.updated_at || n.created_at }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
