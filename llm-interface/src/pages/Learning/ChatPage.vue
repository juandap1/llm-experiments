<template>
  <div class="layout-container">
    <default-navbar />
    <div class="layout-main">
      <default-sidebar />
      <div class="content-container q-pa-md flex column">
        <div class="text-h4 q-mb-md">AI Helper</div>

        <q-scroll-area class="col q-mb-md bg-grey-2 rounded-borders q-pa-sm">
          <div v-for="(msg, idx) in messages" :key="idx" class="q-mb-sm">
            <q-chat-message
              :text="[msg.text]"
              :sent="msg.isUser"
              :bg-color="msg.isUser ? 'primary' : 'white'"
              :text-color="msg.isUser ? 'white' : 'black'"
            />
          </div>
          <div v-if="loading" class="q-ml-md">
            <q-spinner-dots size="2em" />
          </div>
        </q-scroll-area>

        <div class="row q-col-gutter-sm">
          <div class="col">
            <q-input
              outlined
              v-model="input"
              label="Ask for help..."
              @keyup.enter="sendMessage"
              dense
            />
          </div>
          <div class="col-auto">
            <q-btn color="primary" icon="send" @click="sendMessage" round />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent, ref } from 'vue'
import DefaultNavbar from 'src/components/Learning/DefaultNavbar.vue'
import DefaultSidebar from 'src/components/Learning/DefaultSidebar.vue'
// import { llmService } from 'src/services/llm'

export default defineComponent({
  name: 'ChatPage',
  components: { DefaultNavbar, DefaultSidebar },
  setup() {
    const messages = ref([
      { text: 'Hello! I am your learning assistant. How can I help you today?', isUser: false },
    ])
    const input = ref('')
    const loading = ref(false)

    async function sendMessage() {
      if (!input.value.trim()) return

      const userMsg = input.value
      messages.value.push({ text: userMsg, isUser: true })
      input.value = ''
      loading.value = true

      // Mock response
      setTimeout(() => {
        messages.value.push({
          text: `I can help you with that! You asked: "${userMsg}"`,
          isUser: false,
        })
        loading.value = false
      }, 1000)
    }

    return {
      messages,
      input,
      loading,
      sendMessage,
    }
  },
})
</script>

<style scoped>
.content-container {
  height: calc(100vh - 50px); /* Adjust based on navbar height */
}
</style>
