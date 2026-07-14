<template>
  <div class="chat-area" ref="chatContainer">
    <!-- Welcome Screen -->
    <WelcomeScreen
      v-if="!hasStarted"
      @select-question="$emit('sendMessage', $event)"
    />

    <!-- Chat Messages -->
    <div v-else class="chat-messages">
      <TransitionGroup name="message">
        <div
          v-for="(msg, index) in messages"
          :key="index"
          class="message-wrapper"
          :class="msg.role"
        >


          <!-- Message Bubble -->
          <div class="message-bubble" :class="msg.role">

            <div
              class="message-content"
              v-html="renderMarkdown(msg.content)"
            ></div>
            <div class="message-actions" v-if="msg.role === 'bot'">
              <button
                class="copy-btn"
                @click="copyText(msg.content)"
                title="Salin jawaban"
              >
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
              </button>
            </div>

            <!-- Source Documents -->
            <SourceDoc v-if="msg.role === 'bot'" :sources="msg.sources" />
          </div>


        </div>
      </TransitionGroup>

      <!-- Typing Indicator -->
      <div v-if="isLoading" class="message-wrapper bot">

        <div class="message-bubble bot typing-bubble">
          <div class="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'
import { marked } from 'marked'
import WelcomeScreen from './WelcomeScreen.vue'
import SourceDoc from './SourceDoc.vue'

const props = defineProps({
  messages: { type: Array, default: () => [] },
  isLoading: { type: Boolean, default: false },
  hasStarted: { type: Boolean, default: false }
})

defineEmits(['sendMessage'])

const chatContainer = ref(null)

// Auto scroll to bottom on new messages
watch(
  () => props.messages.length,
  async () => {
    await nextTick()
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight
    }
  }
)

watch(
  () => props.isLoading,
  async (loading) => {
    if (loading) {
      await nextTick()
      if (chatContainer.value) {
        chatContainer.value.scrollTop = chatContainer.value.scrollHeight
      }
    }
  }
)

function renderMarkdown(text) {
  if (!text) return ''
  marked.setOptions({ breaks: true, gfm: true })
  return marked.parse(text)
}

function formatTime(timestamp) {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return date.toLocaleTimeString('id-ID', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

function copyText(text) {
  navigator.clipboard.writeText(text).catch(() => {})
}
</script>

<style scoped>
.chat-area {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: var(--bg-chat);
  scroll-behavior: smooth;
}

.chat-messages {
  max-width: 800px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.message-wrapper {
  display: flex;
  gap: 10px;
  margin-bottom: 16px;
  align-items: flex-start;
}

.message-wrapper.user {
  flex-direction: row-reverse;
}

.avatar {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: var(--shadow-sm);
}

.bot-avatar {
  background: linear-gradient(135deg, var(--primary-navy-light), var(--primary-navy));
}

.user-avatar {
  background: linear-gradient(135deg, var(--accent-gold-light), var(--accent-gold));
}

.message-bubble {
  max-width: 72%;
  padding: 14px 18px;
  border-radius: var(--radius-lg);
  position: relative;
  box-shadow: var(--shadow-sm);
}

.message-bubble.bot {
  background: transparent;
  border: none;
  box-shadow: none;
  padding: 8px 0;
}

.message-bubble.user {
  background: #2C2C2C;
  color: var(--text-white);
  border-radius: 24px;
  box-shadow: none;
  padding: 12px 20px;
}



.message-content {
  font-size: 0.9rem;
  line-height: 1.65;
}

.message-content :deep(p) {
  margin: 0 0 8px 0;
}

.message-content :deep(p:last-child) {
  margin-bottom: 0;
}

.message-content :deep(ul),
.message-content :deep(ol) {
  margin: 8px 0;
  padding-left: 20px;
}

.message-content :deep(li) {
  margin-bottom: 4px;
}

.message-content :deep(strong) {
  font-weight: 600;
}

.message-content :deep(code) {
  background: rgba(0, 0, 0, 0.06);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.85em;
}

.message-content :deep(pre) {
  background: #1A2332;
  color: #E2E8F0;
  padding: 12px 16px;
  border-radius: var(--radius-sm);
  overflow-x: auto;
  margin: 8px 0;
}

.message-content :deep(pre code) {
  background: transparent;
  padding: 0;
  color: inherit;
}

.message-actions {
  display: flex;
  align-items: center;
  margin-top: 8px;
}

.copy-btn {
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 2px;
  opacity: 0.5;
  transition: opacity var(--transition);
  display: flex;
  align-items: center;
}

.copy-btn:hover {
  opacity: 1;
}

/* Typing Indicator */
.typing-bubble {
  min-width: 70px;
}

.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 4px 0;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--text-light);
  animation: typingBounce 1.4s ease-in-out infinite;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

/* Message Transition */
.message-enter-active {
  transition: all 0.4s ease;
}

.message-leave-active {
  transition: all 0.2s ease;
}

.message-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.message-leave-to {
  opacity: 0;
  transform: translateX(-10px);
}

@keyframes typingBounce {
  0%, 60%, 100% {
    transform: translateY(0);
    opacity: 0.4;
  }
  30% {
    transform: translateY(-8px);
    opacity: 1;
  }
}
</style>