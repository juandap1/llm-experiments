<template>
  <div class="q-pa-md">
    <div v-if="loading" class="flex flex-center" style="height: 80vh">
      <q-spinner size="50px" color="primary" />
      <div class="text-h6 q-ml-md">Generating Lesson...</div>
    </div>

    <div v-else>
      <div class="text-h4 q-mb-md">{{ lesson.title }}</div>

      <!-- Content Area -->
      <div class="row q-col-gutter-md">
        <div class="col-12 col-md-8">
          <q-card>
            <q-card-section>
              <div v-html="renderedContent" class="markdown-content"></div>
            </q-card-section>
          </q-card>
        </div>

        <!-- Visuals / Helper Sidebar -->
        <div class="col-12 col-md-4">
          <q-card class="q-mb-md">
            <q-card-section>
              <div class="text-h6">Visuals</div>
              <div v-for="(visual, idx) in lesson.visuals" :key="idx" class="q-my-sm">
                <!-- Placeholder for generated image -->
                <q-img :src="visual" style="height: 200px; background-color: #eee">
                  <template v-slot:error>
                    <div class="absolute-full flex flex-center bg-grey-3 text-grey-8">
                      Generated Image Placeholder
                    </div>
                  </template>
                </q-img>
              </div>
            </q-card-section>
          </q-card>

          <q-card>
            <q-card-section>
              <div class="text-h6">AI Helper</div>
              <q-input
                v-model="question"
                label="Ask a question..."
                dense
                outlined
                @keyup.enter="askHelper"
              >
                <template v-slot:after>
                  <q-btn round dense flat icon="send" @click="askHelper" />
                </template>
              </q-input>
            </q-card-section>
          </q-card>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent, ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useLearningStore } from 'src/stores/learning'
import { llmService } from 'src/services/llm'
import { marked } from 'marked' // Assuming marked is available or we need to install it.
// If marked is not installed, we might need to use a simple text display or install it.
// For now, I'll assume we might need to handle markdown rendering.

export default defineComponent({
  name: 'LessonPage',
  setup() {
    const route = useRoute()
    const store = useLearningStore()
    const loading = ref(true)
    const lesson = ref({})
    const question = ref('')

    const renderedContent = computed(() => {
      // Simple markdown to HTML conversion (placeholder)
      // In real app, use 'marked' or similar library
      return lesson.value.content
        ? lesson.value.content
            .replace(/\n/g, '<br>')
            .replace(/# (.*)/g, '<h1>$1</h1>')
            .replace(/## (.*)/g, '<h2>$1</h2>')
        : ''
    })

    onMounted(async () => {
      const topicId = route.params.topicId
      loading.value = true
      try {
        const data = await llmService.generateLesson(topicId)
        lesson.value = data
        store.currentLesson = data
      } catch (e) {
        console.error(e)
      } finally {
        loading.value = false
      }
    })

    function askHelper() {
      console.log('Asking:', question.value)
      question.value = ''
    }

    return {
      loading,
      lesson,
      renderedContent,
      question,
      askHelper,
    }
  },
})
</script>

<style scoped>
.markdown-content {
  font-family: 'Arial', sans-serif;
  line-height: 1.6;
}
</style>
