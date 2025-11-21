<template>
  <div class="layout-container">
    <default-navbar />
    <div class="layout-main">
      <default-sidebar>
        <div class="q-pa-md text-white">
          <div class="text-h6 q-mb-sm">Folders</div>
          <q-tree :nodes="folders" node-key="label" dark default-expand-all />
        </div>
      </default-sidebar>
      <div class="content-container">
        <q-scroll-area style="height: calc(100vh - 35px)" dark>
          <div class="editor-wrapper">
            <div class="row items-center justify-between q-mb-md">
              <input v-if="editMode" class="note-title" type="text" v-model="title" />
              <div v-else class="note-title">{{ title }}</div>

              <div>
                <q-btn
                  color="secondary"
                  icon="auto_awesome"
                  label="Ask AI"
                  @click="askAI"
                  class="q-mr-sm"
                />
                <q-btn
                  :color="editMode ? 'primary' : 'grey'"
                  :label="editMode ? 'Save' : 'Edit'"
                  @click="toggleEditMode"
                />
              </div>
            </div>

            <div id="editor"></div>
          </div>
        </q-scroll-area>
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent } from 'vue'
import '@toast-ui/editor/dist/toastui-editor.css'
import '@toast-ui/editor/dist/theme/toastui-editor-dark.css'
import DefaultNavbar from 'src/components/Learning/DefaultNavbar.vue'
import DefaultSidebar from 'src/components/Learning/DefaultSidebar.vue'
import Editor from '@toast-ui/editor'
// import { useLearningStore } from 'src/stores/learning'
// import { llmService } from 'src/services/llm'

export default defineComponent({
  name: 'MarkdownEditorPage',
  components: { DefaultNavbar, DefaultSidebar },
  setup() {
    return {
      editor: null,
    }
  },
  data() {
    return {
      title: 'New Note',
      editorEl: null,
      previewEl: null,
      editMode: true,
      folders: [
        {
          label: 'Math',
          children: [
            { label: 'Algebra', icon: 'note' },
            { label: 'Geometry', icon: 'note' },
          ],
        },
        {
          label: 'Science',
          children: [{ label: 'Physics', icon: 'note' }],
        },
      ],
    }
  },
  mounted() {
    this.editor = new Editor({
      el: document.querySelector('#editor'),
      height: '70vh',
      initialEditType: 'markdown',
      previewStyle: 'vertical',
      theme: 'dark',
    })

    this.editor.getMarkdown()
    const el = this.editor.getEditorElements()
    this.editorEl = el.mdEditor
    this.previewEl = el.mdPreview

    // Default content
    this.editor.setMarkdown('# My Notes\nStart typing or ask AI for help...')
  },
  methods: {
    async askAI() {
      const currentContent = this.editor.getMarkdown()
      // Mock AI suggestion
      const suggestion = `\n\n## AI Suggestion\nHere is a summary of the key points:\n- Point 1\n- Point 2`
      this.editor.setMarkdown(currentContent + suggestion)
    },
    toggleEditMode() {
      this.editMode = !this.editMode
    },
  },
  computed: {
    // ...
  },
})
</script>
<style scoped>
.editor-wrapper {
  padding: 20px 40px;
}

.note-title {
  width: 100%;
  font-size: 2em;
  font-weight: bold;
  margin-bottom: 8px;
  border: none;
  border-radius: 4px;
  background-color: transparent;
  color: #fff;
  outline: none;
  padding: 0px;
}

.edit-toggle {
  position: fixed;
  top: 40px;
  right: 5px;
}

.btn {
  background-color: #1976d2;
  color: white;
  font-weight: bold;
  border: none;
  padding: 5px 15px;
  margin: 5px;
  border-radius: 4px;
  cursor: pointer;
  transition: opacity 0.3s;
}

.btn:hover {
  opacity: 0.9;
}
</style>
