<template>
  <div class="basic-widget">
    <div class="widget-header">
      <h6>History</h6>
      <button class="alt-btn">
        <q-icon name="fas fa-plus" />
        Add
      </button>
    </div>
  </div>
</template>

<script>
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'HistoryWidget',
  props: {},
})
</script>
<style scoped>
.basic-widget {
  padding: 20px;
  border: 1px solid var(--border-color);
  border-radius: 15px;
}

.widget-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
</style>
