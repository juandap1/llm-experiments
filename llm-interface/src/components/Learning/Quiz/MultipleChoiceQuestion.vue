<template>
  <div class="mc-question">
    <div class="question-text">{{ question.question }}</div>
    <div class="options-list">
      <div
        v-for="(option, index) in question.options"
        :key="index"
        class="option-item"
        :class="{ selected: modelValue === index }"
        @click="$emit('update:modelValue', index)"
      >
        <div class="option-marker">{{ getMarker(index) }}</div>
        <div class="option-content">{{ option }}</div>
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'MultipleChoiceQuestion',
  props: {
    question: {
      type: Object,
      required: true,
    },
    modelValue: {
      type: [Number, String],
      default: null,
    },
  },
  emits: ['update:modelValue'],
  setup() {
    function getMarker(index) {
      return String.fromCharCode(65 + index) // A, B, C, D...
    }
    return { getMarker }
  },
})
</script>

<style scoped>
.mc-question {
  display: flex;
  flex-direction: column;
  gap: 20px;
  width: 100%;
}

.question-text {
  font-size: 1.2em;
  font-weight: 500;
  color: #fff;
  margin-bottom: 10px;
}

.options-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.option-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px 20px;
  background-color: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.option-item:hover {
  background-color: rgba(255, 255, 255, 0.1);
  transform: translateX(5px);
}

.option-item.selected {
  background-color: rgba(var(--q-secondary-rgb), 0.15);
  border-color: var(--secondary);
}

.option-marker {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background-color: rgba(255, 255, 255, 0.1);
  font-weight: bold;
  color: #aaa;
  transition: all 0.2s;
}

.option-item.selected .option-marker {
  background-color: var(--secondary);
  color: #000;
}

.option-content {
  font-size: 1.1em;
  color: #eee;
}
</style>
