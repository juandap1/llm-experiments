<template>
  <div class="q-pa-md">
    <div class="text-h4 q-mb-md">Learning Analytics</div>

    <div class="row q-col-gutter-md">
      <!-- Progress Overview -->
      <div class="col-12 col-md-4">
        <q-card class="my-card">
          <q-card-section>
            <div class="text-h6">Current Level</div>
            <div class="text-h3 text-primary">{{ userProfile.level || 'Not Assessed' }}</div>
          </q-card-section>
        </q-card>
      </div>

      <div class="col-12 col-md-4">
        <q-card class="my-card">
          <q-card-section>
            <div class="text-h6">Topics Mastered</div>
            <div class="text-h3 text-positive">0</div>
          </q-card-section>
        </q-card>
      </div>

      <div class="col-12 col-md-4">
        <q-card class="my-card">
          <q-card-section>
            <div class="text-h6">Study Streak</div>
            <div class="text-h3 text-orange">1 Day</div>
          </q-card-section>
        </q-card>
      </div>

      <!-- Charts (Placeholders) -->
      <div class="col-12 col-md-8">
        <q-card>
          <q-card-section>
            <div class="text-h6">Growth Over Time</div>
            <div class="chart-placeholder bg-grey-2 flex flex-center">[Line Chart Placeholder]</div>
          </q-card-section>
        </q-card>
      </div>

      <div class="col-12 col-md-4">
        <q-card>
          <q-card-section>
            <div class="text-h6">Skill Breakdown</div>
            <div class="chart-placeholder bg-grey-2 flex flex-center">
              [Radar Chart Placeholder]
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent, computed } from 'vue'
import { useLearningStore } from 'src/stores/learning'

export default defineComponent({
  name: 'AnalyticsPage',
  setup() {
    const store = useLearningStore()
    const userProfile = computed(() => store.userProfile)

    return {
      userProfile,
    }
  },
})
</script>

<style scoped>
.chart-placeholder {
  height: 300px;
  border-radius: 8px;
  color: #666;
}
</style>
