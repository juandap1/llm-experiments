// src/services/llm.js

// This service abstracts the LLM calls.
// In a real implementation, this would call an API (OpenAI, Gemini, etc.)
// For now, we can mock responses or set up the structure for the API call.

const MOCK_DELAY = 1000

export const llmService = {
  async generateAssessment(topic) {
    console.log(`Generating assessment for ${topic}...`)
    // TODO: Replace with actual API call
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve([
          {
            id: 1,
            question: 'What is 2 + 2?',
            options: ['3', '4', '5', '6'],
            correctIndex: 1,
            difficulty: 'easy',
          },
          {
            id: 2,
            question: 'Solve for x: 2x = 10',
            options: ['2', '5', '10', '20'],
            correctIndex: 1,
            difficulty: 'medium',
          },
        ])
      }, MOCK_DELAY)
    })
  },

  async evaluateLevel(answers) {
    console.log('Evaluating level based on answers:', answers)
    // TODO: Replace with actual API call
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve('Beginner')
      }, MOCK_DELAY)
    })
  },

  async generateCurriculum(topic, level) {
    console.log(`Generating curriculum for ${topic} at ${level} level...`)
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve([
          { id: '1', label: 'Introduction to Numbers', status: 'open', children: [] },
          { id: '2', label: 'Basic Addition', status: 'locked', children: [] },
          { id: '3', label: 'Basic Subtraction', status: 'locked', children: [] },
        ])
      }, MOCK_DELAY)
    })
  },

  async generateLesson(topicId) {
    console.log(`Generating lesson for topic ${topicId}...`)
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          title: 'Introduction to Numbers',
          content: `
# Introduction to Numbers

Numbers are the building blocks of mathematics.

## What is a Number?
A number is a mathematical object used to count, measure, and label.

![Whiteboard drawing of numbers 1 through 10](placeholder_image_url)

## Types of Numbers
* **Natural Numbers**: 1, 2, 3...
* **Whole Numbers**: 0, 1, 2, 3...
* **Integers**: ...-2, -1, 0, 1, 2...
          `,
          visualPrompts: ['Whiteboard drawing of numbers 1 through 10 in a fun cartoon style'],
        })
      }, MOCK_DELAY)
    })
  },

  async generateQuizQuestion(topic, difficulty) {
    // ...
  },

  async chat(context, message) {
    // ...
  },
}
