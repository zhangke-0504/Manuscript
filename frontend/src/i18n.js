import { reactive, computed } from 'vue';
const messages = {
    zh: {
        saving: '保存中...',
        createPlaceholder: '创建资产',
        createSuccess: '创建成功',
        deleteSuccess: '删除成功',
        updateSuccess: '更新成功',
        selectChapterPrompt: '请选择左侧章节进入编辑',
        assets: '资产',
        settings: '设置',
        createNovel: '创建小说',
        deleteSelected: '删除选中',
        loading: '加载中...',
        deleting: '删除中...',
        deleteConfirm: '确定要删除选中项吗？',
        selectAtLeastOne: '请至少选择一项',
        aiGenerate: 'AI 生成',
        save: '保存',
        saved: '已保存',
        return: '返回',
        chapters: '章节',
        characters: '角色',
        createSession: '新会话',
        aiDefaultPrompt: '请用中文生成该章节的正文，风格偏写实，长度目标约1500-2000字。',
        editorPlaceholder: '在此编辑章节正文（支持中/英），保存请使用 Ctrl+S',
    },
    en: {
        saving: 'Saving...',
        createPlaceholder: 'Create Asset',
        createSuccess: 'Created',
        deleteSuccess: 'Deleted',
        updateSuccess: 'Updated',
        selectChapterPrompt: 'Please select a chapter on the left to edit',
        assets: 'Assets',
        settings: 'Settings',
        createNovel: 'Create Novel',
        deleteSelected: 'Delete Selected',
        loading: 'Loading...',
        deleting: 'Deleting...',
        deleteConfirm: 'Delete selected items?',
        selectAtLeastOne: 'Select at least one',
        aiGenerate: 'AI Generate',
        save: 'Save',
        saved: 'Saved',
        return: 'Return',
        chapters: 'Chapters',
        characters: 'Characters',
        createSession: 'New Session',
        aiDefaultPrompt: 'Please generate the chapter body in English (realistic style), target length ~1500-2000 words.',
        editorPlaceholder: 'Write chapter content here (supports EN/CN). Save with Ctrl+S',
    }
};
const state = reactive({ locale: 'zh' });
export function setLocale(l) { state.locale = l; }
export function useI18n() {
    const locale = computed({
        get: () => state.locale,
        set: (v) => { state.locale = v; }
    });
    function t(key) {
        return messages[state.locale]?.[key] ?? messages['en']?.[key] ?? key;
    }
    return { t, locale, setLocale };
}
export default useI18n;
//# sourceMappingURL=i18n.js.map