import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { listChapters, listCharacters, ssePost, updateChapter, updateCharacter, deleteChapters, deleteCharacters, getChapter, createChapter, createCharacter } from '../api';
import AiDialog from '../components/AiDialog.vue';
import useI18n from '../i18n';
import { pushToast } from '../utils/toast';
import { showConfirm } from '../utils/confirm';
import ConfirmModal from '../components/ConfirmModal.vue';
import Toast from '../components/Toast.vue';
const { t } = useI18n();
const route = useRoute();
const router = useRouter();
const uid = String(route.params.uid || '');
const chapters = ref([]);
const characters = ref([]);
// pagination state for chapters
const chapterPage = ref(1);
const chapterSize = ref(10);
const chapterTotal = ref(0);
// pagination state for characters
const characterPage = ref(1);
const characterSize = ref(10);
const characterTotal = ref(0);
const loading = ref(false);
const generatingChapters = ref(false);
const generatingCharacters = ref(false);
const chapterOpen = ref(true);
const charactersOpen = ref(true);
const selectedChapter = ref(null);
const editorContent = ref('');
const editorTitle = ref('');
const selectedLoading = ref(false);
const saving = ref(false);
const savedMessage = ref('');
const aiRef = ref(null);
const aiVisible = ref(false);
function chapterTotalPages() {
    return Math.max(1, Math.ceil(chapterTotal.value / chapterSize.value));
}
function characterTotalPages() {
    return Math.max(1, Math.ceil(characterTotal.value / characterSize.value));
}
function changeChapterPage(p) {
    const max = chapterTotalPages();
    if (p < 1)
        p = 1;
    if (p > max)
        p = max;
    chapterPage.value = p;
    load();
}
function changeCharacterPage(p) {
    const max = characterTotalPages();
    if (p < 1)
        p = 1;
    if (p > max)
        p = max;
    characterPage.value = p;
    load();
}
async function load() {
    loading.value = true;
    // chapters with pagination
    const cRes = await listChapters(uid, chapterPage.value, chapterSize.value);
    const rawChapters = cRes?.data?.items || [];
    chapterTotal.value = cRes?.data?.total || 0;
    chapters.value = rawChapters.map((it) => ({ ...it, uid: it.uid || it.chapter_uid || (it.chapter && it.chapter.uid) }));
    // characters with pagination
    const chRes = await listCharacters(uid, characterPage.value, characterSize.value);
    const rawChars = chRes?.data?.items || [];
    characterTotal.value = chRes?.data?.total || 0;
    characters.value = rawChars.map((it) => ({ ...it, uid: it.uid || it.character_uid || (it.character && it.character.uid) }));
    loading.value = false;
}
onMounted(load);
async function genOutline() {
    generatingChapters.value = true;
    chapters.value = [];
    await ssePost('/working_flow/create_chapter_outline', { novel_uid: uid, provider: 'deepseek' }, (data) => {
        if (data.type === 'chapter' && data.chapter) {
            const ch = data.chapter;
            chapters.value.push({ title: ch.title, synopsis: ch.synopsis, uid: ch.uid || ch.chapter_uid });
        }
    }, async () => {
        generatingChapters.value = false;
        // refresh current page
        await load();
    });
}
async function genCharacters() {
    generatingCharacters.value = true;
    characters.value = [];
    try {
        await ssePost('/working_flow/create_characters', { novel_uid: uid, provider: 'deepseek' }, (data) => {
            if (data.type === 'character' && data.character) {
                const cc = data.character;
                characters.value.push({ name: cc.name, description: cc.description, uid: cc.uid || cc.character_uid });
            }
        }, async () => {
            generatingCharacters.value = false;
            await load();
        });
    }
    catch (e) {
        generatingCharacters.value = false;
        throw e;
    }
}
async function selectChapter(ch) {
    selectedChapter.value = null;
    editorContent.value = '';
    editorTitle.value = '';
    if (!ch?.uid)
        return;
    selectedLoading.value = true;
    try {
        const res = await getChapter(ch.uid);
        const d = res?.data;
        selectedChapter.value = d;
        editorContent.value = d?.content || '';
        editorTitle.value = d?.title || '';
    }
    finally {
        selectedLoading.value = false;
    }
}
async function saveChapter() {
    if (!selectedChapter.value) {
        pushToast('No chapter selected', 'error');
        return;
    }
    saving.value = true;
    savedMessage.value = '';
    try {
        await updateChapter({ uid: selectedChapter.value.uid, title: editorTitle.value, content: editorContent.value });
        savedMessage.value = 'Saved';
        setTimeout(() => (savedMessage.value = ''), 2000);
        await load();
    }
    catch (e) {
        pushToast('Save failed: ' + (e?.message || e), 'error');
    }
    finally {
        saving.value = false;
    }
}
function openAi() {
    // ensure AI panel is mounted and visible, then open it
    aiVisible.value = true;
    nextTick(() => { if (aiRef.value && aiRef.value.open)
        aiRef.value.open(); });
}
function handleAiInsert(content) {
    // append into editor
    editorContent.value += '\n' + content;
}
async function editChapterTitle(ch) {
    const t = prompt('New chapter title', ch.title);
    if (!t)
        return;
    await updateChapter({ uid: ch.uid, title: t });
    await load();
    pushToast('Chapter updated', 'success');
}
async function editCharacter(c) {
    const name = prompt('Name', c.name);
    const desc = prompt('Description', c.description);
    if (!name && !desc)
        return;
    await updateCharacter({ uid: c.uid, name, description: desc });
    await load();
    pushToast('Character updated', 'success');
}
async function removeChapters() {
    const uids = chapters.value.filter((c) => c._checked).map((c) => c.uid);
    if (!uids.length) {
        pushToast('select', 'error');
        return;
    }
    if (!await showConfirm('Delete selected chapters?'))
        return;
    await deleteChapters(uids);
    await load();
    pushToast('Deleted chapters', 'success');
}
async function removeCharacters() {
    const uids = characters.value.filter((c) => c._checked).map((c) => c.uid);
    if (!uids.length) {
        pushToast('select', 'error');
        return;
    }
    if (!await showConfirm('Delete selected characters?'))
        return;
    await deleteCharacters(uids);
    await load();
    pushToast('Deleted characters', 'success');
}
async function createNewChapter() {
    const title = prompt('Chapter title');
    if (!title)
        return;
    try {
        const res = await createChapter({ novel_uid: uid, chapter_idx: chapters.value.length + 1, title, content: '' });
        // reload to pick up normalized uid
        await load();
        // try to select the new chapter if returned
        const newUid = res?.data?.uid || res?.uid || (res?.data && res.data.uid);
        if (newUid) {
            const found = chapters.value.find((c) => c.uid === newUid);
            if (found)
                selectChapter(found);
        }
    }
    catch (e) {
        pushToast('Create chapter failed: ' + (e?.message || e), 'error');
    }
}
async function createNewCharacter() {
    const name = prompt('Character name');
    if (!name)
        return;
    try {
        await createCharacter({ novel_uid: uid, name, description: '' });
        await load();
    }
    catch (e) {
        pushToast('Create character failed: ' + (e?.message || e), 'error');
    }
}
function onKeydown(e) {
    const isMac = navigator.platform.toUpperCase().includes('MAC');
    const saveKey = isMac ? e.metaKey && e.key === 's' : e.ctrlKey && e.key === 's';
    if (saveKey) {
        e.preventDefault();
        saveChapter();
    }
}
window.addEventListener('keydown', onKeydown);
onBeforeUnmount(() => window.removeEventListener('keydown', onKeydown));
const __VLS_ctx = {
    ...{},
    ...{},
};
let __VLS_components;
let __VLS_intrinsics;
let __VLS_directives;
__VLS_asFunctionalElement1(__VLS_intrinsics.div, __VLS_intrinsics.div)({
    ...{ class: "layout" },
});
/** @type {__VLS_StyleScopedClasses['layout']} */ ;
__VLS_asFunctionalElement1(__VLS_intrinsics.aside, __VLS_intrinsics.aside)({
    ...{ class: "sidebar" },
});
/** @type {__VLS_StyleScopedClasses['sidebar']} */ ;
__VLS_asFunctionalElement1(__VLS_intrinsics.div, __VLS_intrinsics.div)({
    ...{ style: {} },
});
__VLS_asFunctionalElement1(__VLS_intrinsics.h3, __VLS_intrinsics.h3)({
    ...{ style: {} },
});
(__VLS_ctx.t('chapters'));
__VLS_asFunctionalElement1(__VLS_intrinsics.button, __VLS_intrinsics.button)({
    ...{ onClick: (...[$event]) => {
            __VLS_ctx.chapterOpen = !__VLS_ctx.chapterOpen;
            // @ts-ignore
            [t, chapterOpen, chapterOpen,];
        } },
});
(__VLS_ctx.chapterOpen ? '▾' : '▸');
if (__VLS_ctx.chapterOpen) {
    __VLS_asFunctionalElement1(__VLS_intrinsics.div, __VLS_intrinsics.div)({
        ...{ style: {} },
    });
    __VLS_asFunctionalElement1(__VLS_intrinsics.div, __VLS_intrinsics.div)({
        ...{ style: {} },
    });
    __VLS_asFunctionalElement1(__VLS_intrinsics.button, __VLS_intrinsics.button)({
        ...{ onClick: (__VLS_ctx.genOutline) },
        ...{ class: "btn-primary" },
        disabled: (__VLS_ctx.generatingChapters),
    });
    /** @type {__VLS_StyleScopedClasses['btn-primary']} */ ;
    (__VLS_ctx.t('aiGenerate'));
    __VLS_asFunctionalElement1(__VLS_intrinsics.button, __VLS_intrinsics.button)({
        ...{ onClick: (__VLS_ctx.createNewChapter) },
        ...{ class: "btn-ghost" },
    });
    /** @type {__VLS_StyleScopedClasses['btn-ghost']} */ ;
    __VLS_asFunctionalElement1(__VLS_intrinsics.button, __VLS_intrinsics.button)({
        ...{ onClick: (__VLS_ctx.removeChapters) },
        ...{ class: "btn-ghost" },
    });
    /** @type {__VLS_StyleScopedClasses['btn-ghost']} */ ;
    if (__VLS_ctx.generatingChapters) {
        __VLS_asFunctionalElement1(__VLS_intrinsics.div, __VLS_intrinsics.div)({
            ...{ style: {} },
        });
        __VLS_asFunctionalElement1(__VLS_intrinsics.span, __VLS_intrinsics.span)({
            ...{ class: "spinner" },
        });
        /** @type {__VLS_StyleScopedClasses['spinner']} */ ;
    }
    __VLS_asFunctionalElement1(__VLS_intrinsics.div, __VLS_intrinsics.div)({
        ...{ style: {} },
    });
    __VLS_asFunctionalElement1(__VLS_intrinsics.div, __VLS_intrinsics.div)({
        ...{ style: {} },
    });
    (__VLS_ctx.chapterPage);
    (__VLS_ctx.chapterTotalPages());
    __VLS_asFunctionalElement1(__VLS_intrinsics.button, __VLS_intrinsics.button)({
        ...{ onClick: (...[$event]) => {
                if (!(__VLS_ctx.chapterOpen))
                    return;
                __VLS_ctx.changeChapterPage(__VLS_ctx.chapterPage - 1);
                // @ts-ignore
                [t, chapterOpen, chapterOpen, genOutline, generatingChapters, generatingChapters, createNewChapter, removeChapters, chapterPage, chapterPage, chapterTotalPages, changeChapterPage,];
            } },
    });
    __VLS_asFunctionalElement1(__VLS_intrinsics.button, __VLS_intrinsics.button)({
        ...{ onClick: (...[$event]) => {
                if (!(__VLS_ctx.chapterOpen))
                    return;
                __VLS_ctx.changeChapterPage(__VLS_ctx.chapterPage + 1);
                // @ts-ignore
                [chapterPage, changeChapterPage,];
            } },
    });
    __VLS_asFunctionalElement1(__VLS_intrinsics.input)({
        ...{ onChange: (...[$event]) => {
                if (!(__VLS_ctx.chapterOpen))
                    return;
                __VLS_ctx.changeChapterPage(__VLS_ctx.chapterPage);
                // @ts-ignore
                [chapterPage, changeChapterPage,];
            } },
        ...{ onKeydown: (...[$event]) => {
                if (!(__VLS_ctx.chapterOpen))
                    return;
                __VLS_ctx.changeChapterPage(__VLS_ctx.chapterPage);
                // @ts-ignore
                [chapterPage, changeChapterPage,];
            } },
        type: "number",
        ...{ style: {} },
    });
    (__VLS_ctx.chapterPage);
    __VLS_asFunctionalElement1(__VLS_intrinsics.ul, __VLS_intrinsics.ul)({
        ...{ style: {} },
    });
    for (const [c] of __VLS_vFor((__VLS_ctx.chapters))) {
        __VLS_asFunctionalElement1(__VLS_intrinsics.li, __VLS_intrinsics.li)({
            key: (c.uid),
            ...{ style: {} },
        });
        __VLS_asFunctionalElement1(__VLS_intrinsics.div, __VLS_intrinsics.div)({
            ...{ style: {} },
        });
        __VLS_asFunctionalElement1(__VLS_intrinsics.div, __VLS_intrinsics.div)({
            ...{ style: {} },
        });
        __VLS_asFunctionalElement1(__VLS_intrinsics.input)({
            type: "checkbox",
        });
        (c._checked);
        __VLS_asFunctionalElement1(__VLS_intrinsics.button, __VLS_intrinsics.button)({
            ...{ onClick: (...[$event]) => {
                    if (!(__VLS_ctx.chapterOpen))
                        return;
                    __VLS_ctx.selectChapter(c);
                    // @ts-ignore
                    [chapterPage, chapters, selectChapter,];
                } },
            ...{ style: {} },
        });
        (c.title);
        __VLS_asFunctionalElement1(__VLS_intrinsics.div, __VLS_intrinsics.div)({});
        __VLS_asFunctionalElement1(__VLS_intrinsics.button, __VLS_intrinsics.button)({
            ...{ onClick: (...[$event]) => {
                    if (!(__VLS_ctx.chapterOpen))
                        return;
                    __VLS_ctx.editChapterTitle(c);
                    // @ts-ignore
                    [editChapterTitle,];
                } },
        });
        __VLS_asFunctionalElement1(__VLS_intrinsics.div, __VLS_intrinsics.div)({
            ...{ style: {} },
        });
        (c.synopsis);
        // @ts-ignore
        [];
    }
}
__VLS_asFunctionalElement1(__VLS_intrinsics.div, __VLS_intrinsics.div)({
    ...{ style: {} },
});
__VLS_asFunctionalElement1(__VLS_intrinsics.h3, __VLS_intrinsics.h3)({
    ...{ style: {} },
});
(__VLS_ctx.t('characters'));
__VLS_asFunctionalElement1(__VLS_intrinsics.button, __VLS_intrinsics.button)({
    ...{ onClick: (...[$event]) => {
            __VLS_ctx.charactersOpen = !__VLS_ctx.charactersOpen;
            // @ts-ignore
            [t, charactersOpen, charactersOpen,];
        } },
});
(__VLS_ctx.charactersOpen ? '▾' : '▸');
if (__VLS_ctx.charactersOpen) {
    __VLS_asFunctionalElement1(__VLS_intrinsics.div, __VLS_intrinsics.div)({
        ...{ style: {} },
    });
    __VLS_asFunctionalElement1(__VLS_intrinsics.div, __VLS_intrinsics.div)({
        ...{ style: {} },
    });
    __VLS_asFunctionalElement1(__VLS_intrinsics.button, __VLS_intrinsics.button)({
        ...{ onClick: (__VLS_ctx.genCharacters) },
        ...{ class: "btn-primary" },
    });
    /** @type {__VLS_StyleScopedClasses['btn-primary']} */ ;
    (__VLS_ctx.t('aiGenerate'));
    __VLS_asFunctionalElement1(__VLS_intrinsics.button, __VLS_intrinsics.button)({
        ...{ onClick: (__VLS_ctx.createNewCharacter) },
        ...{ class: "btn-ghost" },
    });
    /** @type {__VLS_StyleScopedClasses['btn-ghost']} */ ;
    __VLS_asFunctionalElement1(__VLS_intrinsics.button, __VLS_intrinsics.button)({
        ...{ onClick: (__VLS_ctx.removeCharacters) },
        ...{ class: "btn-ghost" },
    });
    /** @type {__VLS_StyleScopedClasses['btn-ghost']} */ ;
    if (__VLS_ctx.generatingCharacters) {
        __VLS_asFunctionalElement1(__VLS_intrinsics.div, __VLS_intrinsics.div)({
            ...{ style: {} },
        });
        __VLS_asFunctionalElement1(__VLS_intrinsics.span, __VLS_intrinsics.span)({
            ...{ class: "spinner" },
        });
        /** @type {__VLS_StyleScopedClasses['spinner']} */ ;
    }
    __VLS_asFunctionalElement1(__VLS_intrinsics.div, __VLS_intrinsics.div)({
        ...{ style: {} },
    });
    __VLS_asFunctionalElement1(__VLS_intrinsics.div, __VLS_intrinsics.div)({
        ...{ style: {} },
    });
    (__VLS_ctx.characterPage);
    (__VLS_ctx.characterTotalPages());
    __VLS_asFunctionalElement1(__VLS_intrinsics.button, __VLS_intrinsics.button)({
        ...{ onClick: (...[$event]) => {
                if (!(__VLS_ctx.charactersOpen))
                    return;
                __VLS_ctx.changeCharacterPage(__VLS_ctx.characterPage - 1);
                // @ts-ignore
                [t, charactersOpen, charactersOpen, genCharacters, createNewCharacter, removeCharacters, generatingCharacters, characterPage, characterPage, characterTotalPages, changeCharacterPage,];
            } },
    });
    __VLS_asFunctionalElement1(__VLS_intrinsics.button, __VLS_intrinsics.button)({
        ...{ onClick: (...[$event]) => {
                if (!(__VLS_ctx.charactersOpen))
                    return;
                __VLS_ctx.changeCharacterPage(__VLS_ctx.characterPage + 1);
                // @ts-ignore
                [characterPage, changeCharacterPage,];
            } },
    });
    __VLS_asFunctionalElement1(__VLS_intrinsics.input)({
        ...{ onChange: (...[$event]) => {
                if (!(__VLS_ctx.charactersOpen))
                    return;
                __VLS_ctx.changeCharacterPage(__VLS_ctx.characterPage);
                // @ts-ignore
                [characterPage, changeCharacterPage,];
            } },
        ...{ onKeydown: (...[$event]) => {
                if (!(__VLS_ctx.charactersOpen))
                    return;
                __VLS_ctx.changeCharacterPage(__VLS_ctx.characterPage);
                // @ts-ignore
                [characterPage, changeCharacterPage,];
            } },
        type: "number",
        ...{ style: {} },
    });
    (__VLS_ctx.characterPage);
    __VLS_asFunctionalElement1(__VLS_intrinsics.ul, __VLS_intrinsics.ul)({
        ...{ style: {} },
    });
    for (const [c] of __VLS_vFor((__VLS_ctx.characters))) {
        __VLS_asFunctionalElement1(__VLS_intrinsics.li, __VLS_intrinsics.li)({
            key: (c.uid),
            ...{ style: {} },
        });
        __VLS_asFunctionalElement1(__VLS_intrinsics.div, __VLS_intrinsics.div)({
            ...{ style: {} },
        });
        __VLS_asFunctionalElement1(__VLS_intrinsics.input)({
            type: "checkbox",
        });
        (c._checked);
        __VLS_asFunctionalElement1(__VLS_intrinsics.div, __VLS_intrinsics.div)({
            ...{ style: {} },
        });
        __VLS_asFunctionalElement1(__VLS_intrinsics.div, __VLS_intrinsics.div)({
            ...{ style: {} },
        });
        (c.name);
        __VLS_asFunctionalElement1(__VLS_intrinsics.div, __VLS_intrinsics.div)({
            ...{ style: {} },
        });
        (c.description);
        __VLS_asFunctionalElement1(__VLS_intrinsics.div, __VLS_intrinsics.div)({});
        __VLS_asFunctionalElement1(__VLS_intrinsics.button, __VLS_intrinsics.button)({
            ...{ onClick: (...[$event]) => {
                    if (!(__VLS_ctx.charactersOpen))
                        return;
                    __VLS_ctx.editCharacter(c);
                    // @ts-ignore
                    [characterPage, characters, editCharacter,];
                } },
        });
        // @ts-ignore
        [];
    }
}
__VLS_asFunctionalElement1(__VLS_intrinsics.section, __VLS_intrinsics.section)({
    ...{ class: "content" },
});
/** @type {__VLS_StyleScopedClasses['content']} */ ;
__VLS_asFunctionalElement1(__VLS_intrinsics.div, __VLS_intrinsics.div)({
    ...{ style: {} },
});
__VLS_asFunctionalElement1(__VLS_intrinsics.h3, __VLS_intrinsics.h3)({});
__VLS_asFunctionalElement1(__VLS_intrinsics.div, __VLS_intrinsics.div)({
    ...{ style: {} },
});
if (__VLS_ctx.selectedLoading) {
    __VLS_asFunctionalElement1(__VLS_intrinsics.span, __VLS_intrinsics.span)({
        ...{ class: "muted" },
    });
    /** @type {__VLS_StyleScopedClasses['muted']} */ ;
    (__VLS_ctx.t('loading'));
}
if (__VLS_ctx.saving) {
    __VLS_asFunctionalElement1(__VLS_intrinsics.span, __VLS_intrinsics.span)({
        ...{ class: "muted" },
    });
    /** @type {__VLS_StyleScopedClasses['muted']} */ ;
    (__VLS_ctx.t('saving') || 'Saving...');
}
if (__VLS_ctx.savedMessage) {
    __VLS_asFunctionalElement1(__VLS_intrinsics.span, __VLS_intrinsics.span)({
        ...{ style: {} },
    });
    (__VLS_ctx.savedMessage);
}
__VLS_asFunctionalElement1(__VLS_intrinsics.button, __VLS_intrinsics.button)({
    ...{ onClick: (__VLS_ctx.openAi) },
    ...{ class: "btn-primary" },
});
/** @type {__VLS_StyleScopedClasses['btn-primary']} */ ;
(__VLS_ctx.t('aiGenerate'));
__VLS_asFunctionalElement1(__VLS_intrinsics.button, __VLS_intrinsics.button)({
    ...{ onClick: (__VLS_ctx.saveChapter) },
    ...{ class: "btn-ghost" },
    disabled: (__VLS_ctx.saving),
});
/** @type {__VLS_StyleScopedClasses['btn-ghost']} */ ;
(__VLS_ctx.t('save'));
__VLS_asFunctionalElement1(__VLS_intrinsics.button, __VLS_intrinsics.button)({
    ...{ onClick: (() => __VLS_ctx.router.push({ name: 'novel-list' })) },
    ...{ class: "btn-ghost" },
});
/** @type {__VLS_StyleScopedClasses['btn-ghost']} */ ;
(__VLS_ctx.t('return'));
if (!__VLS_ctx.selectedChapter) {
    __VLS_asFunctionalElement1(__VLS_intrinsics.div, __VLS_intrinsics.div)({
        ...{ style: {} },
    });
    (__VLS_ctx.t('selectChapterPrompt'));
}
else {
    __VLS_asFunctionalElement1(__VLS_intrinsics.div, __VLS_intrinsics.div)({
        ...{ style: {} },
    });
    __VLS_asFunctionalElement1(__VLS_intrinsics.div, __VLS_intrinsics.div)({
        ...{ class: "editor-row" },
        ...{ style: {} },
    });
    /** @type {__VLS_StyleScopedClasses['editor-row']} */ ;
    __VLS_asFunctionalElement1(__VLS_intrinsics.div, __VLS_intrinsics.div)({
        ...{ class: "editor-panel" },
        ...{ style: {} },
    });
    /** @type {__VLS_StyleScopedClasses['editor-panel']} */ ;
    __VLS_asFunctionalElement1(__VLS_intrinsics.input)({
        ...{ style: {} },
    });
    (__VLS_ctx.editorTitle);
    __VLS_asFunctionalElement1(__VLS_intrinsics.textarea, __VLS_intrinsics.textarea)({
        value: (__VLS_ctx.editorContent),
        placeholder: (__VLS_ctx.t('editorPlaceholder')),
        ...{ style: {} },
    });
}
if (__VLS_ctx.aiVisible) {
    __VLS_asFunctionalElement1(__VLS_intrinsics.div, __VLS_intrinsics.div)({
        ...{ class: "ai-panel" },
    });
    /** @type {__VLS_StyleScopedClasses['ai-panel']} */ ;
    const __VLS_0 = AiDialog;
    // @ts-ignore
    const __VLS_1 = __VLS_asFunctionalComponent1(__VLS_0, new __VLS_0({
        ...{ 'onInsert': {} },
        ...{ 'onOpen': {} },
        ...{ 'onClose': {} },
        ref: "aiRef",
        chapter_uid: (__VLS_ctx.selectedChapter?.uid),
    }));
    const __VLS_2 = __VLS_1({
        ...{ 'onInsert': {} },
        ...{ 'onOpen': {} },
        ...{ 'onClose': {} },
        ref: "aiRef",
        chapter_uid: (__VLS_ctx.selectedChapter?.uid),
    }, ...__VLS_functionalComponentArgsRest(__VLS_1));
    let __VLS_5;
    const __VLS_6 = ({ insert: {} },
        { onInsert: (__VLS_ctx.handleAiInsert) });
    const __VLS_7 = ({ open: {} },
        { onOpen: (...[$event]) => {
                if (!(__VLS_ctx.aiVisible))
                    return;
                __VLS_ctx.aiVisible = true;
                // @ts-ignore
                [t, t, t, t, t, t, t, selectedLoading, saving, saving, savedMessage, savedMessage, openAi, saveChapter, router, selectedChapter, selectedChapter, editorTitle, editorContent, aiVisible, aiVisible, handleAiInsert,];
            } });
    const __VLS_8 = ({ close: {} },
        { onClose: (...[$event]) => {
                if (!(__VLS_ctx.aiVisible))
                    return;
                __VLS_ctx.aiVisible = false;
                // @ts-ignore
                [aiVisible,];
            } });
    var __VLS_9 = {};
    var __VLS_3;
    var __VLS_4;
}
const __VLS_11 = ConfirmModal;
// @ts-ignore
const __VLS_12 = __VLS_asFunctionalComponent1(__VLS_11, new __VLS_11({}));
const __VLS_13 = __VLS_12({}, ...__VLS_functionalComponentArgsRest(__VLS_12));
const __VLS_16 = Toast;
// @ts-ignore
const __VLS_17 = __VLS_asFunctionalComponent1(__VLS_16, new __VLS_16({}));
const __VLS_18 = __VLS_17({}, ...__VLS_functionalComponentArgsRest(__VLS_17));
// @ts-ignore
var __VLS_10 = __VLS_9;
// @ts-ignore
[];
const __VLS_export = (await import('vue')).defineComponent({});
export default {};
//# sourceMappingURL=NovelEditor.vue.js.map