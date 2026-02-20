<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { listNovels, deleteNovels, createNovel } from '../api'
import { useRouter } from 'vue-router'
import useI18n from '../i18n'

const { t } = useI18n()

const novels = ref<any[]>([])
const loading = ref(false)
const deleting = ref(false)
const page = ref(1)
const size = ref(10)
const total = ref(0)
const router = useRouter()

async function load() {
  loading.value = true
  const res = await listNovels(page.value, size.value)
  novels.value = res?.data?.items || []
  total.value = res?.data?.total || 0
  loading.value = false
}

onMounted(load)

function totalPages() {
  return Math.max(1, Math.ceil(total.value / size.value))
}

function changePage(p: number) {
  const max = totalPages()
  if (p < 1) p = 1
  if (p > max) p = max
  page.value = p
  load()
}

async function onCreate() {
  const title = prompt('Novel title')
  if (!title) return
  const res = await createNovel({ title, genre: '未知', description: '' })
  // After creating an asset, stay on the asset list page and refresh
  await load()
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
    <div style="display:flex;gap:8px;margin-bottom:12px;align-items:center">
      <button @click="onDeleteSelected" :disabled="loading || deleting">{{ t('deleteSelected') }}</button>
      <span v-if="loading">{{ t('loading') }}</span>
      <span v-if="deleting" style="color:crimson">{{ t('deleting') }}</span>
      <div style="margin-left:auto;display:flex;align-items:center;gap:8px">
        <div style="font-size:12px;color:#666">Page {{ page }} / {{ totalPages() }}</div>
        <button @click="changePage(page - 1)" :disabled="page<=1">Prev</button>
        <button @click="changePage(page + 1)" :disabled="page>=totalPages()">Next</button>
        <input type="number" style="width:70px" :value="page" @change="(e) => changePage(Number($event.target.value))" />
      </div>
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
