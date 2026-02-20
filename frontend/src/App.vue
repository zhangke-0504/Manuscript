<script setup lang="ts">
import { useRouter } from 'vue-router'
import useI18n from './i18n'
const { t, locale, setLocale } = useI18n()
</script>

<template>
  <div id="app">
    <header style="display:flex;align-items:center;gap:12px;padding:12px;border-bottom:1px solid #eee">
      <h2 style="margin:0">Manuscript</h2>
      <nav style="margin-left:12px">
        <router-link to="/" style="margin-right:8px">{{ t('assets') }}</router-link>
        <router-link to="/settings">{{ t('settings') }}</router-link>
      </nav>
      <div style="margin-left:auto">
        <select v-model="locale">
          <option value="zh">中文</option>
          <option value="en">English</option>
        </select>
      </div>
    </header>

    <main style="padding:12px">
      <router-view />
    </main>
  </div>
</template>

<style>
body {
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial;
}
</style>
