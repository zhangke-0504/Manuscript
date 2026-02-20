<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { listNovels, deleteNovels, createNovel } from '../api'
import { useRouter } from 'vue-router'
import useI18n from '../i18n'
import Pagination from '../components/Pagination.vue'
import { pushToast } from '../utils/toast'
import ConfirmModal from '../components/ConfirmModal.vue'
import { showConfirm } from '../utils/confirm'
import Toast from '../components/Toast.vue'

const { t } = useI18n()

const novels = ref<any[]>([])
const loading = ref(false)
const deleting = ref(false)
const page = ref(1)
const size = ref(10)
const total = ref(0)
const router = useRouter()

// hook up toast listener for global toast component
import { onPush } from '../utils/toast'

onPush((m)=>{
  // noop here; Toast.vue subscribes via its own listener import
})

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
  if (!uids.length) { pushToast(t('selectAtLeastOne') || 'Select at least one', 'error'); return }
  const ok = await showConfirm(t('deleteConfirm') || 'Delete selected?')
  if (!ok) return
  deleting.value = true
  try {
    await deleteNovels(uids)
    await load()
    pushToast(t('deleteSuccess') || 'Deleted', 'success')
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
      <button class="btn-ghost" @click="onDeleteSelected" :disabled="loading || deleting">{{ t('deleteSelected') }}</button>
      <span v-if="loading" class="muted">{{ t('loading') }}</span>
      <span v-if="deleting" style="color:crimson">{{ t('deleting') }}</span>
      <div style="margin-left:auto;display:flex;align-items:center;gap:8px">
        <div class="muted">Page {{ page }} / {{ totalPages() }}</div>
        <button class="btn-ghost" @click="changePage(page - 1)" :disabled="page<=1">Prev</button>
        <button class="btn-ghost" @click="changePage(page + 1)" :disabled="page>=totalPages()">Next</button>
        <input type="number" style="width:70px" v-model.number="page" @change="changePage(page)" @keydown.enter.prevent="changePage(page)" />
      </div>
    </div>

    <div class="card-list">
      <div @click="onCreate" class="asset-card" style="border:1px dashed rgba(255,255,255,0.06);display:flex;align-items:center;justify-content:center">+ {{ t('createPlaceholder') }}</div>
      <div v-for="n in novels" :key="n.uid" class="asset-card">
        <div style="display:flex;justify-content:space-between;align-items:center">
          <div>
            <input type="checkbox" :data-uid="n.uid" />
          </div>
          <div style="flex:1;margin-left:12px;cursor:pointer" @click="openNovel(n.uid)">
            <div style="font-weight:700">{{ n.title }}</div>
            <div class="muted">{{ n.updated_at || n.created_at }}</div>
          </div>
        </div>
      </div>
    </div>
    <ConfirmModal />
    <Toast />
  </div>
</template>
