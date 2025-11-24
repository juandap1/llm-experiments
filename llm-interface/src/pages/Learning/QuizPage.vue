<template>
  <div class="content-container">
    <progress-bar :percent="progressPercent" />
    <div class="exam-header">
      <div class="back-btn" v-if="false">
        <q-icon name="fas fa-arrow-left" />
      </div>
      <div>
        <div class="exam-title">General Math Assessment</div>
        <div class="question-label" v-if="!quizCompleted && questions.length > 0">
          <div>Question {{ currentQuestionIndex + 1 }}</div>
          <div style="font-size: 23px; margin: 0px 2.5px; line-height: 1">/</div>
          <div>{{ questions.length }}</div>
        </div>
      </div>
    </div>
    <div class="main-cont">
      <div class="test-shell" v-if="loading">
        <div class="test-cont shadow-6 flex flex-center" style="min-height: 300px">
          <q-spinner size="50px" color="secondary" />
        </div>
      </div>

      <div class="test-shell" v-else-if="!quizCompleted && questions.length > 0">
        <div class="test-cont shadow-6">
          <component
            :is="getComponentType(currentQuestion)"
            :question="currentQuestion"
            v-model="answers[currentQuestion.id]"
          />

          <div class="actions-row q-mt-xl flex justify-end">
            <q-btn
              v-if="currentQuestionIndex > 0"
              flat
              color="white"
              label="Previous"
              class="q-mr-sm"
              @click="prevQuestion"
            />
            <q-btn
              v-if="currentQuestionIndex < questions.length - 1"
              color="secondary"
              label="Next"
              @click="nextQuestion"
              :disable="answers[currentQuestion.id] === undefined"
            />
            <q-btn
              v-else
              color="primary"
              label="Submit Quiz"
              @click="submitQuiz"
              :disable="answers[currentQuestion.id] === undefined"
            />
          </div>
        </div>
        <div class="cont-fade-1 shadow-6"></div>
        <div class="cont-fade-2 shadow-6"></div>
      </div>

      <div class="test-shell" v-else-if="quizCompleted">
        <div class="test-cont shadow-6 text-center">
          <div class="text-h4 q-mb-md">Quiz Completed!</div>
          <div class="text-h2 text-secondary q-mb-lg">{{ score }}%</div>
          <div class="text-h6 q-mb-xl">
            You got {{ correctCount }} out of {{ questions.length }} questions correct.
          </div>
          <div>
            <q-btn outline color="white" label="Retake Quiz" @click="resetQuiz" />
          </div>
        </div>
        <div class="cont-fade-1 shadow-6"></div>
        <div class="cont-fade-2 shadow-6"></div>
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent, ref, computed, onMounted } from 'vue'
import ProgressBar from 'src/components/Learning/ProgressBar.vue'
import MultipleChoiceQuestion from 'src/components/Learning/Quiz/MultipleChoiceQuestion.vue'
import { useLearningStore } from 'src/stores/learning'
import { llmService } from 'src/services/llm'

export default defineComponent({
  name: 'QuizPage',
  components: { ProgressBar, MultipleChoiceQuestion },
  setup() {
    const store = useLearningStore()
    const questions = ref([])
    const loading = ref(true)
    const currentQuestionIndex = ref(0)
    const answers = ref({})
    const quizCompleted = ref(false)

    const currentQuestion = computed(() => {
      if (questions.value.length === 0) return null
      return questions.value[currentQuestionIndex.value]
    })

    const progressPercent = computed(() => {
      if (questions.value.length === 0) return 0
      if (quizCompleted.value) return 100
      return ((currentQuestionIndex.value + 1) / questions.value.length) * 100
    })

    const correctCount = computed(() => {
      if (!quizCompleted.value) return 0
      let correct = 0
      questions.value.forEach((q) => {
        if (answers.value[q.id] === q.correctIndex) {
          correct++
        }
      })
      return correct
    })

    const score = computed(() => {
      if (questions.value.length === 0) return 0
      return Math.round((correctCount.value / questions.value.length) * 100)
    })

    onMounted(async () => {
      await loadQuiz()
    })

    async function loadQuiz() {
      loading.value = true
      quizCompleted.value = false
      currentQuestionIndex.value = 0
      answers.value = {}
      // Fetch questions for current level/weaknesses
      // For now, just asking for 'General Math'
      questions.value = await llmService.generateAssessment('General Math')
      loading.value = false
    }

    function getComponentType(question) {
      // Future proofing: check question.type if it exists
      if (question.type === 'multiple_choice') {
        return 'MultipleChoiceQuestion'
      }
      return 'MultipleChoiceQuestion'
    }

    function nextQuestion() {
      if (currentQuestionIndex.value < questions.value.length - 1) {
        currentQuestionIndex.value++
      }
    }

    function prevQuestion() {
      if (currentQuestionIndex.value > 0) {
        currentQuestionIndex.value--
      }
    }

    function submitQuiz() {
      quizCompleted.value = true
    }

    function resetQuiz() {
      loadQuiz()
    }

    return {
      store,
      questions,
      loading,
      currentQuestionIndex,
      currentQuestion,
      answers,
      quizCompleted,
      progressPercent,
      correctCount,
      score,
      getComponentType,
      nextQuestion,
      prevQuestion,
      submitQuiz,
      resetQuiz,
    }
  },
})
</script>
<style scoped>
.layout-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.layout-main {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.content-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: #161616;
  color: #eee;
  overflow-y: auto;
}

.exam-header {
  padding: 0px 5vw;
  display: flex;
  align-items: center;
  margin-top: 20px;
}

.back-btn {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: rgb(255, 255, 255, 0.1);
  font-size: 20px;
  margin-right: 10px;
  cursor: pointer;
  transition: all 0.3s;
}

.back-btn:hover {
  scale: 1.05;
}

.exam-title {
  font-size: 28px;
  line-height: 1;
  margin-bottom: 5px;
  font-weight: bold;
}

.question-label {
  color: #a7a7a7;
  font-weight: bold;
  display: flex;
  align-items: center;
  font-size: 16px;
}

.main-cont {
  width: 100%;
  padding: 25px;
  display: flex;
  justify-content: center;
  flex: 1;
}

.test-shell {
  width: 80%;
  max-width: 800px;
}

.test-cont {
  padding: 30px 40px;
  background-color: #1e1e1e;
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 20px;
  display: flex;
  flex-flow: column;
  padding-bottom: 30px;
  min-height: 400px;
}

.cont-fade-1 {
  width: 95%;
  border-radius: 0px 0px 20px 20px;
  height: 10px;
  background-color: rgba(255, 255, 255, 0.05);
  margin: auto;
}

.cont-fade-2 {
  width: 90%;
  border-radius: 0px 0px 20px 20px;
  height: 10px;
  background-color: rgba(255, 255, 255, 0.03);
  margin: auto;
}
</style>
