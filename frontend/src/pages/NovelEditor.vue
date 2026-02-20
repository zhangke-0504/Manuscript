<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { listChapters, listCharacters, ssePost, updateChapter, updateCharacter, deleteChapters, deleteCharacters, getChapter, getCharacter, createChapter, createCharacter } from '../api'
import AiDialog from '../components/AiDialog.vue'
import useI18n from '../i18n'
import Pagination from '../components/Pagination.vue'
import { pushToast } from '../utils/toast'
import { showConfirm } from '../utils/confirm'
import ConfirmModal from '../components/ConfirmModal.vue'
import Toast from '../components/Toast.vue'

const { t } = useI18n()

const route = useRoute()
const router = useRouter()
const uid = String(route.params.uid || '')

const chapters = ref<any[]>([])
const characters = ref<any[]>([])
// pagination state for chapters
const chapterPage = ref(1)
const chapterSize = ref(10)
const chapterTotal = ref(0)
// pagination state for characters
const characterPage = ref(1)
const characterSize = ref(10)
const characterTotal = ref(0)
const loading = ref(false)
const generatingChapters = ref(false)
const generatingCharacters = ref(false)
const chapterOpen = ref(true)
const charactersOpen = ref(true)

const selectedChapter = ref<any>(null)
const editorContent = ref('')
const editorTitle = ref('')
const selectedLoading = ref(false)
const saving = ref(false)
const savedMessage = ref('')

const aiRef = ref<any>(null)
const aiVisible = ref(false)

function chapterTotalPages() {
  return Math.max(1, Math.ceil(chapterTotal.value / chapterSize.value))
}

function characterTotalPages() {
  return Math.max(1, Math.ceil(characterTotal.value / characterSize.value))
}

function changeChapterPage(p: number) {
  const max = chapterTotalPages()
  if (p < 1) p = 1
  if (p > max) p = max
  chapterPage.value = p
  load()
}

function changeCharacterPage(p: number) {
  const max = characterTotalPages()
  if (p < 1) p = 1
  if (p > max) p = max
  characterPage.value = p
  load()
}

async function load() {
  loading.value = true
  // chapters with pagination
  const cRes = await listChapters(uid, chapterPage.value, chapterSize.value)
  const rawChapters = cRes?.data?.items || []
  chapterTotal.value = cRes?.data?.total || 0
  chapters.value = rawChapters.map((it: any) => ({ ...it, uid: it.uid || it.chapter_uid || (it.chapter && it.chapter.uid) }))

  // characters with pagination
  const chRes = await listCharacters(uid, characterPage.value, characterSize.value)
  const rawChars = chRes?.data?.items || []
  characterTotal.value = chRes?.data?.total || 0
  characters.value = rawChars.map((it: any) => ({ ...it, uid: it.uid || it.character_uid || (it.character && it.character.uid) }))
  loading.value = false
}

onMounted(load)

async function genOutline() {
  generatingChapters.value = true
  chapters.value = []
  await ssePost('/working_flow/create_chapter_outline', { novel_uid: uid, provider: 'deepseek' }, (data) => {
    if (data.type === 'chapter' && data.chapter) {
      const ch = data.chapter
      chapters.value.push({ title: ch.title, synopsis: ch.synopsis, uid: ch.uid || ch.chapter_uid })
    }
  }, async () => {
    generatingChapters.value = false
    // refresh current page
    await load()
  })
}

async function genCharacters() {
  generatingCharacters.value = true
  characters.value = []
    try {
      await ssePost('/working_flow/create_characters', { novel_uid: uid, provider: 'deepseek' }, (data) => {
        if (data.type === 'character' && data.character) {
          const cc = data.character
          characters.value.push({ name: cc.name, description: cc.description, uid: cc.uid || cc.character_uid })
        }
      }, async () => {
        generatingCharacters.value = false
        await load()
      })
    } catch (e) {
      generatingCharacters.value = false
      throw e
    }
}

async function selectChapter(ch: any) {
  selectedChapter.value = null
  editorContent.value = ''
  editorTitle.value = ''
  if (!ch?.uid) return
  selectedLoading.value = true
  try {
    const res = await getChapter(ch.uid)
    const d = res?.data
    selectedChapter.value = d
    editorContent.value = d?.content || ''
    editorTitle.value = d?.title || ''
  } finally {
    selectedLoading.value = false
  }
}

async function saveChapter() {
  if (!selectedChapter.value) { pushToast('No chapter selected','error'); return }
  saving.value = true
  savedMessage.value = ''
  try {
    await updateChapter({ uid: selectedChapter.value.uid, title: editorTitle.value, content: editorContent.value })
    savedMessage.value = 'Saved'
    setTimeout(() => (savedMessage.value = ''), 2000)
    await load()
    } catch (e: any) {
    pushToast('Save failed: ' + (e?.message || e), 'error')
  } finally {
    saving.value = false
  }
}

