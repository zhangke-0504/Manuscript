import { ref, watch } from 'vue';
import { ssePost } from '../api';
import useI18n from '../i18n';
import { provider } from '../store/provider';
const props = defineProps();
const emit = defineEmits(['insert', 'open', 'close']);
const visible = ref(false);
const sessions = ref([]);
const selected = ref(0);
const { t } = useI18n();
const input = ref('');
const streaming = ref(false);
const errorMsg = ref('');
const storageKey = () => `ai_sessions:${props.chapter_uid || 'global'}`;
function loadSessions() {
    try {
        const raw = localStorage.getItem(storageKey());
        sessions.value = raw ? JSON.parse(raw) : [];
    }
    catch {
        sessions.value = [];
    }
    if (!sessions.value.length)
        createSession();
    if (selected.value >= sessions.value.length)
        selected.value = sessions.value.length - 1;
}
function saveSessions() {
    try {
        localStorage.setItem(storageKey(), JSON.stringify(sessions.value));
    }
    catch { }
}
function createSession() {
    const s = { id: Date.now().toString(), created_at: Date.now(), messages: [] };
    sessions.value.push(s);
    selected.value = sessions.value.length - 1;
    saveSessions();
}
import { showConfirm } from '../utils/confirm';
async function deleteSession(idx) {
    const ok = await showConfirm('Delete this AI session?');
    if (!ok)
        return;
    sessions.value.splice(idx, 1);
    if (!sessions.value.length)
        createSession();
    if (selected.value >= sessions.value.length)
        selected.value = sessions.value.length - 1;
    saveSessions();
}
function open() {
    loadSessions();
    // set default prompt when opening if empty
    if (!input.value)
        input.value = t('aiDefaultPrompt');
    visible.value = true;
}
function close() { visible.value = false; emit('close'); }
// notify parent when opened/closed
watch(visible, (v) => { if (v)
    emit('open'); });
