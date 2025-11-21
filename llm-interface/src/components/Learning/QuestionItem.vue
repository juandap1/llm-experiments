<template>
  <div class="question-item">
    <div class="question-item-header">
      <div class="question-number">1</div>
      <div class="question-preview">
        A company operates a three-tier application with all its components hosted on AWS, except
        for the data layer. This data layer consists of a MySQL-compatible database located
        on-premises, connected to AWS through a Site-to-Site VPN. The database’s memory consumption
        ranges from 2 to 16 GiB. On the other hand, the application experiences unpredictable
        traffic patterns, including spikes and periods of zero activity, which translates to
        irregular load on the database. The company wants to replace the on-premises database with a
        managed service that can automatically adapt to varying demands. Which option will meet
        these requirements?
      </div>
    </div>
    <div class="question-item-footer">
      <div class="question-type"><q-icon name="fas fa-check-to-slot" /> Multiple Choice</div>
      <q-icon name="fas fa-ellipsis" />
    </div>
  </div>
</template>

<script>
import { useStore } from 'src/stores/store'
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'QuestionItem',
  props: {},
  components: {},
  setup() {
    return {
      store: useStore(),
    }
  },
  data() {
    return {}
  },
  methods: {},
  mounted() {},
  computed: {},
})
</script>
<style scoped>
.question-item {
  border: 1px solid #444;
  border-radius: 8px;
  padding: 8px;
  margin-bottom: 16px;
  width: 100%;
  max-width: 100%;
  cursor: pointer;
}

.question-item-header {
  display: flex;
  align-items: center;
  gap: 5px;
}

.question-number {
  width: 24px;
  min-width: 24px;
  height: 24px;
  background-color: #333;
  font-size: 14px;
  font-weight: bold;
  line-height: 1;
  border-radius: 5px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.question-preview {
  flex-grow: 1;
  height: 20px;
  border-radius: 5px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-weight: 500;
}

.question-type {
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 13px;
}

.question-item-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
}
</style>
