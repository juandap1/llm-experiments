<template>
  <div class="layout-container">
    <default-navbar />
    <div class="layout-main">
      <default-sidebar>
        <question-item />
      </default-sidebar>
      <div class="content-container">
        <progress-bar :percent="45" />
        <div class="exam-header">
          <div class="back-btn" v-if="false">
            <q-icon name="fas fa-arrow-left" />
          </div>
          <div>
            <div class="exam-title">Exam Title</div>
            <div class="question-label">
              <div>Question 1</div>
              <div style="font-size: 23px; margin: 0px 2.5px; line-height: 1">/</div>
              <div>5</div>
            </div>
          </div>
        </div>
        <div class="main-cont">
          <div class="test-shell">
            <div class="test-cont shadow-6">
              <question-template />
            </div>
            <div class="cont-fade-1 shadow-6"></div>
            <div class="cont-fade-2 shadow-6"></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent, ref, onMounted } from 'vue'
import DefaultNavbar from 'src/components/Learning/DefaultNavbar.vue'
import DefaultSidebar from 'src/components/Learning/DefaultSidebar.vue'
import ProgressBar from 'src/components/ProgressBar.vue'
import QuestionTemplate from 'src/components/Learning/QuestionTemplate.vue'
import QuestionItem from 'src/components/Learning/QuestionItem.vue'
import { useLearningStore } from 'src/stores/learning'
import { llmService } from 'src/services/llm'

export default defineComponent({
  name: 'QuizPage',
  components: { DefaultNavbar, DefaultSidebar, ProgressBar, QuestionTemplate, QuestionItem },
  setup() {
    const store = useLearningStore()
    const questions = ref([])
    const loading = ref(true)

    onMounted(async () => {
      loading.value = true
      // Fetch questions for current level/weaknesses
      // For now, just asking for 'General Math'
      questions.value = await llmService.generateAssessment('General Math')
      loading.value = false
    })

    return {
      questions,
      loading,
    }
  },
})
</script>
<style scoped>
.exam-header {
  padding: 0px 5vw;
  display: flex;
  align-items: center;
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
  margin-bottom: 2.5px;
  margin-top: 20px;
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
}

.test-shell {
  width: 80%;
}

.test-cont {
  padding: 20px 25px;
  background-color: rgb(255, 255, 255, 0.1);
  border-radius: 20px;
  display: flex;
  flex-flow: column;
  padding-bottom: 30px;
}

.cont-fade-1 {
  width: 95%;
  border-radius: 0px 0px 20px 20px;
  height: 10px;
  background-color: rgb(39, 39, 61);
  margin: auto;
}

.cont-fade-2 {
  width: 90%;
  border-radius: 0px 0px 20px 20px;
  height: 10px;
  background-color: rgb(26, 26, 66);
  margin: auto;
}
</style>