watch(sessions, saveSessions, { deep: true });
async function send() {
    const prompt = input.value.trim();
    if (!prompt)
        return;
    const sess = sessions.value[selected.value];
    sess.messages.push({ role: 'user', content: prompt });
    input.value = '';
    errorMsg.value = '';
    streaming.value = true;
    // ensure an assistant placeholder exists
    sess.messages.push({ role: 'assistant', content: '' });
    const assistantIndex = sess.messages.length - 1;
    await ssePost('/working_flow/create_chapter_content', { chapter_uid: props.chapter_uid, provider: provider.value, conversation_messages: sess.messages }, (data) => {
        if (!data)
            return;
        if (data.type === 'error') {
            errorMsg.value = data.message || 'Stream error';
            streaming.value = false;
            return;
        }
        if (data.type === 'token') {
            const token = data.token || '';
            const last = sess.messages[assistantIndex];
            if (!last || last.role !== 'assistant')
                sess.messages.push({ role: 'assistant', content: token });
            else
                last.content += token;
        }
        else if (data.type === 'assistant' && data.content) {
            sess.messages[assistantIndex].content += data.content;
        }
        else if (typeof data === 'string') {
            sess.messages[assistantIndex].content += data;
        }
    }, () => {
        streaming.value = false;
        saveSessions();
    }, { retries: 2, retryDelay: 1000 });
}
function insertToEditor(content) {
    emit('insert', content);
}
function copyToClipboard(text) {
    try {
        navigator.clipboard.writeText(text);
    }
    catch { }
}
const __VLS_exposed = { open, close };
defineExpose(__VLS_exposed);
const __VLS_ctx = {
    ...{},
    ...{},
    ...{},
    ...{},
    ...{},
};
let __VLS_components;
let __VLS_intrinsics;
let __VLS_directives;
/** @type {__VLS_StyleScopedClasses['ai-select']} */ ;
/** @type {__VLS_StyleScopedClasses['ai-message']} */ ;
/** @type {__VLS_StyleScopedClasses['ai-message']} */ ;
/** @type {__VLS_StyleScopedClasses['ai-message']} */ ;
/** @type {__VLS_StyleScopedClasses['user']} */ ;
/** @type {__VLS_StyleScopedClasses['ai-bubble']} */ ;
/** @type {__VLS_StyleScopedClasses['ai-input']} */ ;
/** @type {__VLS_StyleScopedClasses['ai-controls']} */ ;
/** @type {__VLS_StyleScopedClasses['ai-actions']} */ ;
/** @type {__VLS_StyleScopedClasses['btn-ghost']} */ ;
if (__VLS_ctx.visible) {
    __VLS_asFunctionalElement1(__VLS_intrinsics.div, __VLS_intrinsics.div)({
        ...{ class: "ai-dialog" },
    });
    /** @type {__VLS_StyleScopedClasses['ai-dialog']} */ ;
    __VLS_asFunctionalElement1(__VLS_intrinsics.div, __VLS_intrinsics.div)({
        ...{ class: "ai-header" },
    });
    /** @type {__VLS_StyleScopedClasses['ai-header']} */ ;
    __VLS_asFunctionalElement1(__VLS_intrinsics.div, __VLS_intrinsics.div)({
        ...{ class: "ai-sessions" },
    });
    /** @type {__VLS_StyleScopedClasses['ai-sessions']} */ ;
    __VLS_asFunctionalElement1(__VLS_intrinsics.select, __VLS_intrinsics.select)({
        value: (__VLS_ctx.selected),
        ...{ class: "ai-select" },
    });
    /** @type {__VLS_StyleScopedClasses['ai-select']} */ ;
    for (const [s, idx] of __VLS_vFor((__VLS_ctx.sessions))) {
        __VLS_asFunctionalElement1(__VLS_intrinsics.option, __VLS_intrinsics.option)({
            key: (s.id),
            value: (idx),
        });
        (idx + 1);
        (new Date(s.created_at).toLocaleString());
        // @ts-ignore
        [visible, selected, sessions,];
    }
    __VLS_asFunctionalElement1(__VLS_intrinsics.button, __VLS_intrinsics.button)({
        ...{ onClick: (__VLS_ctx.createSession) },
        ...{ class: "btn-ghost" },
    });
    /** @type {__VLS_StyleScopedClasses['btn-ghost']} */ ;
    __VLS_asFunctionalElement1(__VLS_intrinsics.button, __VLS_intrinsics.button)({
        ...{ onClick: (...[$event]) => {
                if (!(__VLS_ctx.visible))
                    return;
                __VLS_ctx.deleteSession(__VLS_ctx.selected);
                // @ts-ignore
                [selected, createSession, deleteSession,];
            } },
        ...{ class: "btn-ghost" },
    });
    /** @type {__VLS_StyleScopedClasses['btn-ghost']} */ ;
    __VLS_asFunctionalElement1(__VLS_intrinsics.div, __VLS_intrinsics.div)({
        ...{ class: "ai-status" },
    });
    /** @type {__VLS_StyleScopedClasses['ai-status']} */ ;
    if (__VLS_ctx.streaming) {
        __VLS_asFunctionalElement1(__VLS_intrinsics.span, __VLS_intrinsics.span)({
            ...{ class: "muted" },
        });
        /** @type {__VLS_StyleScopedClasses['muted']} */ ;
    }
    __VLS_asFunctionalElement1(__VLS_intrinsics.div, __VLS_intrinsics.div)({
        ...{ class: "ai-messages" },
    });
    /** @type {__VLS_StyleScopedClasses['ai-messages']} */ ;
    if (__VLS_ctx.errorMsg) {
        __VLS_asFunctionalElement1(__VLS_intrinsics.div, __VLS_intrinsics.div)({
            ...{ class: "error" },
        });
        /** @type {__VLS_StyleScopedClasses['error']} */ ;
        (__VLS_ctx.errorMsg);
    }
    for (const [m, idx] of __VLS_vFor((__VLS_ctx.sessions[__VLS_ctx.selected]?.messages || []))) {
        __VLS_asFunctionalElement1(__VLS_intrinsics.div, __VLS_intrinsics.div)({
            key: (idx),
            ...{ class: (['ai-message', m.role]) },
        });
        /** @type {__VLS_StyleScopedClasses['ai-message']} */ ;
        __VLS_asFunctionalElement1(__VLS_intrinsics.div, __VLS_intrinsics.div)({
            ...{ onClick: (...[$event]) => {
                    if (!(__VLS_ctx.visible))
                        return;
                    m.role === 'assistant' && __VLS_ctx.insertToEditor(m.content);
                    // @ts-ignore
                    [selected, sessions, streaming, errorMsg, errorMsg, insertToEditor,];
                } },
            ...{ onDblclick: (...[$event]) => {
                    if (!(__VLS_ctx.visible))
                        return;
                    m.role === 'assistant' && __VLS_ctx.copyToClipboard(m.content);
                    // @ts-ignore
                    [copyToClipboard,];
                } },
            ...{ class: "ai-bubble" },
            title: (m.role === 'assistant' ? 'Click to insert, double-click to copy' : ''),
        });
        /** @type {__VLS_StyleScopedClasses['ai-bubble']} */ ;
        (m.content);
        if (m.role === 'assistant') {
            __VLS_asFunctionalElement1(__VLS_intrinsics.div, __VLS_intrinsics.div)({
                ...{ class: "ai-actions" },
            });
            /** @type {__VLS_StyleScopedClasses['ai-actions']} */ ;
            __VLS_asFunctionalElement1(__VLS_intrinsics.button, __VLS_intrinsics.button)({
                ...{ onClick: (...[$event]) => {
                        if (!(__VLS_ctx.visible))
                            return;
                        if (!(m.role === 'assistant'))
                            return;
                        __VLS_ctx.insertToEditor(m.content);
                        // @ts-ignore
                        [insertToEditor,];
                    } },
                ...{ class: "btn-ghost" },
            });
            /** @type {__VLS_StyleScopedClasses['btn-ghost']} */ ;
            __VLS_asFunctionalElement1(__VLS_intrinsics.button, __VLS_intrinsics.button)({
                ...{ onClick: (...[$event]) => {
                        if (!(__VLS_ctx.visible))
                            return;
                        if (!(m.role === 'assistant'))
                            return;
                        __VLS_ctx.copyToClipboard(m.content);
                        // @ts-ignore
                        [copyToClipboard,];
                    } },
                ...{ class: "btn-ghost" },
            });
            /** @type {__VLS_StyleScopedClasses['btn-ghost']} */ ;
        }
        // @ts-ignore
        [];
    }
    __VLS_asFunctionalElement1(__VLS_intrinsics.div, __VLS_intrinsics.div)({
        ...{ class: "ai-input" },
    });
    /** @type {__VLS_StyleScopedClasses['ai-input']} */ ;
    __VLS_asFunctionalElement1(__VLS_intrinsics.textarea, __VLS_intrinsics.textarea)({
        ...{ onKeydown: ((e) => { if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                __VLS_ctx.send();
            } }) },
        value: (__VLS_ctx.input),
        placeholder: "Type message, Enter to send, Shift+Enter newline",
    });
    __VLS_asFunctionalElement1(__VLS_intrinsics.div, __VLS_intrinsics.div)({
        ...{ class: "ai-controls" },
    });
    /** @type {__VLS_StyleScopedClasses['ai-controls']} */ ;
    __VLS_asFunctionalElement1(__VLS_intrinsics.button, __VLS_intrinsics.button)({
        ...{ onClick: (__VLS_ctx.send) },
        ...{ class: "btn-primary" },
    });
    /** @type {__VLS_StyleScopedClasses['btn-primary']} */ ;
    __VLS_asFunctionalElement1(__VLS_intrinsics.button, __VLS_intrinsics.button)({
        ...{ onClick: (__VLS_ctx.close) },
        ...{ class: "btn-ghost" },
    });
    /** @type {__VLS_StyleScopedClasses['btn-ghost']} */ ;
}
// @ts-ignore
[send, send, input, close,];
const __VLS_export = (await import('vue')).defineComponent({
    setup: () => (__VLS_exposed),
    emits: {},
    __typeProps: {},
});
export default {};
//# sourceMappingURL=AiDialog.vue.js.map