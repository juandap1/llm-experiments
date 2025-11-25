<template>
  <div class="lesson-content">
    <div class="lesson-header">
      <h1>Introduction to Large Language Models</h1>
      <div class="meta">
        <q-chip size="sm" color="primary" text-color="white">Beginner</q-chip>
        <span class="duration">10 min read</span>
      </div>
    </div>

    <div class="content-body">
      <p class="intro">
        Large Language Models (LLMs) represent a significant leap forward in artificial
        intelligence, capable of understanding and generating human-like text.
      </p>

      <h2>What are LLMs?</h2>
      <p>
        At their core, LLMs are deep learning models trained on massive datasets of text. They learn
        patterns, grammar, and reasoning abilities by predicting the next word in a sequence.
      </p>

      <div class="highlight-box">
        <q-icon name="lightbulb" size="sm" class="q-mr-sm" />
        <strong>Key Insight:</strong> LLMs don't just memorize text; they build a statistical model
        of language.
      </div>

      <h2>How do they work?</h2>
      <p>
        LLMs process text as "tokens". A token can be a word, part of a word, or a character. The
        model uses an architecture called the <strong>Transformer</strong> to pay attention to
        different parts of the input simultaneously.
      </p>

      <div class="image-placeholder">[Diagram: Transformer Architecture Visualization]</div>
    </div>
  </div>
</template>

<script>
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'LessonContent',
})
</script>

<style scoped>
.lesson-content {
  max-width: 800px;
  margin: 0 auto;
  color: #e0e0e0;
}

.lesson-header {
  margin-bottom: 40px;
  border-bottom: 1px solid #333;
  padding-bottom: 20px;
}

h1 {
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 15px;
  line-height: 1.2;
}

.meta {
  display: flex;
  align-items: center;
  gap: 15px;
}

.duration {
  color: #888;
  font-size: 14px;
}

.content-body {
  font-size: 16px;
  line-height: 1.6;
}

h2 {
  font-size: 24px;
  font-weight: 600;
  margin-top: 40px;
  margin-bottom: 20px;
  color: #4caf50;
}

p {
  margin-bottom: 20px;
  color: #ccc;
}

.intro {
  font-size: 18px;
  color: #e0e0e0;
  margin-bottom: 30px;
}

.highlight-box {
  background-color: rgba(76, 175, 80, 0.1);
  border: 1px solid rgba(76, 175, 80, 0.3);
  padding: 20px;
  border-radius: 8px;
  margin: 30px 0;
  display: flex;
  align-items: center;
}

.image-placeholder {
  width: 100%;
  height: 200px;
  background-color: #2a2a2a;
  border: 2px dashed #444;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
  margin: 30px 0;
}
</style>
