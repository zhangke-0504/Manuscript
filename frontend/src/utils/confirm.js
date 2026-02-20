import { ref } from 'vue';
const visible = ref(false);
const message = ref('');
let _resolver = null;
export function showConfirm(msg) {
    message.value = msg;
    visible.value = true;
    return new Promise((resolve) => {
        _resolver = resolve;
    });
}
export function resolveConfirm(v) {
    if (_resolver)
        _resolver(v);
    _resolver = null;
    visible.value = false;
}
export { visible as confirmVisible, message as confirmMessage };
//# sourceMappingURL=confirm.js.map