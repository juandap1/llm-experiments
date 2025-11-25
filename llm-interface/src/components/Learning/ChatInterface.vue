<template>
  <div class="chat-interface">
    <div class="chat-header">
      <div class="header-content">
        <q-icon name="fas fa-robot" class="q-mr-sm" />
        <span>AI Assistant</span>
      </div>
      <q-btn flat round dense icon="close" size="sm" @click="$emit('close')" />
    </div>

    <div class="messages-area">
      <div v-for="(msg, index) in messages" :key="index" class="message-wrapper" :class="msg.role">
        <div class="message-bubble">
          {{ msg.content }}
        </div>
        <div class="message-time">10:{{ 30 + index }} AM</div>
      </div>
    </div>

    <div class="input-area">
      <q-input
        v-model="newMessage"
        dark
        dense
        outlined
        placeholder="Ask a question..."
        @keyup.enter="sendMessage"
      >
        <template v-slot:append>
          <q-btn round dense flat icon="send" @click="sendMessage" />
        </template>
      </q-input>
    </div>
  </div>
</template>

<script>
import { defineComponent, ref } from 'vue'

export default defineComponent({
  name: 'ChatInterface',
  setup() {
    const newMessage = ref('')
    const messages = ref([
      {
        role: 'assistant',
        content:
          'Hello! I am here to help you understand the lesson. Feel free to ask any questions.',
      },
      { role: 'user', content: 'What is a token?' },
      {
        role: 'assistant',
        content:
          'A token is a basic unit of text that an LLM processes. It can be a word, part of a word, or even a character.',
      },
    ])

    const sendMessage = () => {
      if (!newMessage.value.trim()) return

      messages.value.push({
        role: 'user',
        content: newMessage.value,
      })

      // Simulate response
      setTimeout(() => {
        messages.value.push({
          role: 'assistant',
          content: 'That is a great question! Let me explain further...',
        })
      }, 1000)

      newMessage.value = ''
    }

    return {
      newMessage,
      messages,
      sendMessage,
    }
  },
})
</script>

<style scoped>
.chat-interface {
  height: 100%;
  background-color: #1e1e1e;
  border-left: 1px solid #333;
  display: flex;
  flex-direction: column;
  color: #e0e0e0;
}

.chat-header {
  padding: 15px;
  border-bottom: 1px solid #333;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.header-content {
  display: flex;
  align-items: center;
}

.messages-area {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.message-wrapper {
  display: flex;
  flex-direction: column;
  max-width: 85%;
}

.message-wrapper.user {
  align-self: flex-end;
  align-items: flex-end;
}

.message-wrapper.assistant {
  align-self: flex-start;
  align-items: flex-start;
}

.message-bubble {
  padding: 10px 15px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.4;
}

.user .message-bubble {
  background-color: #4caf50;
  color: white;
  border-bottom-right-radius: 2px;
}

.assistant .message-bubble {
  background-color: #333;
  color: #e0e0e0;
  border-bottom-left-radius: 2px;
}

.message-time {
  font-size: 10px;
  color: #666;
  margin-top: 4px;
  padding: 0 4px;
}

.input-area {
  padding: 15px;
  border-top: 1px solid #333;
}
</style>
