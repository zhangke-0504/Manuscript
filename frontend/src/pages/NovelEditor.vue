<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { listChapters, listCharacters, ssePost, updateChapter, updateCharacter, deleteChapters, deleteCharacters, getChapter, getCharacter, createChapter, createCharacter } from '../api'
import AiDialog from '../components/AiDialog.vue'
import useI18n from '../i18n'

const { t } = useI18n()

const route = useRoute()
const router = useRouter()
const uid = String(route.params.uid || '')

const chapters = ref<any[]>([])
const characters = ref<any[]>([])
const loading = ref(false)
const generating = ref(false)
const chapterOpen = ref(true)
const charactersOpen = ref(true)

const selectedChapter = ref<any>(null)
const editorContent = ref('')
const editorTitle = ref('')
const selectedLoading = ref(false)
const saving = ref(false)
const savedMessage = ref('')

const aiRef = ref<any>(null)

async function load() {
  loading.value = true
  const cRes = await listChapters(uid)
  // normalize chapter items to always have `uid`
  const rawChapters = cRes?.data?.items || []
  chapters.value = rawChapters.map((it: any) => ({ ...it, uid: it.uid || it.chapter_uid || (it.chapter && it.chapter.uid) }))
  const chRes = await listCharacters(uid)
  // normalize character items to always have `uid`
  const rawChars = chRes?.data?.items || []
  characters.value = rawChars.map((it: any) => ({ ...it, uid: it.uid || it.character_uid || (it.character && it.character.uid) }))
  loading.value = false
}

onMounted(load)

async function genOutline() {
  generating.value = true
  chapters.value = []
  await ssePost('/working_flow/create_chapter_outline', { novel_uid: uid, provider: 'deepseek' }, (data) => {
    if (data.type === 'chapter' && data.chapter) {
      const ch = data.chapter
      chapters.value.push({ title: ch.title, synopsis: ch.synopsis, uid: ch.uid || ch.chapter_uid })
    }
  }, () => generating.value = false)
}

async function genCharacters() {
  characters.value = []
  await ssePost('/working_flow/create_characters', { novel_uid: uid, provider: 'deepseek' }, (data) => {
    if (data.type === 'character' && data.character) {
      const cc = data.character
      characters.value.push({ name: cc.name, description: cc.description, uid: cc.uid || cc.character_uid })
    }
  })
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
  if (!selectedChapter.value) return alert('No chapter selected')
  saving.value = true
  savedMessage.value = ''
  try {
    await updateChapter({ uid: selectedChapter.value.uid, title: editorTitle.value, content: editorContent.value })
    savedMessage.value = 'Saved'
    setTimeout(() => (savedMessage.value = ''), 2000)
    await load()
  } catch (e: any) {
    alert('Save failed: ' + (e?.message || e))
  } finally {
    saving.value = false
  }
}

function openAi() {
  if (aiRef.value && aiRef.value.open) aiRef.value.open()
}

function handleAiInsert(content: string) {
  // append into editor
  editorContent.value += '\n' + content
}

async function editChapterTitle(ch: any) {
  const t = prompt('New chapter title', ch.title)
  if (!t) return
  await updateChapter({ uid: ch.uid, title: t })
  load()
}

async function editCharacter(c: any) {
  const name = prompt('Name', c.name)
  const desc = prompt('Description', c.description)
  if (!name && !desc) return
  await updateCharacter({ uid: c.uid, name, description: desc })
  load()
}

async function removeChapters() {
  const uids = chapters.value.filter((c: any) => c._checked).map((c: any) => c.uid)
  if (!uids.length) return alert('select')
  if (!confirm('Delete selected chapters?')) return
  await deleteChapters(uids)
  load()
}

async function removeCharacters() {
  const uids = characters.value.filter((c: any) => c._checked).map((c: any) => c.uid)
  if (!uids.length) return alert('select')
  if (!confirm('Delete selected characters?')) return
  await deleteCharacters(uids)
  load()
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
    alert('Create chapter failed: ' + (e?.message || e))
  }
}

async function createNewCharacter() {
  const name = prompt('Character name')
  if (!name) return
  try {
    await createCharacter({ novel_uid: uid, name, description: '' })
    await load()
  } catch (e: any) {
    alert('Create character failed: ' + (e?.message || e))
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
  <div style="display:flex;gap:12px">
    <aside style="width:320px;border-right:1px solid #eee;padding-right:12px">
      <div style="display:flex;align-items:center;justify-content:space-between">
        <h3 style="margin:0">{{ t('chapters') }}</h3>
        <button @click="chapterOpen = !chapterOpen">{{ chapterOpen ? '▾' : '▸' }}</button>
      </div>
      <div v-if="chapterOpen" style="margin-top:8px">
        <div style="display:flex;gap:8px;margin-bottom:8px">
            <button @click="genOutline" :disabled="generating">{{ t('aiGenerate') }} 大纲</button>
            <button @click="createNewChapter">创建</button>
            <button @click="removeChapters">删除</button>
        </div>
        <div v-if="generating" style="color:#666">Generating...</div>
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
          <button @click="genCharacters">{{ t('aiGenerate') }} 角色</button>
          <button @click="createNewCharacter">创建</button>
          <button @click="removeCharacters">删除</button>
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

    <section style="flex:1;padding-left:12px;display:flex;flex-direction:column">
      <div style="display:flex;justify-content:space-between;align-items:center">
        <h3>编辑章节</h3>
        <div style="display:flex;gap:8px;align-items:center">
          <span v-if="selectedLoading" style="color:#666">{{ t('loading') }}</span>
          <span v-if="saving" style="color:#666">{{ t('saving') || 'Saving...' }}</span>
          <span v-if="savedMessage" style="color:green">{{ savedMessage }}</span>
          <button @click="openAi">{{ t('aiGenerate') }}</button>
          <button @click="saveChapter" :disabled="saving">{{ t('save') }} (Ctrl+S)</button>
          <button @click="() => router.push({ name: 'novel-list' })">{{ t('return') }}</button>
        </div>
      </div>

      <div v-if="!selectedChapter" style="margin-top:12px;color:#666">{{ t('selectChapterPrompt') }}</div>

      <div v-else style="margin-top:12px;display:flex;flex-direction:column;gap:8px">
        <input v-model="editorTitle" style="font-size:18px;padding:8px" />
        <textarea v-model="editorContent" style="flex:1;min-height:320px;padding:12px;font-family:inherit" />
      </div>

      <AiDialog ref="aiRef" :chapter_uid="selectedChapter?.uid" @insert="handleAiInsert" />
    </section>
  </div>
</template>
