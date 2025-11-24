<template>
  <div style="background-color: #333">
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
  </div>
</template>

<script>
import { defineComponent } from 'vue'
import FolderItem from './FolderItem.vue'
import NoteItem from './NoteItem.vue'
import { useNotesStore } from 'src/stores/notes'

export default defineComponent({
  name: 'InspectorSidebar',
  props: {},
  components: { FolderItem, NoteItem },
  setup() {
    return {
      content: useNotesStore().sample,
    }
  },
  data() {
    return {}
  },
  methods: {},
  mounted() {},
})
</script>
<style scoped>
.sidebar-wrapper {
  height: 100%;
  width: 250px;
  min-width: 250px;
  background-color: #222;
  /* border-right: 1px solid #333; */
  border-top-left-radius: 15px;
  display: flex;
  flex-flow: column;
}

.side-header {
  font-size: 16px;
  font-weight: 500;
  padding: 15px 10px;
  border-bottom: 1px solid #333;
}

.sidebar-content {
  flex: 1 1 auto;
}

.side-scroller {
  height: 100%;
  padding: 10px 0px;
}

.scroller-content {
  width: 250px;
  padding: 0px 10px;
}
</style>
