<template>
  <div class="layout-container">
    <default-navbar />
    <div class="layout-main">
      <default-sidebar></default-sidebar>
      <div class="content-container"></div>
    </div>
  </div>
</template>

<script>
import { defineComponent } from 'vue'
// import HomeNavbar from 'src/components/TabsNavbar.vue'
import DefaultNavbar from 'src/components/Learning/DefaultNavbar.vue'
import DefaultSidebar from 'src/components/Learning/DefaultSidebar.vue'

export default defineComponent({
  name: 'QuizPage',
  components: { DefaultNavbar, DefaultSidebar },
  data() {
    return {}
  },
})
</script>
<style scoped></style>
