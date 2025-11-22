<template>
  <div class="detail-pane">
    <div v-if="concept" class="detail-content">
      <div class="pane-header">
        <span>{{ concept.name || 'Untitled Concept' }}</span>
        <q-btn
          flat
          icon="add"
          size="sm"
          color="secondary"
          label="Add Rule"
          @click="$emit('add-rule', concept)"
        />
      </div>

      <div class="rules-container">
        <div v-for="(rule, rIndex) in concept.rules" :key="rIndex" class="rule-block">
          <div class="rule-header">
            <div class="rule-title-wrapper">
              <span class="label">Rule:</span>
              <input v-model="rule.name" class="bare-input rule-input" placeholder="Rule Name" />
            </div>
            <q-btn
              flat
              round
              icon="close"
              color="grey-7"
              size="xs"
              @click="$emit('remove-rule', concept, rIndex)"
            />
          </div>

          <div class="skills-container">
            <div v-for="(skill, sIndex) in rule.skills" :key="sIndex" class="skill-block">
              <div class="skill-row">
                <span class="label">Skill:</span>
                <input
                  v-model="skill.name"
                  class="bare-input skill-input"
                  placeholder="Skill Name"
                />
                <q-btn
                  flat
                  round
                  icon="close"
                  color="grey-8"
                  size="xs"
                  @click="$emit('remove-skill', rule, sIndex)"
                />
              </div>
              <div class="skill-row description-row">
                <textarea
                  v-model="skill.description"
                  class="bare-input skill-desc"
                  placeholder="Description..."
                  rows="1"
                  @input="autoGrow($event.target)"
                  ref="textareas"
                ></textarea>
              </div>
            </div>
            <div class="add-skill-btn" @click="addSkill(rule)">
              <q-icon name="add" size="xs" /> Add Skill
            </div>
          </div>
        </div>
      </div>
    </div>
    <div v-else-if="hasUnitSelected" class="empty-state">Select a Concept to view details</div>
    <div v-else class="empty-state">Select a Unit or Concept</div>
  </div>
</template>

<script>
import { defineComponent, nextTick, watch } from 'vue'

export default defineComponent({
  name: 'ConceptDetails',
  props: {
    concept: {
      type: Object,
      default: null,
    },
    hasUnitSelected: {
      type: Boolean,
      default: false,
    },
  },
  emits: ['add-rule', 'remove-rule', 'add-skill', 'remove-skill'],
  setup(props, { emit }) {
    function autoGrow(element) {
      if (!element) return
      element.style.height = 'auto'
      element.style.height = element.scrollHeight + 'px'
    }

    function addSkill(rule) {
      emit('add-skill', rule)
      nextTick(() => {
        // We can't easily target the exact new textarea from here without refs or more logic,
        // but the parent component was handling this.
        // Ideally, we should handle it here.
        // Let's try to find the last textarea in the DOM for this rule or globally in this component.
        const textareas = document.querySelectorAll('textarea.skill-desc')
        if (textareas.length > 0) autoGrow(textareas[textareas.length - 1])
      })
    }

    // Watch for concept changes to re-trigger autogrow
    watch(
      () => props.concept,
      () => {
        nextTick(() => {
          const textareas = document.querySelectorAll('textarea.skill-desc')
          textareas.forEach((el) => autoGrow(el))
        })
      },
    )

    return {
      autoGrow,
      addSkill,
    }
  },
})
</script>

<style scoped>
.detail-pane {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  padding-left: 10px;
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

.rules-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.rule-block {
  padding-left: 15px;
  border-left: 2px solid rgba(255, 255, 255, 0.1);
}

.rule-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.rule-title-wrapper {
  display: flex;
  align-items: center;
  flex: 1;
}

.label {
  font-size: 0.8em;
  color: #777;
  margin-right: 10px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  min-width: 50px;
}

.rule-input {
  font-size: 1.1em;
  font-weight: 500;
}

.skills-container {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding-left: 20px;
}

.skill-block {
  margin-bottom: 5px;
}

.skill-row {
  display: flex;
  align-items: center;
  margin-bottom: 2px;
}

.description-row {
  align-items: flex-start;
}

.skill-input {
  font-weight: 500;
}

.skill-desc {
  font-size: 0.9em;
  color: #aaa;
  resize: none;
  overflow: hidden;
  line-height: 1.4;
  padding-top: 4px;
}

.add-skill-btn {
  font-size: 0.9em;
  color: #666;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 5px;
  margin-top: 5px;
}

.add-skill-btn:hover {
  color: var(--secondary);
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

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #555;
  font-style: italic;
}
</style>
