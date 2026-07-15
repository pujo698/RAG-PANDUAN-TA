<template>
  <div v-if="sources && sources.length > 0" class="source-doc">
    <button class="source-toggle" @click="isOpen = !isOpen">
      <svg class="source-toggle-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>
      <span>Sumber Dokumen ({{ sources.length }})</span>
      <svg class="source-chevron" :class="{ open: isOpen }" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg>
    </button>
    <Transition name="source">
      <div v-show="isOpen" class="source-list">
        <div
          v-for="(source, index) in sources"
          :key="index"
          class="source-item"
        >
          <div class="source-header" @click="toggleItem(index)">
            <span class="source-page">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
              <template v-if="source.chapter">
                {{ source.chapter }}
                <template v-if="source.section && source.section !== 'undefined'"> - {{ source.section }}</template>
                (Hal. {{ source.page || '?' }})
              </template>
              <template v-else>
                Halaman {{ source.page || '?' }}
              </template>
            </span>
            <div class="header-right">
              <span class="source-relevance">
                {{ Math.round((source.score || 0.0) * 100) }}% relevan
              </span>
              <svg class="item-chevron" :class="{ open: expandedIndex === index }" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg>
            </div>
          </div>
          <div v-show="expandedIndex === index" class="source-body">
            <p class="source-content">{{ source.content }}</p>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref } from 'vue'

defineProps({
  sources: {
    type: Array,
    default: () => []
  }
})

const isOpen = ref(false)
const expandedIndex = ref(null)

const toggleItem = (index) => {
  expandedIndex.value = expandedIndex.value === index ? null : index
}
</script>

<style scoped>
.source-doc {
  margin-top: 12px;
}

.source-toggle {
  display: flex;
  align-items: center;
  gap: 6px;
  background: transparent;
  border: 1px solid var(--border-light);
  border-radius: var(--radius-sm);
  padding: 8px 14px;
  font-size: 0.8rem;
  color: var(--text-secondary);
  cursor: pointer;
  font-family: 'Inter', sans-serif;
  transition: all var(--transition);
  width: 100%;
}

.source-toggle:hover {
  background: var(--bg-input);
  color: var(--text-primary);
}

.source-toggle-icon {
  flex-shrink: 0;
}

.source-chevron {
  margin-left: auto;
  transition: transform 0.3s ease;
}

.source-chevron.open {
  transform: rotate(180deg);
}

.source-list {
  margin-top: 8px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.source-item {
  background: #F8FAFC;
  border: 1px solid var(--border-light);
  border-radius: var(--radius-sm);
  padding: 12px 14px;
  border-left: 3px solid var(--accent-gold);
}

.source-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  user-select: none;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.item-chevron {
  color: var(--text-light);
  transition: transform 0.3s ease;
}

.item-chevron.open {
  transform: rotate(180deg);
}

.source-body {
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px dashed var(--border-light);
}

.source-meta {
  margin-bottom: 8px;
  display: flex;
}

.source-page {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--primary-navy);
  display: flex;
  align-items: center;
  gap: 4px;
}

.source-page svg {
  flex-shrink: 0;
}

.source-relevance {
  font-size: 0.7rem;
  color: var(--text-light);
  background: var(--bg-input);
  padding: 2px 8px;
  border-radius: 10px;
}

.source-content {
  font-size: 0.78rem;
  color: var(--text-secondary);
  line-height: 1.5;
  white-space: pre-wrap;
}

.source-enter-active,
.source-leave-active {
  transition: all 0.3s ease;
  overflow: hidden;
}

.source-enter-from,
.source-leave-to {
  opacity: 0;
  max-height: 0;
  margin-top: 0;
}

.source-enter-to,
.source-leave-from {
  opacity: 1;
  max-height: 500px;
}
</style>