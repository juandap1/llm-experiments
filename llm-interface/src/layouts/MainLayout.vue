<template>
  <q-layout view="lHh Lpr lFf">
    <q-header>
      <q-toolbar class="navbar">
        <div class="search-inp">
          <input type="text" placeholder="Search" />
          <span> <q-icon name="mdi-apple-keyboard-command" /> + F </span>
        </div>
      </q-toolbar>
    </q-header>

    <q-drawer class="sidebar" v-model="showSidebar" show-if-above>
      <div class="sidebar-header">
        <div class="logo">Thrive</div>
      </div>
    </q-drawer>

    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script>
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'MainLayout',

  components: {},

  setup() {
    return {}
  },
  data() {
    return {
      showSidebar: true,
    }
  },
})
</script>
<style lang="scss" scoped>
.search-inp {
  border: 1px solid var(--border-color);
  height: 34px;
  border-radius: 5px;
  width: 300px;
  display: flex;
  align-items: center;
  gap: 5px;
  font-weight: 500;
  padding: 0px 10px;
  color: #777;

  input {
    flex: 1 1 auto;
    background: transparent;
    outline: none;
    border: none;
    color: white;
  }
}
</style>
