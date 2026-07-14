<template>
  <div class="suggested-chips">
    <p class="chips-label">
      <svg class="label-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="10"/>
        <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/>
        <line x1="12" y1="17" x2="12.01" y2="17"/>
      </svg>
      Pertanyaan yang sering ditanyakan:
    </p>
    <div class="chips-container">
      <button
        v-for="(chip, index) in chips"
        :key="index"
        class="chip"
        :style="{ animationDelay: `${index * 0.08}s` }"
        @click="$emit('select', chip.question)"
      >
        <span class="chip-icon" v-html="chip.icon"></span>
        <span class="chip-text">{{ chip.question }}</span>
      </button>
    </div>
  </div>
</template>

<script setup>
defineEmits(['select'])

const chips = [
  {
    icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="9" y1="21" x2="9" y2="9"/></svg>`,
    question: 'Apa saja persyaratan mengambil Tugas Akhir?'
  },
  {
    icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>`,
    question: 'Bagaimana prosedur pengajuan judul TA?'
  },
  {
    icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="8" y1="12" x2="16" y2="12"/></svg>`,
    question: 'Bagaimana tahapan seminar proposal TA?'
  },
  {
    icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>`,
    question: 'Apa saja syarat mengikuti seminar kemajuan?'
  },
  {
    icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>`,
    question: 'Bagaimana alur pendaftaran sidang TA?'
  },
  {
    icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>`,
    question: 'Bagaimana sistematika penulisan laporan TA?'
  }
]
</script>

<style scoped>
.suggested-chips {
  padding: 0;
  text-align: left;
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.chips-label {
  font-size: 0.85rem;
  color: var(--text-secondary);
  margin-bottom: 12px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 6px;
  justify-content: flex-start;
}

.label-icon {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
  color: var(--accent-gold);
}

.chips-container {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 8px;
  width: 100%;
}

.chip {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  background: var(--bg-chat);
  border: 1px solid var(--border-light);
  border-radius: 20px;
  cursor: pointer;
  font-size: 0.85rem;
  color: var(--text-primary);
  font-family: 'Inter', sans-serif;
  transition: all var(--transition);
  box-shadow: var(--shadow-sm);
  opacity: 0;
  animation: chipFadeIn 0.4s ease forwards;
  width: fit-content;
  text-align: left;
}

.chip:hover {
  background: var(--primary-navy);
  color: var(--text-white);
  border-color: var(--primary-navy);
  transform: translateX(4px);
  box-shadow: var(--shadow-md);
}

.chip:hover .chip-icon {
  color: var(--accent-gold-light);
}

.chip-icon {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color var(--transition);
  color: var(--text-secondary);
}

.chip-icon :deep(svg) {
  width: 18px;
  height: 18px;
}

.chip-text {
  font-weight: 500;
}

@keyframes chipFadeIn {
  from {
    opacity: 0;
    transform: translateX(-8px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}
</style>