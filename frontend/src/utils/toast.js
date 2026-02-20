const listeners = [];
export function onPush(fn) { listeners.push(fn); }
export function pushToast(message, type = 'info') {
    listeners.forEach(l => l({ message, type }));
}
//# sourceMappingURL=toast.js.map