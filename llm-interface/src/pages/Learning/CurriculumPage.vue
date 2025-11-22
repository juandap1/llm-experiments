<template>
  <div class="curriculum-page">
    <div class="header-row">
      <div class="text-h4">Curriculum Editor</div>
      <div class="actions">
        <q-btn flat icon="refresh" @click="loadCurriculum" :loading="loading" color="white" />
        <q-btn color="secondary" label="Save Changes" @click="saveCurriculum" :loading="saving" />
      </div>
    </div>

    <div v-if="loading" class="loading-container">
      <q-spinner size="50px" color="secondary" />
    </div>

    <div v-else class="editor-container">
      <div class="tabs-header">
        <div
          class="tab-btn"
          :class="{ active: activeTab === 'content' }"
          @click="activeTab = 'content'"
        >
          Content
        </div>
        <div
          class="tab-btn"
          :class="{ active: activeTab === 'dependencies' }"
          @click="activeTab = 'dependencies'"
        >
          Dependencies
        </div>
        <div class="tab-btn" :class="{ active: activeTab === 'json' }" @click="activeTab = 'json'">
          Raw JSON
        </div>
      </div>

      <div class="tab-content">
        <!-- Content Tab: Master-Detail Layout -->
        <div v-if="activeTab === 'content'" class="master-detail-layout">
          <!-- Master Pane: Hierarchy Tree -->
          <div class="master-pane">
            <div class="pane-header">
              <span>Hierarchy</span>
              <q-btn
                flat
                round
                icon="add"
                size="sm"
                color="secondary"
                @click="addUnit"
                title="Add Unit"
              />
            </div>
            <div class="tree-list">
              <div
                v-for="(unit, uIndex) in curriculum.units_content"
                :key="uIndex"
                class="unit-group"
              >
                <!-- Unit Row -->
                <div
                  class="tree-item unit-item"
                  :class="{ active: selectedUnitIndex === uIndex && selectedConceptIndex === null }"
                  @click="selectUnit(uIndex)"
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
                      @click.stop="addConcept(unit)"
                      title="Add Concept"
                    />
                    <q-btn
                      flat
                      round
                      icon="delete"
                      color="negative"
                      size="xs"
                      @click.stop="removeUnit(uIndex)"
                    />
                  </div>
                </div>

                <!-- Concepts List -->
                <div class="concepts-list">
                  <div
                    v-for="(concept, cIndex) in unit.data.concepts"
                    :key="cIndex"
                    class="tree-item concept-item"
                    :class="{
                      active: selectedUnitIndex === uIndex && selectedConceptIndex === cIndex,
                    }"
                    @click.stop="selectConcept(uIndex, cIndex)"
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
                        @click.stop="removeConcept(unit, cIndex)"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Detail Pane: Rules & Skills -->
          <div class="detail-pane">
            <div v-if="selectedConcept" class="detail-content">
              <div class="pane-header">
                <span>{{ selectedConcept.name || 'Untitled Concept' }}</span>
                <q-btn
                  flat
                  round
                  icon="add"
                  size="sm"
                  color="secondary"
                  label="Add Rule"
                  @click="addRule(selectedConcept)"
                />
              </div>

              <div class="rules-container">
                <div
                  v-for="(rule, rIndex) in selectedConcept.rules"
                  :key="rIndex"
                  class="rule-block"
                >
                  <div class="rule-header">
                    <div class="rule-title-wrapper">
                      <span class="label">Rule:</span>
                      <input
                        v-model="rule.name"
                        class="bare-input rule-input"
                        placeholder="Rule Name"
                      />
                    </div>
                    <q-btn
                      flat
                      round
                      icon="close"
                      color="grey-7"
                      size="xs"
                      @click="removeRule(selectedConcept, rIndex)"
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
                          @click="removeSkill(rule, sIndex)"
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
            <div v-else-if="selectedUnit" class="empty-state">Select a Concept to view details</div>
            <div v-else class="empty-state">Select a Unit or Concept</div>
          </div>
        </div>

        <!-- Dependencies Tab -->
        <div v-if="activeTab === 'dependencies'" class="dependencies-layout">
          <div class="toolbar">
            <q-btn outline color="secondary" label="Add Dependency" @click="addDependency" />
          </div>
          <div class="dependencies-grid">
            <div
              v-for="(dep, dIndex) in curriculum.dependencies"
              :key="dIndex"
              class="dependency-card"
            >
              <div class="card-header">
                <span>Dependency {{ dIndex + 1 }}</span>
                <q-btn
                  flat
                  round
                  icon="delete"
                  color="negative"
                  size="sm"
                  @click="removeDependency(dIndex)"
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

        <!-- JSON Tab -->
        <div v-if="activeTab === 'json'" class="json-layout">
          <q-banner class="bg-warning text-black q-mb-md" rounded dense>
            <template v-slot:avatar>
              <q-icon name="warning" />
            </template>
            Edits made here will override the visual editor.
          </q-banner>
          <textarea
            v-model="jsonString"
            class="json-editor"
            @input="updateFromJSON($event.target.value)"
          ></textarea>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent, ref, onMounted, watch, computed, nextTick } from 'vue'
