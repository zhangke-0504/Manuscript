import { ref, onMounted, watch } from 'vue';
import { getModelConfig, updateModelConfig } from '../api';
import useI18n from '../i18n';
import { pushToast } from '../utils/toast';
const { t } = useI18n();
const provider = ref('deepseek');
const apiKey = ref('');
async function load() {
    const res = await getModelConfig(provider.value);
    apiKey.value = res?.data?.config?.api_key || '';
}
onMounted(load);
// reload API key when provider selection changes
watch(provider, () => load());
async function save() {
    await updateModelConfig(provider.value, { api_key: apiKey.value });
    pushToast(t('saved') || 'Saved', 'success');
}
const __VLS_ctx = {
    ...{},
    ...{},
};
let __VLS_components;
let __VLS_intrinsics;
let __VLS_directives;
/** @type {__VLS_StyleScopedClasses['form-input']} */ ;
/** @type {__VLS_StyleScopedClasses['form-input']} */ ;
/** @type {__VLS_StyleScopedClasses['form-input']} */ ;
__VLS_asFunctionalElement1(__VLS_intrinsics.div, __VLS_intrinsics.div)({});
__VLS_asFunctionalElement1(__VLS_intrinsics.h3, __VLS_intrinsics.h3)({});
__VLS_asFunctionalElement1(__VLS_intrinsics.div, __VLS_intrinsics.div)({
    ...{ class: "card" },
    ...{ style: {} },
});
/** @type {__VLS_StyleScopedClasses['card']} */ ;
__VLS_asFunctionalElement1(__VLS_intrinsics.div, __VLS_intrinsics.div)({
    ...{ class: "form-row" },
});
/** @type {__VLS_StyleScopedClasses['form-row']} */ ;
__VLS_asFunctionalElement1(__VLS_intrinsics.label, __VLS_intrinsics.label)({
    ...{ class: "form-label" },
});
/** @type {__VLS_StyleScopedClasses['form-label']} */ ;
__VLS_asFunctionalElement1(__VLS_intrinsics.select, __VLS_intrinsics.select)({
    value: (__VLS_ctx.provider),
    ...{ class: "form-input" },
});
/** @type {__VLS_StyleScopedClasses['form-input']} */ ;
__VLS_asFunctionalElement1(__VLS_intrinsics.option, __VLS_intrinsics.option)({
    value: "deepseek",
});
__VLS_asFunctionalElement1(__VLS_intrinsics.option, __VLS_intrinsics.option)({
    value: "openai",
});
__VLS_asFunctionalElement1(__VLS_intrinsics.div, __VLS_intrinsics.div)({
    ...{ class: "form-row" },
    ...{ style: {} },
});
/** @type {__VLS_StyleScopedClasses['form-row']} */ ;
__VLS_asFunctionalElement1(__VLS_intrinsics.label, __VLS_intrinsics.label)({
    ...{ class: "form-label" },
});
/** @type {__VLS_StyleScopedClasses['form-label']} */ ;
__VLS_asFunctionalElement1(__VLS_intrinsics.input)({
    ...{ class: "form-input" },
});
(__VLS_ctx.apiKey);
/** @type {__VLS_StyleScopedClasses['form-input']} */ ;
__VLS_asFunctionalElement1(__VLS_intrinsics.div, __VLS_intrinsics.div)({
    ...{ class: "hint" },
    ...{ style: {} },
});
/** @type {__VLS_StyleScopedClasses['hint']} */ ;
__VLS_asFunctionalElement1(__VLS_intrinsics.div, __VLS_intrinsics.div)({
    ...{ style: {} },
});
__VLS_asFunctionalElement1(__VLS_intrinsics.button, __VLS_intrinsics.button)({
    ...{ onClick: (__VLS_ctx.save) },
    ...{ class: "btn-primary" },
});
/** @type {__VLS_StyleScopedClasses['btn-primary']} */ ;
__VLS_asFunctionalElement1(__VLS_intrinsics.button, __VLS_intrinsics.button)({
    ...{ onClick: (() => __VLS_ctx.provider = __VLS_ctx.provider) },
    ...{ class: "btn-ghost" },
});
/** @type {__VLS_StyleScopedClasses['btn-ghost']} */ ;
// @ts-ignore
[provider, provider, provider, apiKey, save,];
const __VLS_export = (await import('vue')).defineComponent({});
export default {};
//# sourceMappingURL=Settings.vue.js.map