import { ref } from 'vue'
import axios from 'axios'

export function useChat() {
  const messages = ref([])
  const isLoading = ref(false)
  const error = ref(null)
  const hasStarted = ref(false)

  const apiClient = axios.create({
    baseURL: '/api',
    timeout: 120000,
    headers: {
      'Content-Type': 'application/json'
    }
  })

  async function sendMessage(question) {
    if (!question.trim() || isLoading.value) return

    hasStarted.value = true

    // Add user message
    messages.value.push({
      role: 'user',
      content: question.trim(),
      timestamp: new Date().toISOString()
    })

    error.value = null
    isLoading.value = true

    try {
      const response = await apiClient.post('/ask', {
        question: question.trim()
      })

      const data = response.data

      // Add bot message with sources
      messages.value.push({
        role: 'bot',
        content: data.answer || 'Maaf, tidak ada jawaban yang tersedia.',
        sources: data.sources || [],
        timestamp: new Date().toISOString()
      })
    } catch (err) {
      error.value = 'Gagal terhubung ke server. Pastikan backend sedang berjalan.'
      messages.value.push({
        role: 'bot',
        content: 'Maaf, terjadi kesalahan saat menghubungi server. Pastikan backend sedang berjalan.',
        sources: [],
        timestamp: new Date().toISOString()
      })
    } finally {
      isLoading.value = false
    }
  }

  function clearChat() {
    messages.value = []
    hasStarted.value = false
    error.value = null
  }

  return {
    messages,
    isLoading,
    error,
    hasStarted,
    sendMessage,
    clearChat
  }
}