import { llmService } from 'src/services/llm'
import { useQuasar } from 'quasar'

export default defineComponent({
  name: 'CurriculumPage',
  setup() {
    const $q = useQuasar()
    const loading = ref(true)
    const saving = ref(false)
    const activeTab = ref('content')

    const curriculum = ref({
      units_content: [],
      dependencies: [],
    })

    const jsonString = ref('')

    // Selection state
    const selectedUnitIndex = ref(null)
    const selectedConceptIndex = ref(null)

    const selectedUnit = computed(() => {
      if (selectedUnitIndex.value === null) return null
      return curriculum.value.units_content[selectedUnitIndex.value]
    })

    const selectedConcept = computed(() => {
      if (!selectedUnit.value || selectedConceptIndex.value === null) return null
      return selectedUnit.value.data.concepts[selectedConceptIndex.value]
    })

    onMounted(async () => {
      await loadCurriculum()
    })

    watch(
      curriculum,
      (newVal) => {
        if (activeTab.value !== 'json') {
          jsonString.value = JSON.stringify(newVal, null, 2)
        }
      },
      { deep: true },
    )

    // Watch for selection changes to resize textareas
    watch(selectedConcept, () => {
      nextTick(() => {
        const textareas = document.querySelectorAll('textarea.skill-desc')
        textareas.forEach((el) => autoGrow(el))
      })
    })

    async function loadCurriculum() {
      try {
        loading.value = true
        const data = await llmService.getCurriculumJson()
        if (!data.units_content) data.units_content = []
        if (!data.dependencies) data.dependencies = []

        curriculum.value = data
        jsonString.value = JSON.stringify(data, null, 2)

        if (data.units_content.length > 0) {
          selectedUnitIndex.value = 0
          if (data.units_content[0].data.concepts.length > 0) {
            selectedConceptIndex.value = 0
          }
        }
      } catch (error) {
        console.error('Error loading curriculum:', error)
        $q.notify({ color: 'negative', message: 'Failed to load curriculum' })
      } finally {
        loading.value = false
      }
    }

    function updateFromJSON(val) {
      try {
        const parsed = JSON.parse(val)
        curriculum.value = parsed
      } catch (e) {
        console.error('Error parsing JSON:', e)
      }
    }

    async function saveCurriculum() {
      try {
        saving.value = true
        if (activeTab.value === 'json') {
          try {
            curriculum.value = JSON.parse(jsonString.value)
          } catch (e) {
            console.error('Error parsing JSON:', e)
            $q.notify({ color: 'negative', message: 'Invalid JSON' })
            return
          }
        }
        await llmService.saveCurriculumJson(curriculum.value)
        $q.notify({ color: 'positive', message: 'Saved successfully' })
      } catch (error) {
        console.error('Error saving curriculum:', error)
        $q.notify({ color: 'negative', message: 'Failed to save' })
      } finally {
        saving.value = false
      }
    }

    function selectUnit(index) {
      selectedUnitIndex.value = index
      selectedConceptIndex.value = null
    }

    function selectConcept(uIndex, cIndex) {
      selectedUnitIndex.value = uIndex
      selectedConceptIndex.value = cIndex
    }

    function autoGrow(element) {
      if (!element) return
      element.style.height = 'auto'
      element.style.height = element.scrollHeight + 'px'
    }

    // CRUD Helpers
    function addUnit() {
      curriculum.value.units_content.push({
        unit: 'New Unit',
        order: curriculum.value.units_content.length,
        data: { concepts: [] },
      })
      selectedUnitIndex.value = curriculum.value.units_content.length - 1
      selectedConceptIndex.value = null
    }

    function removeUnit(index) {
      $q.dialog({
        title: 'Confirm',
        message: 'Delete this unit?',
        cancel: true,
        persistent: true,
        dark: true,
      }).onOk(() => {
        curriculum.value.units_content.splice(index, 1)
        if (selectedUnitIndex.value === index) {
          selectedUnitIndex.value = null
          selectedConceptIndex.value = null
        } else if (selectedUnitIndex.value > index) {
          selectedUnitIndex.value--
        }
      })
    }

    function addConcept(unit) {
      if (!unit.data) unit.data = { concepts: [] }
      if (!unit.data.concepts) unit.data.concepts = []
      unit.data.concepts.push({ name: 'New Concept', rules: [] })
      // Automatically select the new concept
      selectedUnitIndex.value = curriculum.value.units_content.indexOf(unit)
      selectedConceptIndex.value = unit.data.concepts.length - 1
    }

    function removeConcept(unit, index) {
      unit.data.concepts.splice(index, 1)
      if (selectedConceptIndex.value === index) selectedConceptIndex.value = null
    }

    function addRule(concept) {
      if (!concept.rules) concept.rules = []
      concept.rules.push({ name: 'New Rule', skills: [] })
    }

    function removeRule(concept, index) {
      concept.rules.splice(index, 1)
    }

    function addSkill(rule) {
      if (!rule.skills) rule.skills = []
      rule.skills.push({ name: 'New Skill', description: '' })
      nextTick(() => {
        // Trigger autogrow for new skill
        const textareas = document.querySelectorAll('textarea.skill-desc')
        if (textareas.length > 0) autoGrow(textareas[textareas.length - 1])
      })
    }

    function removeSkill(rule, index) {
      rule.skills.splice(index, 1)
    }

    function addDependency() {
      curriculum.value.dependencies.push({ source: '', target: '', reason: '' })
    }

    function removeDependency(index) {
      curriculum.value.dependencies.splice(index, 1)
    }

    return {
      loading,
      saving,
      activeTab,
      curriculum,
      jsonString,
      selectedUnitIndex,
      selectedConceptIndex,
      selectedUnit,
      selectedConcept,
      loadCurriculum,
      saveCurriculum,
      updateFromJSON,
      selectUnit,
      selectConcept,
      addUnit,
      removeUnit,
      addConcept,
      removeConcept,
      addRule,
      removeRule,
      addSkill,
      removeSkill,
      addDependency,
      removeDependency,
      autoGrow,
    }
  },
})
</script>

