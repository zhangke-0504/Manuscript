import NovelList from '../pages/NovelList.vue';
import NovelEditor from '../pages/NovelEditor.vue';
import Settings from '../pages/Settings.vue';
export default [
    { path: '/', name: 'novel-list', component: NovelList },
    { path: '/novel/:uid', name: 'novel-editor', component: NovelEditor, props: true },
    { path: '/settings', name: 'settings', component: Settings },
];
//# sourceMappingURL=index.js.map