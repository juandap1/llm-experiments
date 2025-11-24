<template>
  <div class="file-item note" :class="{ active: isActive }" @click="store.setActiveNote(id)">
    <div v-for="i in level" :key="i" class="folder-spacer"></div>
    <!-- <q-icon class="file-icon" name="fas fa-folder" /> -->
    <div class="file-name">{{ name }}</div>
  </div>
</template>

<script>
import { useNotesStore } from 'src/stores/notes'
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'FolderItem',
  props: {
    id: {
      type: [String, Number],
      required: true,
    },
    name: {
      type: String,
      required: false,
      default: 'Note Name',
    },
    level: {
      type: Number,
      required: false,
      default: 0,
    },
  },
  components: {},
  setup() {
    return {
      store: useNotesStore(),
    }
  },
  data() {
    return {}
  },
  methods: {},
  mounted() {},
  computed: {
    isActive() {
      return useNotesStore()._activeNote === this.id
    },
  },
})
</script>
<style scoped></style>
