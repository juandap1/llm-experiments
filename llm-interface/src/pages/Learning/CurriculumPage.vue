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
          <CurriculumTree
            :units="curriculum.units_content"
            :selected-unit-index="selectedUnitIndex"
            :selected-concept-index="selectedConceptIndex"
            @add-unit="addUnit"
            @remove-unit="removeUnit"
            @select-unit="selectUnit"
            @add-concept="addConcept"
            @remove-concept="removeConcept"
            @select-concept="selectConcept"
          />

          <ConceptDetails
            :concept="selectedConcept"
            :has-unit-selected="selectedUnitIndex !== null"
            @add-rule="addRule"
            @remove-rule="removeRule"
            @add-skill="addSkill"
            @remove-skill="removeSkill"
          />
        </div>

        <!-- Dependencies Tab -->
        <DependencyEditor
          v-if="activeTab === 'dependencies'"
          :dependencies="curriculum.dependencies"
          :skills="allSkills"
          @add-dependency="addDependency"
          @remove-dependency="removeDependency"
          @update-dependency="updateDependency"
        />

        <!-- JSON Tab -->
        <JsonEditor
          v-if="activeTab === 'json'"
          v-model="jsonString"
          @update:model-value="updateFromJSON"
        />
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent } from 'vue'
import { llmService } from 'src/services/llm'
import CurriculumTree from 'src/components/Learning/Curriculum/CurriculumTree.vue'
import ConceptDetails from 'src/components/Learning/Curriculum/ConceptDetails.vue'
import DependencyEditor from 'src/components/Learning/Curriculum/DependencyEditor.vue'
import JsonEditor from 'src/components/Learning/Curriculum/JsonEditor.vue'

