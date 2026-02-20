import { reactive, computed } from 'vue'

const messages: Record<string, Record<string, string>> = {
  zh: {
      saving: '保存中...',
      createPlaceholder: '创作小说',
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
  },
  en: {
      saving: 'Saving...',
      createPlaceholder: 'Create Novel',
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
  }
}

const state = reactive({ locale: 'zh' })

export function setLocale(l: string) { state.locale = l }
export function useI18n() {
  const locale = computed({
    get: () => state.locale,
    set: (v: string) => { state.locale = v }
  })
  function t(key: string) {
    return messages[state.locale]?.[key] ?? messages['en']?.[key] ?? key
  }
  return { t, locale, setLocale }
}

export default useI18n
