import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import { createRouter, createWebHistory } from 'vue-router'
import routes from './router'
// optional UI library (install naive-ui via npm to enable)
import naive from 'naive-ui'

const app = createApp(App)

const router = createRouter({
	history: createWebHistory(),
	routes,
})

app.use(router)
// register naive if available
try { app.use(naive) } catch (e) { /* naive not installed */ }

app.mount('#app')
