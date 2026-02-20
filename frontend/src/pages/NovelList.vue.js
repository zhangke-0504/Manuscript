import { ref, onMounted } from 'vue';
import { listNovels, deleteNovels, createNovel } from '../api';
import { useRouter } from 'vue-router';
import useI18n from '../i18n';
import { pushToast } from '../utils/toast';
import ConfirmModal from '../components/ConfirmModal.vue';
import { showConfirm } from '../utils/confirm';
import Toast from '../components/Toast.vue';
const { t } = useI18n();
const novels = ref([]);
const loading = ref(false);
const deleting = ref(false);
const page = ref(1);
const size = ref(10);
const total = ref(0);
const router = useRouter();
// hook up toast listener for global toast component
import { onPush } from '../utils/toast';
onPush((m) => {
    // noop here; Toast.vue subscribes via its own listener import
});
async function load() {
    loading.value = true;
    const res = await listNovels(page.value, size.value);
    novels.value = res?.data?.items || [];
    total.value = res?.data?.total || 0;
    loading.value = false;
}
onMounted(load);
function totalPages() {
    return Math.max(1, Math.ceil(total.value / size.value));
}
function changePage(p) {
    const max = totalPages();
    if (p < 1)
        p = 1;
    if (p > max)
        p = max;
    page.value = p;
    load();
}
async function onCreate() {
    const title = prompt('Novel title');
    if (!title)
        return;
    const res = await createNovel({ title, genre: '未知', description: '' });
    // After creating an asset, stay on the asset list page and refresh
    await load();
}
async function onDeleteSelected() {
    const checked = document.querySelectorAll('input[data-uid]:checked');
    const uids = Array.from(checked).map((c) => c.getAttribute('data-uid'));
    if (!uids.length) {
        pushToast(t('selectAtLeastOne') || 'Select at least one', 'error');
        return;
    }
    const ok = await showConfirm(t('deleteConfirm') || 'Delete selected?');
    if (!ok)
        return;
    deleting.value = true;
    try {
        await deleteNovels(uids);
        await load();
        pushToast(t('deleteSuccess') || 'Deleted', 'success');
    }
    finally {
        deleting.value = false;
    }
}
function openNovel(uid) {
    router.push({ name: 'novel-editor', params: { uid } });
}
const __VLS_ctx = {
    ...{},
    ...{},
};
let __VLS_components;
let __VLS_intrinsics;
let __VLS_directives;
__VLS_asFunctionalElement1(__VLS_intrinsics.div, __VLS_intrinsics.div)({});
__VLS_asFunctionalElement1(__VLS_intrinsics.div, __VLS_intrinsics.div)({
    ...{ style: {} },
});
__VLS_asFunctionalElement1(__VLS_intrinsics.button, __VLS_intrinsics.button)({
    ...{ onClick: (__VLS_ctx.onDeleteSelected) },
    ...{ class: "btn-ghost" },
    disabled: (__VLS_ctx.loading || __VLS_ctx.deleting),
});
/** @type {__VLS_StyleScopedClasses['btn-ghost']} */ ;
(__VLS_ctx.t('deleteSelected'));
if (__VLS_ctx.loading) {
    __VLS_asFunctionalElement1(__VLS_intrinsics.span, __VLS_intrinsics.span)({
        ...{ class: "muted" },
    });
    /** @type {__VLS_StyleScopedClasses['muted']} */ ;
    (__VLS_ctx.t('loading'));
}
if (__VLS_ctx.deleting) {
    __VLS_asFunctionalElement1(__VLS_intrinsics.span, __VLS_intrinsics.span)({
        ...{ style: {} },
    });
    (__VLS_ctx.t('deleting'));
}
__VLS_asFunctionalElement1(__VLS_intrinsics.div, __VLS_intrinsics.div)({
    ...{ style: {} },
});
__VLS_asFunctionalElement1(__VLS_intrinsics.div, __VLS_intrinsics.div)({
    ...{ class: "muted" },
});
/** @type {__VLS_StyleScopedClasses['muted']} */ ;
(__VLS_ctx.page);
(__VLS_ctx.totalPages());
__VLS_asFunctionalElement1(__VLS_intrinsics.button, __VLS_intrinsics.button)({
    ...{ onClick: (...[$event]) => {
            __VLS_ctx.changePage(__VLS_ctx.page - 1);
            // @ts-ignore
            [onDeleteSelected, loading, loading, deleting, deleting, t, t, t, page, page, totalPages, changePage,];
        } },
    ...{ class: "btn-ghost" },
    disabled: (__VLS_ctx.page <= 1),
});
/** @type {__VLS_StyleScopedClasses['btn-ghost']} */ ;
__VLS_asFunctionalElement1(__VLS_intrinsics.button, __VLS_intrinsics.button)({
    ...{ onClick: (...[$event]) => {
            __VLS_ctx.changePage(__VLS_ctx.page + 1);
            // @ts-ignore
            [page, page, changePage,];
        } },
    ...{ class: "btn-ghost" },
    disabled: (__VLS_ctx.page >= __VLS_ctx.totalPages()),
});
/** @type {__VLS_StyleScopedClasses['btn-ghost']} */ ;
__VLS_asFunctionalElement1(__VLS_intrinsics.input)({
    ...{ onChange: (...[$event]) => {
            __VLS_ctx.changePage(Number($event.target.value));
            // @ts-ignore
            [page, totalPages, changePage,];
        } },
    ...{ onKeydown: (...[$event]) => {
            __VLS_ctx.changePage(Number($event.target.value));
            // @ts-ignore
            [changePage,];
        } },
    type: "number",
    ...{ style: {} },
    value: (__VLS_ctx.page),
});
__VLS_asFunctionalElement1(__VLS_intrinsics.div, __VLS_intrinsics.div)({
    ...{ class: "card-list" },
});
/** @type {__VLS_StyleScopedClasses['card-list']} */ ;
__VLS_asFunctionalElement1(__VLS_intrinsics.div, __VLS_intrinsics.div)({
    ...{ onClick: (__VLS_ctx.onCreate) },
    ...{ class: "asset-card" },
    ...{ style: {} },
});
/** @type {__VLS_StyleScopedClasses['asset-card']} */ ;
(__VLS_ctx.t('createPlaceholder'));
for (const [n] of __VLS_vFor((__VLS_ctx.novels))) {
    __VLS_asFunctionalElement1(__VLS_intrinsics.div, __VLS_intrinsics.div)({
        key: (n.uid),
        ...{ class: "asset-card" },
    });
    /** @type {__VLS_StyleScopedClasses['asset-card']} */ ;
    __VLS_asFunctionalElement1(__VLS_intrinsics.div, __VLS_intrinsics.div)({
        ...{ style: {} },
    });
    __VLS_asFunctionalElement1(__VLS_intrinsics.div, __VLS_intrinsics.div)({});
    __VLS_asFunctionalElement1(__VLS_intrinsics.input)({
        type: "checkbox",
        'data-uid': (n.uid),
    });
    __VLS_asFunctionalElement1(__VLS_intrinsics.div, __VLS_intrinsics.div)({
        ...{ onClick: (...[$event]) => {
                __VLS_ctx.openNovel(n.uid);
                // @ts-ignore
                [t, page, onCreate, novels, openNovel,];
            } },
        ...{ style: {} },
    });
    __VLS_asFunctionalElement1(__VLS_intrinsics.div, __VLS_intrinsics.div)({
        ...{ style: {} },
    });
    (n.title);
    __VLS_asFunctionalElement1(__VLS_intrinsics.div, __VLS_intrinsics.div)({
        ...{ class: "muted" },
    });
    /** @type {__VLS_StyleScopedClasses['muted']} */ ;
    (n.updated_at || n.created_at);
    // @ts-ignore
    [];
}
const __VLS_0 = ConfirmModal;
// @ts-ignore
const __VLS_1 = __VLS_asFunctionalComponent1(__VLS_0, new __VLS_0({}));
const __VLS_2 = __VLS_1({}, ...__VLS_functionalComponentArgsRest(__VLS_1));
const __VLS_5 = Toast;
// @ts-ignore
const __VLS_6 = __VLS_asFunctionalComponent1(__VLS_5, new __VLS_5({}));
const __VLS_7 = __VLS_6({}, ...__VLS_functionalComponentArgsRest(__VLS_6));
// @ts-ignore
[];
const __VLS_export = (await import('vue')).defineComponent({});
export default {};
//# sourceMappingURL=NovelList.vue.js.map