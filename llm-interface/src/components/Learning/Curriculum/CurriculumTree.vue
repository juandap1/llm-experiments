<template>
  <div class="master-pane">
    <div class="pane-header">
      <span>Hierarchy</span>
      <q-btn
        flat
        round
        icon="add"
        size="sm"
        color="secondary"
        @click="$emit('add-unit')"
        title="Add Unit"
      />
    </div>
    <div class="tree-list">
      <div v-for="(unit, uIndex) in units" :key="uIndex" class="unit-group">
        <!-- Unit Row -->
        <div
          class="tree-item unit-item"
          :class="{ active: selectedUnitIndex === uIndex && selectedConceptIndex === null }"
          @click="$emit('select-unit', uIndex)"
        >
          <q-icon name="school" size="xs" class="q-mr-sm text-grey-6" />
          <input v-model="unit.unit" class="bare-input" placeholder="Unit Name" />
          <div class="item-actions">
            <q-btn
              flat
              round
              icon="add"
              color="secondary"
              size="xs"
              @click.stop="$emit('add-concept', unit)"
              title="Add Concept"
            />
            <q-btn
              flat
              round
              icon="delete"
              color="negative"
              size="xs"
              @click.stop="$emit('remove-unit', uIndex)"
            />
          </div>
        </div>

        <!-- Concepts List -->
        <div class="concepts-list">
          <div
            v-for="(concept, cIndex) in unit.data.concepts"
            :key="cIndex"
            class="tree-item concept-item"
            :class="{ active: selectedUnitIndex === uIndex && selectedConceptIndex === cIndex }"
            @click.stop="$emit('select-concept', uIndex, cIndex)"
          >
            <q-icon name="lightbulb" size="xs" class="q-mr-sm text-grey-6" />
            <input v-model="concept.name" class="bare-input" placeholder="Concept Name" />
            <div class="item-actions">
              <q-btn
                flat
                round
                icon="delete"
                color="negative"
                size="xs"
                @click.stop="$emit('remove-concept', unit, cIndex)"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'CurriculumTree',
  props: {
    units: {
      type: Array,
      required: true,
    },
    selectedUnitIndex: {
      type: Number,
      default: null,
    },
    selectedConceptIndex: {
      type: Number,
      default: null,
    },
  },
  emits: [
    'add-unit',
    'remove-unit',
    'select-unit',
    'add-concept',
    'remove-concept',
    'select-concept',
  ],
})
</script>

<style scoped>
.master-pane {
  width: 300px;
  min-width: 250px;
  display: flex;
  flex-direction: column;
  border-right: 1px solid rgba(255, 255, 255, 0.1);
  padding-right: 10px;
}

.pane-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  font-weight: bold;
  font-size: 1.1em;
  color: #ddd;
}

.tree-list {
  flex: 1;
  overflow-y: auto;
}

.unit-group {
  margin-bottom: 5px;
}

.tree-item {
  display: flex;
  align-items: center;
  padding: 8px 10px;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.2s;
}

.tree-item:hover {
  background-color: rgba(255, 255, 255, 0.05);
}

.tree-item.active {
  background-color: rgba(6, 214, 113, 0.15);
  color: var(--secondary);
}

.tree-item .item-actions {
  display: none;
  margin-left: auto;
}

.tree-item:hover .item-actions {
  display: flex;
}

.unit-item {
  font-weight: 600;
}

.concepts-list {
  margin-left: 20px;
  border-left: 1px solid rgba(255, 255, 255, 0.1);
}

.concept-item {
  font-size: 0.95em;
  padding: 6px 10px;
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
</style>
