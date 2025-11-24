<template>
  <div class="navbar-wrapper">
    <div class="navbar-left-sect"></div>
    <div class="navbar-main">
      <div
        @click="store.setActiveNote(tab)"
        v-for="tab in store._openTabs"
        :key="tab"
        class="nav-tab"
        :class="{ active: store._activeNote == tab }"
      >
        <div>{{ store.noteMap[tab].name }}</div>
        <q-icon name="fas fa-times" />
      </div>
      <div
        v-if="store._activeNote"
        class="add-tab-wrapper"
        :class="{
          'no-line': store._activeNote == store._openTabs[store._openTabs.length - 1],
        }"
      >
        <div class="add-tab-btn">
          <q-icon name="fas fa-plus" />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useNotesStore } from 'src/stores/notes'
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'TabsNavbar',
  props: {},
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
})
</script>
<style scoped>
.navbar-wrapper {
  height: 35px;
  background-color: #333;
  display: flex;
}

.navbar-left-sect {
  width: 250px;
  height: 100%;
}

.navbar-main {
  flex: 1 1 auto;
  height: 100%;
  padding: 0px 10px;
  gap: 3px;
  display: flex;
}

.nav-tab {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0px 8px;
  width: 180px;
  font-weight: 500;
  position: relative;
  border-radius: 5px;
  margin-bottom: 3px;
  margin-top: 7px;
  height: 25px;
}

.nav-tab .q-icon {
  opacity: 0;
}

.nav-tab:hover {
  background-color: #3d3d3d;
  cursor: pointer;
}

.nav-tab:hover .q-icon,
.nav-tab.active .q-icon {
  opacity: 1;
}

.nav-tab.active {
  background-color: #111;
  border-radius: 5px 5px 0px 0px;
  margin: 0;
  margin-top: 7px;
  height: 28px;
  padding-bottom: 3px;
}

.nav-tab.active::before {
  content: '';
  position: absolute;

  background-color: transparent;
  bottom: 0px;
  left: -10px;
  height: 20px;
  width: 10px;
  border-bottom-right-radius: 5px;
  box-shadow: 0 10px 0 0 #111;
}

.nav-tab.active::after {
  content: '';
  position: absolute;

  background-color: transparent;
  bottom: 0px;
  right: -10px;
  height: 20px;
  width: 10px;
  border-bottom-left-radius: 5px;
  box-shadow: 0 10px 0 0 #111;
}

.add-tab-wrapper {
  margin-top: 7px;
  margin-bottom: 3px;
  padding: 0px 5px;
  border-left: 2px solid #3d3d3d;
}

.add-tab-wrapper.no-line {
  border-color: transparent;
}

.add-tab-btn {
  width: 25px;
  height: 25px;
  display: flex;
  justify-content: center;
  align-items: center;
  border-radius: 5px;
  cursor: pointer;
}

.add-tab-btn:hover {
  background-color: #3d3d3d;
}
</style>
