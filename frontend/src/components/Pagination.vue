<template>
  <div class="pagination" v-if="pageCount>1">
    <button class="btn-ghost" @click="go(page-1)" :disabled="page<=1">‹</button>
    <button v-for="p in pagesToShow" :key="p" :class="['btn-ghost', { active: p===page }]" @click="go(p)">{{ p }}</button>
    <button class="btn-ghost" @click="go(page+1)" :disabled="page>=pageCount">›</button>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
const props = defineProps({ page: { type:Number, default:1 }, pageCount: { type:Number, default:1 } })
const emit = defineEmits(['update:page'])

function go(p:number){ if(p<1) p=1; if(p>props.pageCount) p=props.pageCount; emit('update:page', p) }

const pagesToShow = computed(()=>{
  const max = props.pageCount
  const cur = props.page
  const delta = 2
  const start = Math.max(1, cur-delta)
  const end = Math.min(max, cur+delta)
  const arr:number[] = []
  for(let i=start;i<=end;i++) arr.push(i)
  if(start>1){ if(start>2) arr.unshift(-1); arr.unshift(1) }
  if(end<max){ if(end<max-1) arr.push(-1); arr.push(max) }
  return arr
})
</script>

<style scoped>
.pagination{ display:flex;gap:6px;align-items:center }
.btn-ghost{ background:transparent;border:1px solid rgba(255,255,255,0.04);padding:6px 8px;border-radius:6px }
.btn-ghost.active{ background:linear-gradient(90deg,var(--accent),var(--accent-2));color:white;border:none }
.btn-ghost:disabled{ opacity:0.4 }
</style>