export default defineComponent({
  name: 'CurriculumPage',
  components: {
    CurriculumTree,
    ConceptDetails,
    DependencyEditor,
    JsonEditor,
  },
  setup() {
    return {}
  },
  data() {
    return {
      loading: false,
      saving: false,
      activeTab: 'content',
      curriculum: {
        units_content: [],
        dependencies: [],
      },
      jsonString: '',
      selectedUnitIndex: null,
      selectedConceptIndex: null,
    }
  },
  mounted() {
    this.loadCurriculum()
  },
  methods: {
    async loadCurriculum() {
      try {
        this.loading = true
        const data = await llmService.getCurriculumJson()
        if (!data.units_content) data.units_content = []
        if (!data.dependencies) data.dependencies = []

        this.curriculum = data
        this.jsonString = JSON.stringify(data, null, 2)

        if (data.units_content.length > 0) {
          this.selectedUnitIndex = 0
          if (data.units_content[0].data.concepts.length > 0) {
            this.selectedConceptIndex = 0
          }
        }
      } catch (error) {
        console.error('Error loading curriculum:', error)
        this.$q.notify({ color: 'negative', message: 'Failed to load curriculum' })
      } finally {
        this.loading = false
      }
    },
    updateFromJSON(val) {
      try {
        const parsed = JSON.parse(val)
        this.curriculum = parsed
      } catch (e) {
        console.error('Error parsing JSON:', e)
      }
    },
    saveCurriculum: async () => {
      try {
        this.saving = true
        if (this.activeTab === 'json') {
          try {
            this.curriculum = JSON.parse(this.jsonString)
          } catch (e) {
            console.error('Error parsing JSON:', e)
            this.$q.notify({ color: 'negative', message: 'Invalid JSON' })
            return
          }
        }
        await llmService.saveCurriculumJson(this.curriculum)
        this.$q.notify({ color: 'positive', message: 'Saved successfully' })
      } catch (error) {
        console.error('Error saving curriculum:', error)
        this.$q.notify({ color: 'negative', message: 'Failed to save' })
      } finally {
        this.saving = false
      }
    },
    selectUnit(index) {
      this.selectedUnitIndex = index
      this.selectedConceptIndex = null
    },
    selectConcept(uIndex, cIndex) {
      this.selectedUnitIndex = uIndex
      this.selectedConceptIndex = cIndex
    },
    // CRUD Helpers
    addUnit() {
      this.curriculum.units_content.push({
        unit: 'New Unit',
        order: this.curriculum.units_content.length,
        data: { concepts: [] },
      })
      this.selectedUnitIndex = this.curriculum.units_content.length - 1
      this.selectedConceptIndex = null
    },
    removeUnit(index) {
      this.$q
        .dialog({
          title: 'Confirm',
          message: 'Delete this unit?',
          cancel: true,
          persistent: true,
          dark: true,
        })
        .onOk(() => {
          this.curriculum.units_content.splice(index, 1)
          if (this.selectedUnitIndex === index) {
            this.selectedUnitIndex = null
            this.selectedConceptIndex = null
          } else if (this.selectedUnitIndex > index) {
            this.selectedUnitIndex--
          }
        })
    },
    addConcept(unit) {
      if (!unit.data) unit.data = { concepts: [] }
      if (!unit.data.concepts) unit.data.concepts = []
      unit.data.concepts.push({ name: 'New Concept', rules: [] })
      // Automatically select the new concept
      this.selectedUnitIndex = this.curriculum.units_content.indexOf(unit)
      this.selectedConceptIndex = unit.data.concepts.length - 1
    },
    removeConcept(unit, index) {
      unit.data.concepts.splice(index, 1)
      if (this.selectedConceptIndex === index) this.selectedConceptIndex = null
    },
    addRule(concept) {
      if (!concept.rules) concept.rules = []
      concept.rules.push({ name: 'New Rule', skills: [] })
    },
    removeRule(concept, index) {
      concept.rules.splice(index, 1)
    },
    addSkill(rule) {
      if (!rule.skills) rule.skills = []
      rule.skills.push({ name: 'New Skill', description: '' })
    },
    removeSkill(rule, index) {
      rule.skills.splice(index, 1)
    },
    addDependency(payload) {
      if (payload && payload.source && payload.target) {
        this.curriculum.dependencies.push({
          source: payload.source,
          target: payload.target,
          reason: payload.reason || '',
        })
      } else {
        this.curriculum.dependencies.push({ source: '', target: '', reason: '' })
      }
    },
    updateDependency({ index, reason }) {
      if (this.curriculum.dependencies[index]) {
        this.curriculum.dependencies[index].reason = reason
      }
    },
    removeDependency(index) {
      this.curriculum.dependencies.splice(index, 1)
    },
  },
  watch: {
    curriculum: {
      handler(newVal) {
        if (this.activeTab !== 'json') {
          this.jsonString = JSON.stringify(newVal, null, 2)
        }
      },
      deep: true,
    },
  },
  computed: {
    selectedUnit() {
      if (this.selectedUnitIndex === null) return null
      return this.curriculum.units_content[this.selectedUnitIndex]
    },
    selectedConcept() {
      if (!this.selectedUnit || this.selectedConceptIndex === null) return null
      return this.selectedUnit.data.concepts[this.selectedConceptIndex]
    },
    allSkills() {
      const skills = []
      if (!this.curriculum.units_content) return skills

      this.curriculum.units_content.forEach((unit) => {
        if (!unit.data || !unit.data.concepts) return
        unit.data.concepts.forEach((concept) => {
          if (!concept.rules) return
          concept.rules.forEach((rule) => {
            if (!rule.skills) return
            rule.skills.forEach((skill) => {
              skills.push({
                id: skill.name,
                name: skill.name,
                description: skill.description,
                unit: unit.unit,
                concept: concept.name,
                rule: rule.name,
              })
            })
          })
        })
      })
      return skills
    },
  },
})
</script>

<style scoped>
.curriculum-page {
  flex: 1 1 auto;
  display: flex;
  flex-direction: column;
  height: 100vh;
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
</style>
