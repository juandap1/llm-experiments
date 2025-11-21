<template>
  <div class="navbar-wrapper">
    <div class="navbar-left-sect"></div>
    <div class="navbar-main">
      <slot></slot>
    </div>
  </div>
</template>

<script>
import { useStore } from 'src/stores/store'
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'DefaultNavbar',
  props: {},
  components: {},
  setup() {
    return {
      store: useStore(),
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
