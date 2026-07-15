<template>
  <aside class="sidebar">
    <!-- Header -->
    <div class="sidebar-header">
      <div class="sidebar-logo">
        <!-- Book Icon -->
        <img class="logo-icon" src="/UNISSULA - Utama.png" alt="Logo UNISSULA" />
      </div>
      <h2 class="sidebar-title">Panduan TA</h2>
      <p class="sidebar-subtitle">Teknik Informatika</p>
    </div>

    <!-- Divider -->
    <div class="sidebar-divider">
      <span class="divider-gold"></span>
    </div>

    <!-- Action Buttons -->
    <div class="sidebar-actions">
      <button class="btn-nav" :class="{ active: currentView === 'chat' }" @click="$emit('clearChat'); $emit('changeView', 'chat')">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="1 4 1 10 7 10"/><path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"/></svg>
        <span>Chat Baru</span>
      </button>
      
      <button class="btn-nav mt-2" :class="{ active: currentView === 'dashboard' }" @click="$emit('changeView', 'dashboard')">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="9" y1="21" x2="9" y2="9"/></svg>
        <span>Dashboard Evaluasi</span>
      </button>
    </div>

    <!-- Footer -->
    <div class="sidebar-footer">
      <p class="footer-text">&copy; 2024 Teknik Informatika</p>
      <p class="footer-text">Universitas Islam Sultan Agung</p>
      <p class="footer-rag">Powered by RAG + AI</p>
    </div>
  </aside>
</template>

<script setup>
defineProps({
  currentView: {
    type: String,
    default: 'chat'
  }
})
defineEmits(['selectTopic', 'clearChat', 'changeView'])
</script>

<style scoped>
.sidebar {
  width: 280px;
  min-width: 280px;
  background: linear-gradient(180deg, var(--primary-navy-dark) 0%, var(--primary-navy) 100%);
  color: var(--text-white);
  display: flex;
  flex-direction: column;
  padding: 0;
  height: 100vh;
  box-shadow: var(--shadow-lg);
  position: relative;
  z-index: 10;
}

.sidebar-header {
  padding: 28px 20px 16px;
  text-align: center;
}

.sidebar-logo {
  margin-bottom: 12px;
}

.logo-icon {
  width: 56px;
  height: 56px;
  filter: drop-shadow(0 4px 6px rgba(0, 0, 0, 0.3));
}

.sidebar-title {
  font-size: 1.15rem;
  font-weight: 700;
  color: var(--text-white);
  letter-spacing: 0.5px;
  margin-bottom: 2px;
}

.sidebar-subtitle {
  font-size: 0.75rem;
  color: var(--accent-gold-light);
  font-weight: 500;
  letter-spacing: 1px;
}

.sidebar-divider {
  padding: 0 20px;
  margin: 4px 0;
}

.divider-gold {
  display: block;
  height: 1px;
  background: linear-gradient(
    90deg,
    transparent 0%,
    var(--accent-gold) 30%,
    var(--accent-gold) 70%,
    transparent 100%
  );
  opacity: 0.4;
}

.sidebar-section {
  padding: 16px 16px 8px;
  flex-shrink: 0;
}

.section-title {
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 1.5px;
  color: rgba(255, 255, 255, 0.5);
  margin-bottom: 12px;
  padding-left: 4px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.topic-list {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.topic-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all var(--transition);
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.8);
}

.topic-item:hover {
  background: rgba(255, 255, 255, 0.1);
  color: var(--text-white);
  transform: translateX(4px);
}

.topic-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
  transition: transform var(--transition);
}

.topic-item:hover .topic-icon {
  transform: scale(1.15);
}

.topic-text {
  font-weight: 500;
}

.sidebar-actions {
  padding: 12px 16px;
  margin-top: auto;
}

.btn-nav {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  padding: 10px 16px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: var(--text-white);
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 500;
  font-family: 'Inter', sans-serif;
  transition: all var(--transition);
}

.btn-nav:hover, .btn-nav.active {
  background: var(--accent-gold);
  border-color: var(--accent-gold);
  color: var(--primary-navy-dark);
}

.btn-nav.active {
  box-shadow: 0 4px 12px rgba(196, 155, 44, 0.3);
}

.btn-nav:hover svg, .btn-nav.active svg {
  color: var(--primary-navy-dark);
}

.btn-nav svg {
  width: 16px;
  height: 16px;
}

.mt-2 {
  margin-top: 8px;
}

.sidebar-footer {
  padding: 16px 20px;
  text-align: center;
}

.footer-text {
  font-size: 0.68rem;
  color: rgba(255, 255, 255, 0.5);
  line-height: 1.6;
  margin: 0;
}

.footer-rag {
  font-size: 0.62rem;
  color: rgba(255, 255, 255, 0.3);
  margin-top: 4px;
  letter-spacing: 1px;
}
</style>