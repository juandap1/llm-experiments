<template>
  <div class="sidenav-wrapper">
    <router-link to="/" exact>
      <div class="sidenav-btn" title="Notes">
        <img src="/awsLogo.png" />
      </div>
    </router-link>
    <router-link to="/search">
      <div class="sidenav-btn" title="Search Notes">
        <q-icon name="fas fa-search" />
      </div>
    </router-link>
    <router-link to="/topics">
      <div class="sidenav-btn" title="Topic Breakdown">
        <q-icon name="fas fa-rectangle-list" />
      </div>
    </router-link>
    <router-link to="/quiz">
      <div class="sidenav-btn" title="Quiz">
        <q-icon name="fas fa-list-check" />
      </div>
    </router-link>
    <router-link to="/flashcards">
      <div class="sidenav-btn" title="Flashcards">
        <q-icon name="fas fa-layer-group" />
      </div>
    </router-link>
    <router-link to="/analytics">
      <div class="sidenav-btn" title="Analytics">
        <q-icon name="fas fa-chart-pie" />
      </div>
    </router-link>
    <router-link to="/graph">
      <div class="sidenav-btn" title="Graph View">
        <q-icon name="fas fa-diagram-project" />
      </div>
    </router-link>
    <div class="side-filler"></div>
    <router-link to="/settings">
      <div class="sidenav-btn" title="Settings">
        <q-icon name="fas fa-cog" />
      </div>
    </router-link>
  </div>
</template>

<script>
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'SideNavbar',
  props: {},
  components: {},
  setup() {
    return {}
  },
  data() {
    return {}
  },
  methods: {},
  mounted() {},
})
</script>
<style scoped>
.sidenav-wrapper {
  height: 100vh;
  width: 60px;
  min-width: 60px;
  background-color: #333;
  display: flex;
  flex-flow: column;
  padding-top: 40px;
  padding-bottom: 20px;
  align-items: center;
  gap: 10px;
}

.sidenav-btn {
  width: 45px;
  height: 45px;
  display: flex;
  justify-content: center;
  align-items: center;
  border-radius: 7.5px;
  cursor: pointer;
  font-size: 18px;
  overflow: hidden;
  color: white;
}

.router-link-active .sidenav-btn,
.sidenav-btn:hover {
  background-color: #444;
}

.sidenav-btn img {
  width: 45px;
  height: 45px;
  object-fit: fill;
  aspect-ratio: 1 / 1;
  border-radius: 7.5px;
}

.side-filler {
  flex: 1 1 auto;
}
</style>
