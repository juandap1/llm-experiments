<template>
  <div class="lesson-progression">
    <div class="header">
      <div class="title">Lesson Plan</div>
      <div class="subtitle">Introduction to LLMs</div>
    </div>

    <div class="steps-container">
      <div
        v-for="(step, index) in steps"
        :key="index"
        class="step-item"
        :class="{ active: currentStep === step.id, completed: currentStep > step.id }"
        @click="$emit('change-step', step.id)"
      >
        <div class="step-icon">
          <q-icon :name="step.icon" size="xs" />
        </div>
        <div class="step-content">
          <div class="step-title">{{ step.title }}</div>
          <div class="step-desc">{{ step.description }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'LessonProgression',
  props: {
    currentStep: {
      type: Number,
      default: 1,
    },
  },
  setup() {
    const steps = [
      { id: 1, title: 'Introduction', description: 'Basics of LLMs', icon: 'fas fa-book-open' },
      {
        id: 2,
        title: 'Key Concepts',
        description: 'Tokens, Context Window',
        icon: 'fas fa-lightbulb',
      },
      {
        id: 3,
        title: 'Understanding Check',
        description: 'Quick Quiz',
        icon: 'fas fa-question-circle',
      },
      { id: 4, title: 'Review', description: 'Address Gaps', icon: 'fas fa-sync-alt' },
    ]

    return {
      steps,
    }
  },
})
</script>

<style scoped>
.lesson-progression {
  height: 100%;
  background-color: #1e1e1e;
  border-right: 1px solid #333;
  display: flex;
  flex-direction: column;
  color: #e0e0e0;
}

.header {
  padding: 20px;
  border-bottom: 1px solid #333;
}

.title {
  font-size: 12px;
  text-transform: uppercase;
  color: #888;
  letter-spacing: 1px;
  margin-bottom: 5px;
}

.subtitle {
  font-size: 18px;
  font-weight: 600;
}

.steps-container {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
}

.step-item {
  display: flex;
  padding: 15px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-bottom: 5px;
  border: 1px solid transparent;
}

.step-item:hover {
  background-color: #2a2a2a;
}

.step-item.active {
  background-color: #2a2a2a;
  border-color: #4caf50;
}

.step-item.completed .step-icon {
  color: #4caf50;
}

.step-icon {
  width: 30px;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding-top: 2px;
  color: #666;
}

.step-content {
  flex: 1;
}

.step-title {
  font-weight: 500;
  margin-bottom: 2px;
}

.step-desc {
  font-size: 12px;
  color: #888;
}
</style>
