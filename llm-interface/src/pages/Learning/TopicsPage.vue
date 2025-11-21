<template>
  <div class="q-pa-md">
    <div class="text-h4 q-mb-md">Curriculum: {{ userProfile.level || 'General' }}</div>

    <div v-if="loading" class="flex flex-center" style="height: 50vh">
      <q-spinner size="50px" color="primary" />
    </div>

    <div v-else class="row q-col-gutter-md">
      <div v-for="topic in curriculum.nodes" :key="topic.id" class="col-12 col-sm-6 col-md-4">
        <q-card
          class="topic-card cursor-pointer"
          :class="{ locked: topic.status === 'locked', completed: topic.status === 'completed' }"
          @click="openTopic(topic)"
        >
          <q-card-section>
            <div class="row items-center justify-between">
              <div class="text-h6">{{ topic.label }}</div>
              <q-icon
                :name="getStatusIcon(topic.status)"
                :color="getStatusColor(topic.status)"
                size="sm"
              />
            </div>
          </q-card-section>

          <q-card-section>
            <div class="text-caption text-grey">
              {{ topic.description || 'Click to start this lesson.' }}
            </div>
          </q-card-section>

          <q-separator />

          <q-card-actions align="right">
            <q-btn
              flat
              :color="getStatusColor(topic.status)"
              :label="getActionLabel(topic.status)"
            />
          </q-card-actions>
        </q-card>
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent, ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useLearningStore } from 'src/stores/learning'
import { llmService } from 'src/services/llm'

export default defineComponent({
  name: 'TopicsPage',
  setup() {
    const store = useLearningStore()
    const router = useRouter()
    const loading = ref(true)

    const userProfile = computed(() => store.userProfile)
    const curriculum = computed(() => store.curriculum)

    onMounted(async () => {
      loading.value = true
      if (store.curriculum.nodes.length === 0) {
        // Generate curriculum if empty
        const topics = await llmService.generateCurriculum(
          'Math',
          userProfile.value.level || 'Beginner',
        )
        store.setCurriculum(topics)
      }
      loading.value = false
    })

    function getStatusIcon(status) {
      switch (status) {
        case 'completed':
          return 'check_circle'
        case 'locked':
          return 'lock'
        default:
          return 'play_circle'
      }
    }

    function getStatusColor(status) {
      switch (status) {
        case 'completed':
          return 'positive'
        case 'locked':
          return 'grey'
        default:
          return 'primary'
      }
    }

    function getActionLabel(status) {
      switch (status) {
        case 'completed':
          return 'Review'
        case 'locked':
          return 'Locked'
        default:
          return 'Start'
      }
    }

    function openTopic(topic) {
      if (topic.status === 'locked') return
      router.push(`/learning/lesson/${topic.id}`)
    }

    return {
      loading,
      userProfile,
      curriculum,
      getStatusIcon,
      getStatusColor,
      getActionLabel,
      openTopic,
    }
  },
})
</script>

<style scoped>
.topic-card {
  transition: transform 0.2s;
}
.topic-card:hover:not(.locked) {
  transform: translateY(-5px);
}
.topic-card.locked {
  opacity: 0.7;
  cursor: not-allowed;
}
</style>
