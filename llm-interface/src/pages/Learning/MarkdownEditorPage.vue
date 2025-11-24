<template>
  <div class="layout-container">
    <tabs-navbar />
    <div class="layout-main">
      <inspector-sidebar />
      <div class="content-container">
        <q-scroll-area style="height: calc(100vh - 35px)" dark>
          <div class="editor-wrapper">
            <input
              v-if="editMode"
              id="note-title-inp"
              class="note-title"
              type="text"
              v-model="title"
              @keyup="titleInpHandler"
            />
            <div v-else class="note-title">{{ title }}</div>
            <div class="toastui-editor-dark hide-toolbar" id="editor" @click="focusEditor"></div>
          </div>
        </q-scroll-area>
        <div class="edit-toggle">
          <button v-if="!editMode" @click="toggleEditMode" class="btn">Edit Note</button>
          <button v-else @click="toggleEditMode" class="btn">Save Changes</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent } from 'vue'
import '@toast-ui/editor/dist/toastui-editor.css'
import '@toast-ui/editor/dist/theme/toastui-editor-dark.css'
// https://nhn.github.io/tui.editor/latest/ToastUIEditorCore
// https://ui.toast.com/tui-editor
import TabsNavbar from 'src/components/Learning/TabsNavbar.vue'
import InspectorSidebar from 'src/components/Learning/InspectorSidebar.vue'

import Editor from '@toast-ui/editor'
import { useNotesStore } from 'src/stores/notes'

export default defineComponent({
  name: 'MarkdownEditorPage',
  components: { TabsNavbar, InspectorSidebar },
  setup() {
    return {
      editor: null,
    }
  },
  data() {
    return {
      title: 'Note Name',
      editorEl: null,
      previewEl: null,
      editMode: false,
    }
  },
  mounted() {
    this.editor = new Editor({
      el: document.querySelector('#editor'),
      height: 'auto',
      initialEditType: 'markdown',
      previewStyle: 'tab',
      hideModeSwitch: true,
      previewHighlight: false,
    })

    this.editor.getMarkdown()
    const el = this.editor.getEditorElements()
    this.editorEl = el.mdEditor
    this.previewEl = el.mdPreview

    document.querySelector('.ProseMirror').addEventListener('keydown', this.onEditorKeyUp)
    if (this.noteData) {
      this.loadNoteData()
    }
    this.editorEl.style.display = 'none'
    this.previewEl.style.display = 'block'
  },
  methods: {
    titleInpHandler(event) {
      if (event.key === 'ArrowDown' || event.key === 'Enter' || event.key === 'Tab') {
        event.preventDefault()
        this.editor.focus()
      }
    },
    onEditorKeyUp(e) {
      if (e.key === 'ArrowUp') {
        const selection = this.editor.getSelection()
        if (selection[0][0] === 1 && selection[0][1] === 1 && selection[1][0] === selection[1][1]) {
          e.preventDefault()
          document.querySelector('#note-title-inp').focus()
        }
      }
    },
    loadNoteData() {
      this.title = this.noteData.name
      this.editor.reset()
      this.editor.setMarkdown(this.noteData.content || '')
      this.editor.moveCursorToStart()
    },
    toggleEditMode() {
      this.editMode = !this.editMode
      if (this.editMode) {
        this.editorEl.style.display = 'block'
        this.previewEl.style.display = 'none'
        this.editor.focus()
      } else {
        this.editorEl.style.display = 'none'
        this.previewEl.style.display = 'block'
        this.saveNoteChanges()
      }
    },
  },
  computed: {
    noteData() {
      return useNotesStore().activeNoteData
    },
  },
  watch: {
    'noteData.id': function () {
      this.loadNoteData()
    },
  },
})
</script>
<style scoped>
.layout-container {
  flex: 1 1 auto;
  display: flex;
  flex-flow: column;
}

.layout-main {
  display: flex;
  height: calc(100vh - 30px);
}

.content-container {
  flex: 1 1 auto;
  background-color: #111;
}

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
