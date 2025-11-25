<template>
  <div class="quiz-content">
    <div class="quiz-header">
      <div class="quiz-badge">Understanding Check</div>
      <h2>Module 1 Quiz</h2>
    </div>

    <div class="question-card">
      <div class="question-number">Question 1 of 3</div>
      <div class="question-text">
        Which of the following best describes a "token" in the context of LLMs?
      </div>

      <div class="options-list">
        <div
          v-for="(option, index) in options"
          :key="index"
          class="option-item"
          :class="{ selected: selectedOption === index }"
          @click="selectedOption = index"
        >
          <div class="option-marker">{{ String.fromCharCode(65 + index) }}</div>
          <div class="option-text">{{ option }}</div>
          <q-icon v-if="selectedOption === index" name="check_circle" color="positive" />
        </div>
      </div>

      <div class="actions">
        <q-btn flat label="Skip" color="grey" />
        <q-btn
          unelevated
          label="Submit Answer"
          color="primary"
          :disable="selectedOption === null"
        />
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent, ref } from 'vue'

export default defineComponent({
  name: 'QuizContent',
  setup() {
    const selectedOption = ref(null)
    const options = [
      'A physical coin used to pay for API usage',
      'A basic unit of text (word, character, or part of word)',
      'A secure password for authentication',
      'The entire prompt sent to the model',
    ]

    return {
      selectedOption,
      options,
    }
  },
})
</script>

<style scoped>
.quiz-content {
  max-width: 700px;
  margin: 0 auto;
  color: #e0e0e0;
  padding-top: 40px;
}

.quiz-header {
  text-align: center;
  margin-bottom: 40px;
}

.quiz-badge {
  display: inline-block;
  background-color: #333;
  color: #aaa;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 10px;
}

h2 {
  font-size: 28px;
  font-weight: 700;
  margin: 0;
}

.question-card {
  background-color: #1e1e1e;
  border: 1px solid #333;
  border-radius: 16px;
  padding: 40px;
}

.question-number {
  color: #4caf50;
  font-weight: 600;
  margin-bottom: 15px;
}

.question-text {
  font-size: 20px;
  font-weight: 500;
  margin-bottom: 30px;
  line-height: 1.4;
}

.options-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 30px;
}

.option-item {
  display: flex;
  align-items: center;
  padding: 15px 20px;
  background-color: #2a2a2a;
  border: 2px solid transparent;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.option-item:hover {
  background-color: #333;
}

.option-item.selected {
  background-color: rgba(76, 175, 80, 0.1);
  border-color: #4caf50;
}

.option-marker {
  width: 30px;
  height: 30px;
  background-color: #444;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
  font-weight: 600;
  font-size: 14px;
}

.selected .option-marker {
  background-color: #4caf50;
  color: white;
}

.option-text {
  flex: 1;
  font-size: 16px;
}

.actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 20px;
  border-top: 1px solid #333;
}
</style>
