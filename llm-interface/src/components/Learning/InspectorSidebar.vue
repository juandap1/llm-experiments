<template>
  <div class="sidebar-wrapper">
    <div class="side-header">AWS Cloud Architect Associate</div>
    <div class="sidebar-content">
      <q-scroll-area class="side-scroller">
        <template v-for="item in content" :key="item">
          <folder-item v-if="item.type == 'folder'" v-bind="item" :level="0" />
          <note-item v-else-if="item.type == 'note'" v-bind="item" :level="0" />
        </template>
      </q-scroll-area>
    </div>
  </div>
</template>

<script>
import { defineComponent } from 'vue'
import FolderItem from './FolderItem.vue'
import NoteItem from './NoteItem.vue'
import { useStore } from 'src/stores/store'

export default defineComponent({
  name: 'InspectorSidebar',
  props: {},
  components: { FolderItem, NoteItem },
  setup() {
    return {
      content: useStore().sample,
    }
  },
  data() {
    return {}
  },
  methods: {},
  mounted() {},
})
</script>
<style scoped></style>
