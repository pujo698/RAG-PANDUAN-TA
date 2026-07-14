<template>
  <div class="app-layout" :class="{ 'sidebar-open': isSidebarOpen }">
    <!-- Mobile Overlay -->
    <div class="sidebar-overlay" @click="isSidebarOpen = false"></div>

    <!-- Sidebar -->
    <Sidebar
      class="app-sidebar"
      @select-topic="handleSendMessage"
      @clear-chat="handleClearChat"
    />

    <!-- Main Content -->
    <div class="main-content">
      <!-- Header for mobile -->
      <div class="mobile-header">
        <button class="menu-btn" @click="isSidebarOpen = true">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="18" x2="21" y2="18"/></svg>
        </button>
        <span class="mobile-title">Panduan TA</span>
      </div>

      <!-- Chat Area -->
      <ChatArea
        :messages="messages"
        :is-loading="isLoading"
        :has-started="hasStarted"
        @send-message="handleSendMessage"
      />

      <!-- Input Area -->
      <div class="input-area">
        <div class="input-container">
          <input
            v-model="inputText"
            type="text"
            class="chat-input"
            placeholder="Ketik pertanyaan tentang panduan TA..."
            @keydown.enter="handleSendMessage(inputText)"
            :disabled="isLoading"
          />
          <button
            class="send-btn"
            @click="handleSendMessage(inputText)"
            :disabled="!inputText.trim() || isLoading"
            :class="{ loading: isLoading }"
          >
            <span v-if="!isLoading">➤</span>
            <span v-else class="spinner"></span>
          </button>
        </div>
        <p class="input-hint">
          Jawaban dihasilkan berdasarkan Buku Panduan Tugas Akhir resmi.
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useChat } from './composables/useChat.js'
import Sidebar from './components/Sidebar.vue'
import ChatArea from './components/ChatArea.vue'

const { messages, isLoading, hasStarted, sendMessage, clearChat } = useChat()
const inputText = ref('')
const isSidebarOpen = ref(false)

function handleSendMessage(text) {
  const msg = typeof text === 'string' ? text : inputText.value
  if (!msg || !msg.trim() || isLoading.value) return
  inputText.value = ''
  sendMessage(msg.trim())
  isSidebarOpen.value = false
}

function handleClearChat() {
  clearChat()
  inputText.value = ''
  isSidebarOpen.value = false
}
</script>

<style scoped>
.app-layout {
  display: flex;
  height: 100vh;
  width: 100%;
  overflow: hidden;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--bg-chat);
  min-width: 0;
}

/* Responsive Sidebar */
.sidebar-overlay {
  display: none;
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 15;
}

.mobile-header {
  display: none;
  align-items: center;
  padding: 12px 20px;
  background: var(--bg-chat);
  border-bottom: 1px solid var(--border-light);
  gap: 12px;
}

.menu-btn {
  background: transparent;
  border: none;
  cursor: pointer;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  padding: 4px;
}

.mobile-title {
  font-weight: 600;
  color: var(--primary-navy);
}

@media (max-width: 768px) {
  .app-sidebar {
    position: fixed;
    top: 0;
    bottom: 0;
    left: 0;
    transform: translateX(-100%);
    transition: transform 0.3s ease;
    z-index: 20;
  }

  .sidebar-open .app-sidebar {
    transform: translateX(0);
  }

  .sidebar-open .sidebar-overlay {
    display: block;
  }

  .mobile-header {
    display: flex;
  }
}

/* Input Area */
.input-area {
  padding: 16px 20px;
  background: var(--bg-chat);
  border-top: 1px solid var(--border-light);
}

.input-container {
  max-width: 800px;
  margin: 0 auto;
  display: flex;
  gap: 10px;
  background: var(--bg-input);
  border-radius: var(--radius-xl);
  padding: 6px;
  border: 1px solid var(--border-light);
  box-shadow: var(--shadow-sm);
  transition: all var(--transition);
}

.input-container:focus-within {
  border-color: var(--primary-navy);
  box-shadow: 0 0 0 3px rgba(27, 58, 92, 0.1);
}

.chat-input {
  flex: 1;
  border: none;
  background: transparent;
  padding: 10px 16px;
  font-size: 0.9rem;
  font-family: 'Inter', sans-serif;
  color: var(--text-primary);
  outline: none;
}

.chat-input::placeholder {
  color: var(--text-light);
}

.chat-input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.send-btn {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  background: var(--primary-navy);
  border: none;
  color: white;
  font-size: 1rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition);
  flex-shrink: 0;
}

.send-btn:hover:not(:disabled) {
  background: var(--primary-navy-light);
  transform: scale(1.05);
  box-shadow: var(--shadow-md);
}

.send-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.send-btn.loading {
  background: var(--accent-gold);
  animation: btnPulse 1.5s ease-in-out infinite;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

.input-hint {
  text-align: center;
  font-size: 0.68rem;
  color: var(--text-light);
  margin-top: 8px;
  max-width: 800px;
  margin-left: auto;
  margin-right: auto;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@keyframes btnPulse {
  0%, 100% {
    box-shadow: 0 0 0 0 rgba(196, 155, 44, 0.4);
  }
  50% {
    box-shadow: 0 0 0 8px rgba(196, 155, 44, 0);
  }
}
</style>