function openAi() {
  // ensure AI panel is mounted and visible, then open it
  aiVisible.value = true
  nextTick(() => { if (aiRef.value && aiRef.value.open) aiRef.value.open() })
}

function handleAiInsert(content: string) {
  // append into editor
  editorContent.value += '\n' + content
}

async function editChapterTitle(ch: any) {
  const t = prompt('New chapter title', ch.title)
  if (!t) return
  await updateChapter({ uid: ch.uid, title: t })
  await load()
  pushToast('Chapter updated', 'success')
}

async function editCharacter(c: any) {
  const name = prompt('Name', c.name)
  const desc = prompt('Description', c.description)
  if (!name && !desc) return
  await updateCharacter({ uid: c.uid, name, description: desc })
  await load()
  pushToast('Character updated', 'success')
}

async function removeChapters() {
  const uids = chapters.value.filter((c: any) => c._checked).map((c: any) => c.uid)
  if (!uids.length) { pushToast('select', 'error'); return }
  if (!await showConfirm('Delete selected chapters?')) return
  await deleteChapters(uids)
  await load()
  pushToast('Deleted chapters', 'success')
}

async function removeCharacters() {
  const uids = characters.value.filter((c: any) => c._checked).map((c: any) => c.uid)
  if (!uids.length) { pushToast('select', 'error'); return }
  if (!await showConfirm('Delete selected characters?')) return
  await deleteCharacters(uids)
  await load()
  pushToast('Deleted characters', 'success')
}

async function createNewChapter() {
  const title = prompt('Chapter title')
  if (!title) return
  try {
    const res = await createChapter({ novel_uid: uid, chapter_idx: chapters.value.length + 1, title, content: '' })
    // reload to pick up normalized uid
    await load()
    // try to select the new chapter if returned
    const newUid = res?.data?.uid || res?.uid || (res?.data && res.data.uid)
    if (newUid) {
      const found = chapters.value.find((c: any) => c.uid === newUid)
      if (found) selectChapter(found)
    }
  } catch (e: any) {
    pushToast('Create chapter failed: ' + (e?.message || e), 'error')
  }
}

async function createNewCharacter() {
  const name = prompt('Character name')
  if (!name) return
  try {
    await createCharacter({ novel_uid: uid, name, description: '' })
    await load()
  } catch (e: any) {
    pushToast('Create character failed: ' + (e?.message || e), 'error')
  }
}

function onKeydown(e: KeyboardEvent) {
  const isMac = navigator.platform.toUpperCase().includes('MAC')
  const saveKey = isMac ? e.metaKey && e.key === 's' : e.ctrlKey && e.key === 's'
  if (saveKey) {
    e.preventDefault()
    saveChapter()
  }
}

window.addEventListener('keydown', onKeydown)
onBeforeUnmount(() => window.removeEventListener('keydown', onKeydown))
</script>