<style scoped>
.curriculum-page {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 50px);
  padding: 20px;
  background-color: #161616;
  color: #eee;
}

.header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.editor-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  /* Minimalist: No border, just background distinction if needed */
  /* border: 1px solid rgba(255, 255, 255, 0.1); */
  /* border-radius: 8px; */
  /* background-color: #1e1e1e; */
}

.tabs-header {
  display: flex;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  margin-bottom: 10px;
}

.tab-btn {
  padding: 10px 20px;
  cursor: pointer;
  font-weight: 500;
  color: #888;
  transition: all 0.2s;
}

.tab-btn:hover {
  color: #fff;
}

.tab-btn.active {
  color: var(--secondary);
  border-bottom: 2px solid var(--secondary);
}

.tab-content {
  flex: 1;
  overflow: hidden;
  display: flex;
}

/* Master-Detail Layout */
.master-detail-layout {
  display: flex;
  width: 100%;
  height: 100%;
  gap: 20px;
}

.master-pane {
  width: 300px;
  min-width: 250px;
  display: flex;
  flex-direction: column;
  border-right: 1px solid rgba(255, 255, 255, 0.1);
  padding-right: 10px;
}

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

/* Details Styling */
.rules-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.rule-block {
  /* Minimalist: No background, just spacing */
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

/* Inputs */
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
  /* Minimal focus indicator */
  box-shadow: 0 1px 0 0 var(--secondary);
}

.bare-input.bordered {
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 8px;
  border-radius: 4px;
  margin-bottom: 10px;
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #555;
  font-style: italic;
}

/* Dependencies */
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

/* JSON Layout */
.json-layout {
  display: flex;
  flex-direction: column;
  padding: 20px;
  width: 100%;
  height: 100%;
}

.json-editor {
  flex: 1;
  background-color: #111;
  color: #0f0;
  font-family: monospace;
  padding: 15px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  resize: none;
  outline: none;
}
</style>
