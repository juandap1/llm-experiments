import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useLearningStore = defineStore('learning', () => {
  // State
  const userProfile = ref({
    level: null, // e.g., 'Beginner', 'Intermediate', 'Advanced'
    topicMastery: {}, // { 'algebra': 0.8, 'geometry': 0.2 }
    history: [],
  })

  const curriculum = ref({
    nodes: [], // Tree structure of topics
    currentTopicId: null,
  })

  const currentLesson = ref({
    title: '',
    content: '', // Markdown
    visuals: [],
    interactiveChecks: [],
  })

  const quizState = ref({
    active: false,
    questions: [],
    currentQuestionIndex: 0,
    score: 0,
  })

  const notes = ref([]) // Array of note objects { id, title, content, folder }

  // Getters
  const currentTopic = computed(() => {
    return curriculum.value.nodes.find((n) => n.id === curriculum.value.currentTopicId)
  })

  const isAssessmentNeeded = computed(() => {
    return userProfile.value.level === null
  })

  // Actions
  function setLevel(level) {
    userProfile.value.level = level
  }

  function updateMastery(topic, score) {
    userProfile.value.topicMastery[topic] = score
  }

  function setCurriculum(topics) {
    curriculum.value.nodes = topics
  }

  function startLesson(topicId) {
    curriculum.value.currentTopicId = topicId
    // TODO: Trigger LLM generation
  }

  function addNote(note) {
    notes.value.push(note)
  }

  return {
    userProfile,
    curriculum,
    currentLesson,
    quizState,
    notes,
    currentTopic,
    isAssessmentNeeded,
    setLevel,
    updateMastery,
    setCurriculum,
    startLesson,
    addNote,
  }
})