<template>
  <div class="layout">
    <aside class="sidebar">
      <div style="display:flex;align-items:center;justify-content:space-between">
        <h3 style="margin:0">{{ t('chapters') }}</h3>
        <button @click="chapterOpen = !chapterOpen">{{ chapterOpen ? '▾' : '▸' }}</button>
      </div>
      <div v-if="chapterOpen" style="margin-top:8px">
        <div style="display:flex;gap:8px;margin-bottom:8px">
          <button class="btn-primary" @click="genOutline" :disabled="generatingChapters">{{ t('aiGenerate') }} 大纲</button>
          <button class="btn-ghost" @click="createNewChapter">创建</button>
          <button class="btn-ghost" @click="removeChapters">删除</button>
        </div>
        <div v-if="generatingChapters" style="color:var(--muted)"><span class="spinner"></span> Generating...</div>
        <div style="margin-top:8px;display:flex;align-items:center;gap:8px">
          <div style="font-size:12px;color:#666">Page {{ chapterPage }} / {{ chapterTotalPages() }}</div>
          <button @click="changeChapterPage(chapterPage - 1)">Prev</button>
          <button @click="changeChapterPage(chapterPage + 1)">Next</button>
          <input type="number" style="width:70px" v-model.number="chapterPage" @change="changeChapterPage(chapterPage)" @keydown.enter.prevent="changeChapterPage(chapterPage)" />
        </div>
        <ul style="padding:0;list-style:none">
          <li v-for="c in chapters" :key="c.uid" style="padding:8px;border-bottom:1px solid #f5f5f5">
            <div style="display:flex;justify-content:space-between;align-items:center">
              <div style="display:flex;align-items:center;gap:8px">
                <input type="checkbox" v-model="c._checked" />
                <button style="background:none;border:none;padding:0;color:var(--link,#06c);cursor:pointer;text-decoration:underline" @click="selectChapter(c)">{{ c.title }}</button>
              </div>
              <div>
                <button @click="editChapterTitle(c)">Edit</button>
              </div>
            </div>
            <div style="font-size:12px;color:#666;margin-top:6px">{{ c.synopsis }}</div>
          </li>
        </ul>
      </div>

      <div style="display:flex;align-items:center;justify-content:space-between;margin-top:16px">
        <h3 style="margin:0">{{ t('characters') }}</h3>
        <button @click="charactersOpen = !charactersOpen">{{ charactersOpen ? '▾' : '▸' }}</button>
      </div>
      <div v-if="charactersOpen" style="margin-top:8px">
        <div style="display:flex;gap:8px;margin-bottom:8px">
          <button class="btn-primary" @click="genCharacters">{{ t('aiGenerate') }} 角色</button>
          <button class="btn-ghost" @click="createNewCharacter">创建</button>
          <button class="btn-ghost" @click="removeCharacters">删除</button>
        </div>
        <div v-if="generatingCharacters" style="color:var(--muted)"><span class="spinner"></span> Generating...</div>
        <div style="margin-top:8px;display:flex;align-items:center;gap:8px">
          <div style="font-size:12px;color:#666">Page {{ characterPage }} / {{ characterTotalPages() }}</div>
          <button @click="changeCharacterPage(characterPage - 1)">Prev</button>
          <button @click="changeCharacterPage(characterPage + 1)">Next</button>
          <input type="number" style="width:70px" v-model.number="characterPage" @change="changeCharacterPage(characterPage)" @keydown.enter.prevent="changeCharacterPage(characterPage)" />
        </div>
        <ul style="padding:0;list-style:none">
          <li v-for="c in characters" :key="c.uid" style="padding:8px;border-bottom:1px solid #f5f5f5;display:flex;justify-content:space-between;align-items:center">
            <div style="display:flex;gap:8px;align-items:center">
              <input type="checkbox" v-model="c._checked" />
              <div style="flex:1;text-align:center">
                <div style="font-weight:600">{{ c.name }}</div>
                <div style="font-size:12px;color:#666">{{ c.description }}</div>
              </div>
            </div>
            <div>
              <button @click="editCharacter(c)">Edit</button>
            </div>
          </li>
        </ul>
      </div>
    </aside>

    <section class="content">
      <div style="display:flex;justify-content:space-between;align-items:center">
        <h3>编辑章节</h3>
        <div style="display:flex;gap:8px;align-items:center">
          <span v-if="selectedLoading" class="muted">{{ t('loading') }}</span>
          <span v-if="saving" class="muted">{{ t('saving') || 'Saving...' }}</span>
          <span v-if="savedMessage" style="color:var(--accent)">{{ savedMessage }}</span>
          <button class="btn-primary" @click="openAi">{{ t('aiGenerate') }}</button>
          <button class="btn-ghost" @click="saveChapter" :disabled="saving">{{ t('save') }} (Ctrl+S)</button>
          <button class="btn-ghost" @click="() => router.push({ name: 'novel-list' })">{{ t('return') }}</button>
        </div>
      </div>

      <div v-if="!selectedChapter" style="margin-top:12px;color:#666">{{ t('selectChapterPrompt') }}</div>

      <div v-else style="margin-top:12px;display:flex;flex-direction:column;gap:8px;flex:1">
        <div class="editor-row" style="display:flex;gap:12px;align-items:stretch;flex:1">
          <div class="editor-panel" style="flex:1;display:flex;flex-direction:column;gap:8px">
            <input v-model="editorTitle" style="font-size:18px;padding:8px;background:transparent;color:var(--text);border:1px solid rgba(255,255,255,0.03);border-radius:6px" />
            <textarea v-model="editorContent" :placeholder="t('editorPlaceholder')" style="flex:1;min-height:calc(100vh - 260px);padding:12px;font-family:inherit;background:rgba(255,255,255,0.03);color:var(--text);border:1px solid rgba(255,255,255,0.03);border-radius:6px"></textarea>
          </div>
        </div>
      </div>
    </section>

    <!-- AI panel on the right (sibling column) -->
    <div class="ai-panel" v-if="aiVisible">
      <AiDialog ref="aiRef" :chapter_uid="selectedChapter?.uid" @insert="handleAiInsert" @open="aiVisible = true" @close="aiVisible = false" />
    </div>

    <ConfirmModal />
    <Toast />
  </div>
</template>
