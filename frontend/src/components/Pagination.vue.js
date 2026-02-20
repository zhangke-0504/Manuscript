import { computed } from 'vue';
const props = defineProps({ page: { type: Number, default: 1 }, pageCount: { type: Number, default: 1 } });
const emit = defineEmits(['update:page']);
function go(p) { if (p < 1)
    p = 1; if (p > props.pageCount)
    p = props.pageCount; emit('update:page', p); }
const pagesToShow = computed(() => {
    const max = props.pageCount;
    const cur = props.page;
    const delta = 2;
    const start = Math.max(1, cur - delta);
    const end = Math.min(max, cur + delta);
    const arr = [];
    for (let i = start; i <= end; i++)
        arr.push(i);
    if (start > 1) {
        if (start > 2)
            arr.unshift(-1);
        arr.unshift(1);
    }
    if (end < max) {
        if (end < max - 1)
            arr.push(-1);
        arr.push(max);
    }
    return arr;
});
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
/** @type {__VLS_StyleScopedClasses['btn-ghost']} */ ;
/** @type {__VLS_StyleScopedClasses['btn-ghost']} */ ;
if (__VLS_ctx.pageCount > 1) {
    __VLS_asFunctionalElement1(__VLS_intrinsics.div, __VLS_intrinsics.div)({
        ...{ class: "pagination" },
    });
    /** @type {__VLS_StyleScopedClasses['pagination']} */ ;
    __VLS_asFunctionalElement1(__VLS_intrinsics.button, __VLS_intrinsics.button)({
        ...{ onClick: (...[$event]) => {
                if (!(__VLS_ctx.pageCount > 1))
                    return;
                __VLS_ctx.go(__VLS_ctx.page - 1);
                // @ts-ignore
                [pageCount, go, page,];
            } },
        ...{ class: "btn-ghost" },
        disabled: (__VLS_ctx.page <= 1),
    });
    /** @type {__VLS_StyleScopedClasses['btn-ghost']} */ ;
    for (const [p] of __VLS_vFor((__VLS_ctx.pagesToShow))) {
        __VLS_asFunctionalElement1(__VLS_intrinsics.button, __VLS_intrinsics.button)({
            ...{ onClick: (...[$event]) => {
                    if (!(__VLS_ctx.pageCount > 1))
                        return;
                    __VLS_ctx.go(p);
                    // @ts-ignore
                    [go, page, pagesToShow,];
                } },
            key: (p),
            ...{ class: (['btn-ghost', { active: p === __VLS_ctx.page }]) },
        });
        /** @type {__VLS_StyleScopedClasses['active']} */ ;
        /** @type {__VLS_StyleScopedClasses['btn-ghost']} */ ;
        (p);
        // @ts-ignore
        [page,];
    }
    __VLS_asFunctionalElement1(__VLS_intrinsics.button, __VLS_intrinsics.button)({
        ...{ onClick: (...[$event]) => {
                if (!(__VLS_ctx.pageCount > 1))
                    return;
                __VLS_ctx.go(__VLS_ctx.page + 1);
                // @ts-ignore
                [go, page,];
            } },
        ...{ class: "btn-ghost" },
        disabled: (__VLS_ctx.page >= __VLS_ctx.pageCount),
    });
    /** @type {__VLS_StyleScopedClasses['btn-ghost']} */ ;
}
// @ts-ignore
[pageCount, page,];
const __VLS_export = (await import('vue')).defineComponent({
    emits: {},
    props: { page: { type: Number, default: 1 }, pageCount: { type: Number, default: 1 } },
});
export default {};
//# sourceMappingURL=Pagination.vue.js.map