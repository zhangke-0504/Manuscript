import { reactive } from 'vue';
import { onPush } from '../utils/toast';
const state = reactive({ toasts: [] });
// subscribe to global push events
onPush((m) => {
    const id = Date.now() + Math.random();
    state.toasts.push({ id, message: m.message, type: m.type || 'info' });
    setTimeout(() => { const i = state.toasts.findIndex(t => t.id === id); if (i >= 0)
        state.toasts.splice(i, 1); }, 3500);
});
const toasts = state.toasts;
const __VLS_ctx = {
    ...{},
    ...{},
};
let __VLS_components;
let __VLS_intrinsics;
let __VLS_directives;
/** @type {__VLS_StyleScopedClasses['toast']} */ ;
/** @type {__VLS_StyleScopedClasses['toast']} */ ;
/** @type {__VLS_StyleScopedClasses['toast']} */ ;
if (__VLS_ctx.toasts.length) {
    __VLS_asFunctionalElement1(__VLS_intrinsics.div, __VLS_intrinsics.div)({
        ...{ class: "toast-container" },
    });
    /** @type {__VLS_StyleScopedClasses['toast-container']} */ ;
    for (const [t] of __VLS_vFor((__VLS_ctx.toasts))) {
        __VLS_asFunctionalElement1(__VLS_intrinsics.div, __VLS_intrinsics.div)({
            key: (t.id),
            ...{ class: "toast" },
            ...{ class: (t.type) },
        });
        /** @type {__VLS_StyleScopedClasses['toast']} */ ;
        __VLS_asFunctionalElement1(__VLS_intrinsics.div, __VLS_intrinsics.div)({
            ...{ class: "toast-body" },
        });
        /** @type {__VLS_StyleScopedClasses['toast-body']} */ ;
        (t.message);
        // @ts-ignore
        [toasts, toasts,];
    }
}
// @ts-ignore
[];
const __VLS_export = (await import('vue')).defineComponent({});
export default {};
//# sourceMappingURL=Toast.vue.js.map