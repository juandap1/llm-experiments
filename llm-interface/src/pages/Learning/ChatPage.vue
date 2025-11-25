<template>
  <div class="chat-page-container">
    <!-- Left Sidebar: Lesson Progression -->
    <div class="left-sidebar">
      <lesson-progression :current-step="currentStep" @change-step="handleStepChange" />
    </div>

    <!-- Main Content Area -->
    <div class="main-content">
      <div class="content-scroll-area">
        <transition name="fade" mode="out-in">
          <component :is="currentContentComponent" />
        </transition>
      </div>
    </div>

    <!-- Right Sidebar: Chat Interface -->
    <div class="right-sidebar" :class="{ closed: !isChatOpen }">
      <chat-interface v-if="isChatOpen" @close="isChatOpen = false" />
      <div v-else class="chat-toggle-btn" @click="isChatOpen = true" title="Open Chat">
        <q-icon name="chat" />
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent, ref, computed } from 'vue'
import { useQuasar } from 'quasar'
import LessonProgression from 'src/components/Learning/LessonProgression.vue'
import ChatInterface from 'src/components/Learning/ChatInterface.vue'
import LessonContent from 'src/components/Learning/LessonContent.vue'
import QuizContent from 'src/components/Learning/QuizContent.vue'

export default defineComponent({
  name: 'ChatPage',
  components: { LessonProgression, ChatInterface, LessonContent, QuizContent },
  setup() {
    const $q = useQuasar()
    $q.dark.set(true)
    const currentStep = ref(1)
    const isChatOpen = ref(true)
    const currentContentComponent = computed(() => {
      switch (currentStep.value) {
        case 1:
        case 2:
          return 'LessonContent'
        case 3:
          return 'QuizContent'
        case 4:
          return 'LessonContent' // placeholder for review component
        default:
          return 'LessonContent'
      }
    })
    const handleStepChange = (stepId) => {
      currentStep.value = stepId
    }
    return { currentStep, isChatOpen, currentContentComponent, handleStepChange }
  },
})
</script>

<style scoped>
.chat-page-container {
  display: flex;
  height: 100vh;
  width: 100%;
  background-color: #121212;
  overflow: hidden;
}
.left-sidebar {
  width: 300px;
  min-width: 300px;
  height: 100%;
  transition: all 0.3s ease;
}
.main-content {
  flex: 1;
  height: 100%;
  position: relative;
  background-color: #121212;
}
.content-scroll-area {
  height: 100%;
  overflow-y: auto;
  padding: 40px;
}
.right-sidebar {
  width: 350px;
  min-width: 350px;
  height: 100%;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
}
.right-sidebar.closed {
  width: 60px;
  min-width: 60px;
}
.chat-toggle-btn {
  width: 100%;
  height: 100%;
  border-left: 1px solid #333;
  display: flex;
  justify-content: center;
  padding-top: 20px;
  cursor: pointer;
  color: #888;
  background-color: #1e1e1e;
}
.chat-toggle-btn:hover {
  color: white;
  background-color: #2a2a2a;
}
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
