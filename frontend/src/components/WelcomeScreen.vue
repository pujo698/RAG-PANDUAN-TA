<template>
  <div class="welcome-screen">
    <div class="welcome-content">
      <div class="welcome-icon">
        <!-- Book Open Icon -->
        <svg class="icon-main" viewBox="0 0 80 80" fill="none">
          <rect x="10" y="12" width="26" height="56" rx="2" fill="var(--primary-navy)" stroke="var(--primary-navy-dark)" stroke-width="1.5"/>
          <rect x="44" y="12" width="26" height="56" rx="2" fill="var(--primary-navy)" stroke="var(--primary-navy-dark)" stroke-width="1.5"/>
          <path d="M10 20 L36 28 L36 62 L10 54 Z" fill="rgba(255,255,255,0.15)"/>
          <path d="M44 28 L70 20 L70 54 L44 62 Z" fill="rgba(255,255,255,0.15)"/>
          <line x1="36" y1="28" x2="36" y2="62" stroke="var(--accent-gold)" stroke-width="2"/>
          <line x1="44" y1="28" x2="44" y2="62" stroke="var(--accent-gold)" stroke-width="2"/>
          <circle cx="40" cy="24" r="4" fill="var(--accent-gold)"/>
        </svg>
      </div>
      <h1 class="welcome-title">Panduan Tugas Akhir</h1>
      <p class="welcome-subtitle">Teknik Informatika UNISSULA</p>
      <div class="welcome-divider">
        <span class="divider-line"></span>
        <svg class="divider-diamond" width="8" height="8" viewBox="0 0 8 8"><rect x="0.5" y="0.5" width="7" height="7" fill="var(--accent-gold)" transform="rotate(45 4 4)"/></svg>
        <span class="divider-line"></span>
      </div>
      <SuggestedChips @select="$emit('selectQuestion', $event)" />
      <p class="welcome-hint">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><polyline points="19 12 12 19 5 12"/></svg>
        Ketik pertanyaan Anda di bawah ini
      </p>
    </div>
  </div>
</template>

<script setup>
import SuggestedChips from './SuggestedChips.vue'

defineEmits(['selectQuestion'])
</script>

<style scoped>
.welcome-screen {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100%;
  padding: 24px;
  animation: welcomeFadeIn 0.6s ease;
}

.welcome-content {
  text-align: center;
  max-width: 580px;
  width: 100%;
}

.welcome-icon {
  margin-bottom: 20px;
}

.icon-main {
  width: 72px;
  height: 72px;
  display: inline-block;
  animation: iconFloat 3s ease-in-out infinite;
  filter: drop-shadow(0 4px 8px rgba(27, 58, 92, 0.2));
}

.welcome-title {
  font-size: 2rem;
  font-weight: 800;
  color: var(--primary-navy);
  margin-bottom: 4px;
  letter-spacing: -0.5px;
}

.welcome-subtitle {
  font-size: 1rem;
  color: var(--accent-gold);
  font-weight: 600;
  margin-bottom: 20px;
  letter-spacing: 1px;
}

.welcome-divider {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-bottom: 20px;
}

.divider-line {
  width: 40px;
  height: 1px;
  background: var(--border-light);
}

.divider-diamond {
  flex-shrink: 0;
}

.welcome-desc {
  font-size: 0.9rem;
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: 24px;
}

.welcome-desc strong {
  color: var(--primary-navy);
}

.welcome-features {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 28px;
  background: var(--bg-chat);
  border-radius: var(--radius-md);
  padding: 16px 20px;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-light);
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 0.85rem;
  color: var(--text-primary);
  text-align: left;
}

.feature-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.welcome-hint {
  margin-top: 16px;
  font-size: 0.78rem;
  color: var(--text-light);
  animation: hintPulse 2s ease-in-out infinite;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

@keyframes welcomeFadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes iconFloat {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-8px);
  }
}

@keyframes hintPulse {
  0%, 100% {
    opacity: 0.5;
  }
  50% {
    opacity: 1;
  }
}
</style>