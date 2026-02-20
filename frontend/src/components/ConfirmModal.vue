<template>
  <div v-if="confirmVisible" class="confirm-overlay">
    <div class="confirm-box card">
      <div style="margin-bottom:12px">{{ confirmMessage }}</div>
      <div style="display:flex;justify-content:flex-end;gap:8px">
        <button class="btn-ghost" @click="resolveConfirm(false)">Cancel</button>
        <button class="btn-primary" @click="resolveConfirm(true)">OK</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { confirmVisible, confirmMessage, resolveConfirm } from '../utils/confirm'
</script>

<style scoped>
.confirm-overlay { position:fixed; inset:0; display:flex;align-items:center;justify-content:center; background:rgba(0,0,0,0.35); z-index:1001 }
.confirm-box{ width:360px }
</style>
