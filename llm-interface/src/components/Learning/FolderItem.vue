<template>
  <div class="folder-wrapper">
    <div class="file-item folder" @click="active = !active">
      <div v-for="i in level" :key="i" class="folder-spacer"></div>
      <q-icon class="file-expand" :class="{ active: active }" name="fas fa-chevron-right" />
      <!-- <q-icon class="file-icon" name="fas fa-folder" /> -->
      <div class="file-name">{{ name }}</div>
    </div>
    <div class="folder-list" :class="{ active: active }" :style="cssProps">
      <template v-for="item in children" :key="item">
        <folder-item v-if="item.type == 'folder'" v-bind="item" :level="level + 1" />
        <note-item v-else-if="item.type == 'note'" v-bind="item" :level="level + 1" />
      </template>
    </div>
  </div>
</template>

<script>
import { defineComponent } from 'vue'
import NoteItem from './NoteItem.vue'

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
      default: 'Folder Name',
    },
    children: {
      type: Array,
      required: false,
      default: () => [],
    },
    level: {
      type: Number,
      required: false,
      default: 0,
    },
  },
  components: { NoteItem },
  setup() {
    return {}
  },
  data() {
    return {
      active: false,
    }
  },
  methods: {},
  mounted() {},
  computed: {
    cssProps() {
      return `--list-height: ${this.children.length * 30}px;`
    },
  },
})
</script>
<style scoped>
.folder-list {
  transition: height 0.3s;
  height: 0px;
  overflow: hidden;
}

.folder-list.active {
  height: var(--list-height);
}
</style>
