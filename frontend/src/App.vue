<script setup lang="ts">
import { useRouter } from 'vue-router'
import useI18n from './i18n'
const { t, locale, setLocale } = useI18n()
</script>

<template>
  <div id="app">
    <header class="header">
      <div class="logo">Manuscript</div>
      <nav style="margin-left:12px">
        <router-link to="/" class="navlink">{{ t('assets') }}</router-link>
        <router-link to="/settings" class="navlink">{{ t('settings') }}</router-link>
      </nav>
      <div style="margin-left:auto;display:flex;align-items:center;gap:8px">
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
