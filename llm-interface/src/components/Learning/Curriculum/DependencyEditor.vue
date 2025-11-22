<template>
  <div class="dependencies-layout">
    <div class="toolbar">
      <q-btn outline color="secondary" label="Add Dependency" @click="$emit('add-dependency')" />
    </div>
    <div class="dependencies-grid">
      <div v-for="(dep, dIndex) in dependencies" :key="dIndex" class="dependency-card">
        <div class="card-header">
          <span>Dependency {{ dIndex + 1 }}</span>
          <q-btn
            flat
            round
            icon="delete"
            color="negative"
            size="sm"
            @click="$emit('remove-dependency', dIndex)"
          />
        </div>
        <div class="card-body">
          <label>Source</label>
          <input v-model="dep.source" class="bare-input bordered" />
          <label>Target</label>
          <input v-model="dep.target" class="bare-input bordered" />
          <label>Reason</label>
          <textarea
            v-model="dep.reason"
            class="bare-input bordered"
            rows="1"
            @input="autoGrow($event.target)"
          ></textarea>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'DependencyEditor',
  props: {
    dependencies: {
      type: Array,
      required: true,
    },
  },
  emits: ['add-dependency', 'remove-dependency'],
  setup() {
    function autoGrow(element) {
      if (!element) return
      element.style.height = 'auto'
      element.style.height = element.scrollHeight + 'px'
    }
    return { autoGrow }
  },
})
</script>

<style scoped>
.dependencies-layout {
  padding: 20px;
  overflow-y: auto;
  width: 100%;
}

.dependencies-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.dependency-card {
  background-color: #252525;
  padding: 15px;
  border-radius: 6px;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.card-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 15px;
  color: var(--secondary);
  font-weight: bold;
}

.card-body {
  display: flex;
  flex-direction: column;
}

.card-body label {
  font-size: 0.8em;
  color: #777;
  margin-bottom: 4px;
}

.bare-input {
  background: transparent;
  border: none;
  color: inherit;
  width: 100%;
  outline: none;
  font-family: inherit;
  font-size: inherit;
  padding: 2px 0;
}

.bare-input:focus {
  box-shadow: 0 1px 0 0 var(--secondary);
}

.bare-input.bordered {
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 8px;
  border-radius: 4px;
  margin-bottom: 10px;
}
</style>
